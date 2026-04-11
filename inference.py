"""
Inference script - Judges will run this
Uses OpenAI API client to run agent against environment
Follows official OpenEnv format for [START], [STEP], [END]
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from client import CyberInvestigationClient
import requests
from openai import OpenAI

# ── Environment variables ────────────────────────────────────────────────────
# HF router requires a HuggingFace token as the API key.
# The model name must be a valid HF model ID served by the router,
# NOT an OpenAI model name like "gpt-4o-mini".
HF_TOKEN     = os.environ.get("HF_TOKEN", "")
API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY      = os.environ.get("API_KEY") or HF_TOKEN
MODEL_NAME   = os.environ.get("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
ENV_BASE_URL = os.environ.get("ENV_BASE_URL", "http://localhost:7860")

BENCHMARK = "cyber_investigator"
MAX_STEPS  = 10


# ── Logging helpers ──────────────────────────────────────────────────────────

def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error=None):
    error_val = error if error else "null"
    done_val  = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: list):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    success_val = str(success).lower()
    print(f"[END] success={success_val} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


# ── LLM helper ───────────────────────────────────────────────────────────────

def pick_next_log(openai_client, task_name: str, obs: dict, visited_logs: set) -> int:
    """
    Ask the LLM which log index to analyze next.
    Falls back to the first unvisited index if the LLM call fails or
    returns an unparseable / out-of-range response.
    """
    available_ids: list = obs["available_log_ids"]

    # ── deterministic fallback (used when LLM is unavailable) ──
    def fallback() -> int:
        for log_id in available_ids:
            if log_id not in visited_logs:
                return log_id
        return available_ids[0] if available_ids else 0

    if openai_client is None:
        return fallback()

    try:
        prompt = (
            f"You are analyzing system logs for security threats in task: {task_name}\n"
            f"Available log IDs: {available_ids}\n"
            f"Already analyzed: {sorted(visited_logs)}\n"
            f"Current log content: {obs.get('current_log_content', 'N/A')}\n\n"
            "Which log index should we analyze next to find suspicious activity? "
            "Reply with ONLY a single integer (e.g. 2)."
        )

        response = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=8,
        )

        raw = response.choices[0].message.content.strip()
        # Extract first run of digits
        digits = "".join(c for c in raw.split()[0] if c.isdigit()) if raw else ""
        if digits:
            candidate = int(digits)
            if candidate in available_ids:
                return candidate

    except Exception as e:
        print(f"[WARN] LLM call failed, using fallback: {e}", flush=True)

    return fallback()


# ── Task runner ───────────────────────────────────────────────────────────────

def run_task(client: CyberInvestigationClient, openai_client, task_name: str):
    """Run one task episode; return (score, steps, success, rewards)."""
    result = client.reset(task_name)
    obs    = result["observation"]

    visited_logs: set  = set()
    total_reward: float = 0.0
    steps: int          = 0
    rewards: list       = []

    for step_num in range(1, MAX_STEPS + 1):
        best_log   = pick_next_log(openai_client, task_name, obs, visited_logs)
        action_str = f"analyze_log_{best_log}"

        step_error = None
        reward     = 0.0
        done       = False

        try:
            step_result = client.step(best_log)
            obs         = step_result["observation"]
            reward      = step_result["reward"]
            done        = step_result["done"]
        except Exception as e:
            step_error = str(e)
            done       = True

        visited_logs.add(best_log)
        total_reward += reward
        steps  = step_num
        rewards.append(reward)

        log_step(step=step_num, action=action_str, reward=reward, done=done, error=step_error)

        if done:
            break

    # Normalise score to [0, 1]
    if task_name == "task1":
        score = min(1.0, max(0.0, total_reward + 0.5))
    elif task_name == "task2":
        score = min(1.0, max(0.0, total_reward + 0.3))
    else:   # task3
        score = min(1.0, max(0.0, total_reward + 0.1))

    success = score > 0.0
    return score, steps, success, rewards


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    # 1. Check whether the environment server is reachable
    try:
        requests.get(f"{ENV_BASE_URL}/health", timeout=5)
    except Exception:
        print(f"[ERROR] Environment not reachable at {ENV_BASE_URL}", flush=True, file=sys.stderr)
        log_start(task="task1", env=BENCHMARK, model=MODEL_NAME)
        log_end(success=False, steps=0, score=0.0, rewards=[])
        return

    # 2. Build OpenAI client pointing at the HF router
    openai_client = None
    if API_KEY:
        try:
            openai_client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
            print(f"[INFO] Using model: {MODEL_NAME} via {API_BASE_URL}", flush=True)
        except Exception as e:
            print(f"[WARN] Could not create OpenAI client ({e}); will use fallback heuristic.", flush=True)
    else:
        print("[WARN] No HF_TOKEN / API_KEY set — running with deterministic fallback.", flush=True)

    client     = CyberInvestigationClient(base_url=ENV_BASE_URL)
    all_scores = []

    for task_name in ["task1", "task2", "task3"]:
        log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)
        try:
            score, steps, success, rewards = run_task(client, openai_client, task_name)
            all_scores.append(score)
            log_end(success=success, steps=steps, score=score, rewards=rewards)
        except Exception as e:
            print(f"[ERROR] Task {task_name} crashed: {e}", flush=True, file=sys.stderr)
            log_step(step=1, action="error", reward=0.0, done=True, error=str(e))
            log_end(success=False, steps=0, score=0.0, rewards=[])
            all_scores.append(0.0)

    final_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
    print(f"[DEBUG] Final average score: {final_score:.3f}", flush=True)


if __name__ == "__main__":
    main()
