from fastapi import FastAPI
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import LogAnalysisAction
from server.environment import env

app = FastAPI(title="Cyber Investigation Environment")

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/reset")
async def reset(task_name: str = "task1"):
    obs = env.reset(task_name)
    return {
        "observation": json.loads(obs.model_dump_json()),
        "done": False
    }

@app.post("/step")
async def step(action: LogAnalysisAction):
    obs, reward, done, info = env.step(action)
    return {
        "observation": json.loads(obs.model_dump_json()),
        "reward": float(reward),
        "done": done,
        "info": info
    }

@app.get("/state")
async def get_state():
    state = env.state
    return json.loads(state.model_dump_json())
