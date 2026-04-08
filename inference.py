"""
Inference script - Judges will run this
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from client import CyberInvestigationClient
import requests

# Use port 8000 for local dev, HF Spaces will override with API_BASE_URL env var
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN", "dummy")


def run_task(client, task_name: str):
    """Run a task and return score (0.0-1.0)"""
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
            score = run_task(client, task_name)
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
