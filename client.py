import requests
import json
from models import LogAnalysisAction

class CyberInvestigationClient:
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url

    def reset(self, task_name: str = "task1"):
        response = requests.post(f"{self.base_url}/reset", params={"task_name": task_name})
        response.raise_for_status()
        return response.json()

    def step(self, log_entry_id: int):
        action = LogAnalysisAction(log_entry_id=log_entry_id)
        response = requests.post(
            f"{self.base_url}/step",
            json=json.loads(action.model_dump_json())
        )
        response.raise_for_status()
        return response.json()

    def state(self):
        response = requests.get(f"{self.base_url}/state")
        response.raise_for_status()
        return response.json()
