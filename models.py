from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class LogAnalysisAction(BaseModel):
    """Agent action: which log to analyze"""
    log_entry_id: int

class LogAnalysisObservation(BaseModel):
    """What agent observes"""
    current_log_id: int
    current_log_content: str
    available_log_ids: List[int]
    suspicious_score: float
    context: Dict[str, Any] = {}

class LogAnalysisState(BaseModel):
    """Episode state"""
    episode_id: Optional[str] = None
    step_count: int = 0
    path_followed: List[int] = []
    task_name: str = ""
    game_phase: str = "investigating"
    observation: LogAnalysisObservation


class LogAnalysisState(BaseModel):
    """Episode state metadata"""
    episode_id: Optional[str] = None
    step_count: int = 0
    path_followed: List[int] = []
    task_name: Optional[str] = None
    game_phase: str = "investigating"
    current_log_id: int = 0


# ============================================================================
# TASK DEFINITIONS
# ============================================================================

class TaskDef:
    """Task definition"""
    
    def __init__(self, name: str, description: str, difficulty: str, logs: List[Dict], target_seq: List[int]):
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.logs = logs
        self.target_sequence = target_seq


def create_task_1() -> TaskDef:
    """Suspicious Login Detection - EASY"""
    return TaskDef(
        name="Suspicious Login Detection",
        description="Detect an unusual login from an unexpected location",
        difficulty="easy",
        logs=[
            {"id": 0, "timestamp": "2024-04-08 08:00:00", "type": "AUTH", 
             "content": "User john_doe logged in from 192.168.1.50 (Office network)", "suspicious": False, "severity": 0.1},
            {"id": 1, "timestamp": "2024-04-08 14:32:15", "type": "AUTH", 
             "content": "User john_doe logged in from 203.45.67.89 (Unknown international location)", "suspicious": True, "severity": 0.9},
            {"id": 2, "timestamp": "2024-04-08 15:00:00", "type": "FILE", 
             "content": "john_doe accessed /etc/passwd from 203.45.67.89", "suspicious": True, "severity": 0.7},
            {"id": 3, "timestamp": "2024-04-08 09:15:00", "type": "AUTH", 
             "content": "User sarah_smith logged in from 192.168.1.51 (Office network)", "suspicious": False, "severity": 0.1},
            {"id": 4, "timestamp": "2024-04-08 16:00:00", "type": "FILE", 
             "content": "System backup completed successfully", "suspicious": False, "severity": 0.0}
        ],
        target_seq=[1]
    )


def create_task_2() -> TaskDef:
    """Lateral Movement Detection - MEDIUM"""
    return TaskDef(
        name="Lateral Movement Detection",
        description="Trace attacker movement across multiple systems",
        difficulty="medium",
        logs=[
            {"id": 0, "timestamp": "2024-04-08 10:00:00", "type": "AUTH", 
             "content": "Initial compromise: User admin logged in from 10.0.0.5", "suspicious": True, "severity": 0.8},
            {"id": 1, "timestamp": "2024-04-08 10:15:00", "type": "NETWORK", 
             "content": "10.0.0.5 scanned ports on host 10.0.0.10", "suspicious": True, "severity": 0.7},
            {"id": 2, "timestamp": "2024-04-08 10:25:00", "type": "AUTH", 
             "content": "User postgres login attempt on 10.0.0.10 from 10.0.0.5 - SUCCESS", "suspicious": True, "severity": 0.9},
            {"id": 3, "timestamp": "2024-04-08 10:30:00", "type": "FILE", 
             "content": "File /var/www/html/app.py modified from 10.0.0.10", "suspicious": True, "severity": 0.8},
            {"id": 4, "timestamp": "2024-04-08 11:00:00", "type": "AUTH", 
             "content": "User john_doe logged in from 192.168.1.50 (legitimate)", "suspicious": False, "severity": 0.1},
            {"id": 5, "timestamp": "2024-04-08 09:00:00", "type": "FILE", 
             "content": "Nightly backup started", "suspicious": False, "severity": 0.0}
        ],
        target_seq=[0, 1, 2, 3]
    )


def create_task_3() -> TaskDef:
    """Privilege Escalation & Full Attack Chain - HARD"""
    return TaskDef(
        name="Privilege Escalation Attack Chain",
        description="Detect the complete attack pattern from initial access to full compromise",
        difficulty="hard",
        logs=[
            {"id": 0, "timestamp": "2024-04-08 08:30:00", "type": "AUTH", 
             "content": "Weak password attack: user guest successful login from 203.100.200.50", "suspicious": True, "severity": 0.7},
            {"id": 1, "timestamp": "2024-04-08 08:45:00", "type": "PROCESS", 
             "content": "Suspicious process 'exploit.sh' started by guest user", "suspicious": True, "severity": 0.8},
            {"id": 2, "timestamp": "2024-04-08 09:00:00", "type": "AUTH", 
             "content": "Privilege escalation attempt: guest -> root via sudo vulnerability", "suspicious": True, "severity": 0.95},
            {"id": 3, "timestamp": "2024-04-08 09:10:00", "type": "FILE", 
             "content": "Root user created new admin account 'backdoor' with shell access", "suspicious": True, "severity": 0.99},
            {"id": 4, "timestamp": "2024-04-08 09:20:00", "type": "NETWORK", 
             "content": "Backdoor account connected from 203.100.200.50 - C2 communication established", "suspicious": True, "severity": 0.95},
            {"id": 5, "timestamp": "2024-04-08 07:00:00", "type": "FILE", 
             "content": "Regular system health check completed", "suspicious": False, "severity": 0.0},
            {"id": 6, "timestamp": "2024-04-08 10:00:00", "type": "AUTH", 
             "content": "Normal user john_doe logged in from office", "suspicious": False, "severity": 0.1}
        ],
        target_seq=[0, 1, 2, 3, 4]
    )


# ============================================================================
# TASK REGISTRY
# ============================================================================

TASKS = {
    "login_detection": create_task_1(),
    "lateral_movement": create_task_2(),
    "privilege_escalation": create_task_3()
}

TASK_ORDER = ["login_detection", "lateral_movement", "privilege_escalation"]
