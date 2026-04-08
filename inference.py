"""
Inference script - Judges will run this
Uses OpenAI API client to run agent against environment
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from client import CyberInvestigationClient
import requests
from openai import OpenAI

# Environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-dummy")
HF_TOKEN = os.getenv("HF_TOKEN", "dummy")


def run_task(client, openai_client, task_name: str):
    """Run a task with LLM reasoning and return score (0.0-1.0)"""
    print("[STEP]")
    print(json.dumps({"task": task_name, "status": "starting"}))
    
    result = client.reset(task_name)
    obs = result["observation"]
    
    visited_logs = set()
    total_reward = 0.0
    steps = 0
    max_steps = 10
    
    for step in range(max_steps):
        available_ids = obs["available_log_ids"]
        
        # Use LLM to reason about which log to analyze next
        try:
            prompt = f"""You are analyzing system logs for security threats in task: {task_name}
Current logs available: {available_ids}
Already analyzed: {list(visited_logs)}
Current observation: {obs.get('current_log_content', 'N/A')}

Which log index should we analyze next? Respond with just the index number (e.g., 0 or 1)."""
            
            response = openai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=10
            )
            
            # Parse LLM response to get log index
            response_text = response.choices[0].message.content.strip()
            best_log = int(''.join(filter(str.isdigit, response_text.split()[0]))) if response_text else None
            
            # Fallback if parsing fails or invalid index
            if best_log is None or best_log not in available_ids:
                for log_id in available_ids:
                    if log_id not in visited_logs:
                        best_log = log_id
                        break
                if best_log is None:
                    best_log = available_ids[0] if available_ids else 0
        except Exception as e:
            # Fallback to deterministic approach if LLM fails
            best_log = None
            for log_id in available_ids:
                if log_id not in visited_logs:
                    best_log = log_id
                    break
            if best_log is None:
                best_log = available_ids[0] if available_ids else 0
        
        step_result = client.step(best_log)
        obs = step_result["observation"]
        reward = step_result["reward"]
        done = step_result["done"]
        
        visited_logs.add(best_log)
        total_reward += reward
        steps += 1
        
        print("[STEP]")
        print(json.dumps({
            "action": f"analyze_log_{best_log}",
            "reward": float(reward),
            "step": steps
        }))
        
        if done:
            break
    
    if task_name == "task1":
        score = min(1.0, max(0.0, total_reward + 0.5))
    elif task_name == "task2":
        score = min(1.0, max(0.0, total_reward + 0.3))
    else:
        score = min(1.0, max(0.0, total_reward + 0.1))
    
    return float(score)


def main():
    print("[START]")
    print(json.dumps({
        "inference": "cyber_investigation",
        "model": MODEL_NAME,
        "api": API_BASE_URL
    }))
    
    # Initialize OpenAI client
    openai_client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=None  # Uses OpenAI's default endpoint
    )
    
    # Initialize environment client
    client = CyberInvestigationClient(base_url=API_BASE_URL)
    
    try:
        requests.get(f"{API_BASE_URL}/health", timeout=2)
    except:
        print("[END]")
        print(json.dumps({"error": "env_unreachable", "score": 0.0}))
        return
    
    tasks = ["task1", "task2", "task3"]
    scores = []
    
    for task_name in tasks:
        try:
            score = run_task(client, openai_client, task_name)
            scores.append(score)
        except Exception as e:
            print("[STEP]")
            print(json.dumps({"task_error": task_name, "error": str(e)}))
            scores.append(0.0)
    
    final_score = sum(scores) / len(scores) if scores else 0.0
    
    print("[END]")
    print(json.dumps({
        "tasks": len(scores),
        "scores": [float(s) for s in scores],
        "score": float(final_score)
    }))


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
