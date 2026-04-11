"""
Cyber Investigation Environment - Core logic
"""
from typing import Tuple, Optional, List, Dict, Any
import sys
import random
from pathlib import Path

# Robust path insertion so models.py is always found
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import LogAnalysisObservation, LogAnalysisAction, LogAnalysisState

# Task data
TASK1_LOGS = [
    "Normal login from 192.168.1.1 at 9:00 AM",
    "Normal login from 192.168.1.2 at 9:15 AM",
    "SUSPICIOUS: Login from 41.203.45.67 at 2:30 AM - unusual location",
    "Normal logout at 5:00 PM",
]

TASK2_LOGS = [
    "User john_doe login from 192.168.1.50",
    "SSH connection to server_A from 192.168.1.50",
    "SSH connection to server_B from 192.168.1.51 (lateral movement)",
    "SSH connection to server_C from 192.168.1.52 (lateral movement)",
    "Normal file access on server_C",
]

TASK3_LOGS = [
    "Failed login attempt for user admin",
    "Failed login attempt for user admin",
    "Successful login as user admin (exploit)",
    "Sudo command executed to gain root",
    "Backdoor installed at /tmp/backdoor.sh",
    "Outbound connection to C2 server 203.45.67.89:4444",
    "Data exfiltration in progress",
]

class CyberInvestigationEnvironment:
    def __init__(self, custom_logs: Optional[Dict[str, List[str]]] = None, custom_indices: Optional[Dict[str, List[int]]] = None) -> None:
        self.current_task: Optional[str] = None
        self.current_logs: Optional[List[str]] = None
        self.current_log_id: int = 0
        self.visited_logs: set = set()
        self.step_count: int = 0
        self.max_steps: int = 10

        # Use custom logs if provided, otherwise use defaults
        if custom_logs:
            task1_logs = custom_logs.get("task1", TASK1_LOGS)
            task2_logs = custom_logs.get("task2", TASK2_LOGS)
            task3_logs = custom_logs.get("task3", TASK3_LOGS)
        else:
            task1_logs = TASK1_LOGS
            task2_logs = TASK2_LOGS
            task3_logs = TASK3_LOGS

        # Use custom correct indices if provided, otherwise use defaults
        if custom_indices:
            task1_indices = custom_indices.get("task1", [2])
            task2_indices = custom_indices.get("task2", [1, 2, 3])
            task3_indices = custom_indices.get("task3", [0, 1, 2, 3, 4, 5, 6])
        else:
            task1_indices = [2]
            task2_indices = [1, 2, 3]
            task3_indices = [0, 1, 2, 3, 4, 5, 6]

        self.tasks: Dict[str, Dict[str, Any]] = {
            "task1": {
                "logs": task1_logs,
                "correct_indices": task1_indices,
                "description": "suspicious_login_detection"
            },
            "task2": {
                "logs": task2_logs,
                "correct_indices": task2_indices,
                "description": "lateral_movement_detection"
            },
            "task3": {
                "logs": task3_logs,
                "correct_indices": task3_indices,
                "description": "privilege_escalation_chain"
            }
        }

    def reset(self, task_name: str = "task1") -> LogAnalysisObservation:
        self.current_task = task_name
        task_info = self.tasks[task_name]
        logs: List[str] = task_info["logs"]
        self.current_logs = logs
        self.current_log_id = 0
        self.visited_logs = set()
        self.step_count = 0

        return LogAnalysisObservation(
            current_log_id=self.current_log_id,
            current_log_content=logs[self.current_log_id],
            available_log_ids=list(range(len(logs))),
            suspicious_score=0.0,
            context={"task": task_name, "total_logs": len(logs)}
        )

    def step(self, action: LogAnalysisAction) -> Tuple[LogAnalysisObservation, float, bool, dict]:
        self.step_count += 1
        log_id = action.log_entry_id

        assert self.current_logs is not None, "Reset must be called before step()"
        assert self.current_task is not None, "Reset must be called before step()"

        if log_id < 0 or log_id >= len(self.current_logs):
            reward = -0.1
            done = self.step_count >= self.max_steps
            return self._get_observation(0), reward, done, {}

        reward = self._calculate_reward(log_id)
        self.current_log_id = log_id
        self.visited_logs.add(log_id)

        task_info = self.tasks[self.current_task]
        all_correct_found = all(idx in self.visited_logs for idx in task_info["correct_indices"])
        done = all_correct_found or self.step_count >= self.max_steps

        obs = self._get_observation(log_id)

        return obs, reward, done, {"task": self.current_task}

    def _calculate_reward(self, log_id: int) -> float:
        assert self.current_task is not None, "Reset must be called before _calculate_reward()"

        task_info = self.tasks[self.current_task]
        correct_indices = task_info["correct_indices"]

        noise = random.uniform(-0.05, 0.05)

        if log_id in self.visited_logs:
            return -0.2 + noise

        if log_id in correct_indices:
            if len(self.visited_logs) == 0:
                return 0.5 + noise
            return 0.3 + noise

        return -0.1 + noise

    def _get_observation(self, log_id: int) -> LogAnalysisObservation:
        assert self.current_logs is not None, "Reset must be called before _get_observation()"
        assert self.current_task is not None, "Reset must be called before _get_observation()"

        task_info = self.tasks[self.current_task]
        correct_indices = task_info["correct_indices"]

        suspicious_score = 1.0 if log_id in correct_indices else 0.2

        return LogAnalysisObservation(
            current_log_id=log_id,
            current_log_content=self.current_logs[log_id],
            available_log_ids=list(range(len(self.current_logs))),
            suspicious_score=suspicious_score,
            context={
                "task": self.current_task,
                "step": self.step_count,
                "visited": list(self.visited_logs)
            }
        )

    @property
    def state(self) -> LogAnalysisState:
        return LogAnalysisState(
            episode_id=self.current_task or "unknown",
            step_count=self.step_count,
            path_followed=list(self.visited_logs),
            task_name=self.current_task or "unknown",
            game_phase="investigating"
        )

env = CyberInvestigationEnvironment()
