from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import LogAnalysisAction
from server.environment import env

app = FastAPI(title="Cyber Investigation Environment")

class ResetRequest(BaseModel):
    task_name: str = "task1"

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/reset")
async def reset(request: Optional[ResetRequest] = None, task_name: str = "task1"):
    # Accept task_name from JSON body OR query param
    name = (request.task_name if request else None) or task_name
    obs = env.reset(name)
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


def main():
    """Run the FastAPI server"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
