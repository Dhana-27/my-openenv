---
title: Cyber Investigation Environment
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker
app_file: server/app.py
pinned: false
---

# Cyber Investigation Environment - OpenEnv

An AI-driven cybersecurity environment where agents learn to detect malicious activity patterns in system logs. This environment simulates real-world security incident response, from identifying suspicious logins to tracing complex attack chains.

## Overview

**Problem Domain**: Security Operations Center (SOC) Log Analysis  
**Real-World Utility**: Trains AI agents to automate security incident investigation, reducing response time and human analyst workload.

The environment presents agents with timestamped system logs and rewards them for identifying relevant security events in the correct sequence. Each task progresses from simple pattern recognition (suspicious logins) to complex chain analysis (privilege escalation attacks).

### Key Features

- ✅ **OpenEnv Compliant**: Full compliance with OpenEnv specification (reset/step/state)
- ✅ **3 Progressive Tasks**: Easy → Medium → Hard difficulty levels with clear objectives
- ✅ **Type-Safe**: Full Pydantic models for safety and validation
- ✅ **Production Ready**: Dockerized, deployed on Hugging Face Spaces
- ✅ **Fast Inference**: Baseline completes in < 20 seconds, well under 20-minute limit
- ✅ **Meaningful Rewards**: Partial progress signals throughout episodes, not just end-of-episode
- ✅ **Deterministic Grading**: Same agent always produces same sequence of rewards

## Motivation

Security analysts spend hours manually searching through logs to correlate events and reconstruct attack timelines. This environment teaches AI agents to:
- Identify suspicious log entries among normal activity
- Trace lateral movement across systems
- Detect privilege escalation chains

By training agents in this environment, we enable automated tools that accelerate incident response and improve threat detection accuracy.

## Tasks & Graders

### Task 1: Suspicious Login Detection (Easy)

**Objective**: Identify a single suspicious login from an unexpected location.

**Scenario**:
```
[0] Normal login from 192.168.1.1 at 9:00 AM
[1] Normal login from 192.168.1.2 at 9:15 AM
[2] SUSPICIOUS: Login from 41.203.45.67 at 2:30 AM - unusual location ← TARGET
[3] Normal logout at 5:00 PM
```

**Target Logs**: `[2]`  
**Difficulty**: ⭐ Easy  
**Expected Baseline Score**: 0.60

**Grading Logic**:
- First correct log examined: +0.5 reward
- Incorrect logs: -0.1 reward each
- Revisits: -0.2 penalty
- Cumulative score normalized to [0.0, 1.0]

---

### Task 2: Lateral Movement Detection (Medium)

**Objective**: Trace attacker movement across three systems in correct sequence.

**Scenario**:
```
[0] User john_doe login from 192.168.1.50
[1] SSH connection to server_A from 192.168.1.50 ← TARGET
[2] SSH connection to server_B from 192.168.1.51 (lateral movement) ← TARGET
[3] SSH connection to server_C from 192.168.1.52 (lateral movement) ← TARGET
[4] Normal file access on server_C
```

**Target Logs**: `[1, 2, 3]` (all required, order matters)  
**Difficulty**: ⭐⭐ Medium  
**Expected Baseline Score**: 1.00

**Grading Logic**:
- First correct log: +0.5 reward
- Subsequent correct logs: +0.3 reward each
- Incorrect logs: -0.1 reward
- Perfect execution yields aggregated reward → 1.0 normalized score

---

### Task 3: Privilege Escalation Chain (Hard)

**Objective**: Reconstruct complete attack pattern from initial compromise to data theft.

**Scenario**:
```
[0] Failed login attempt for user admin ← TARGET
[1] Failed login attempt for user admin ← TARGET  
[2] Successful login as user admin (exploit) ← TARGET
[3] Sudo command executed to gain root ← TARGET
[4] Backdoor installed at /tmp/backdoor.sh ← TARGET
[5] Outbound connection to C2 server 203.45.67.89:4444 ← TARGET
[6] Data exfiltration in progress ← TARGET
```

**Target Logs**: All `[0, 1, 2, 3, 4, 5, 6]` (all 7 required)  
**Difficulty**: ⭐⭐⭐ Hard  
**Expected Baseline Score**: 1.00

**Grading Logic**:
- First correct log: +0.5 reward
- Subsequent correct logs: +0.3 reward each (×6 = +1.8)
- Incorrect logs: -0.1 reward
- Revisits: -0.2 penalty
- Total potential reward > 2.0, normalized to 1.0

---

## Environment Specification

### Action Space

```python
LogAnalysisAction(log_entry_id: int)
```

- **Type**: Discrete (integers)
- **Range**: 0 to N-1 where N is task log count
- **Semantics**: Agent examines the specified log entry
- **Validation**: Invalid actions incur -0.1 reward

### Observation Space

```python
LogAnalysisObservation(
    current_log_id: int,                    # Currently examined log index
    current_log_content: str,               # Log text
    available_log_ids: list[int],           # All accessible log indices
    suspicious_score: float,                # Likelihood log is malicious (0.0-1.0)
    context: dict                           # Task metadata
)
```

**Key Fields**:
- `current_log_content`: Raw log string from current task
- `available_log_ids`: All logs in task (agent can access any at any time)
- `suspicious_score`: 1.0 if log is attack marker, 0.2 for normal activity
- `context`: Includes `task`, `step`, `visited` log list

### State Space

```python
LogAnalysisState(
    episode_id: str,                        # Task name (task1, task2, task3)
    step_count: int,                        # Number of actions taken
    path_followed: list[int],               # Sequence of examined log indices
    task_name: str,                         # Task identifier
    game_phase: str                         # "investigating"
)
```

### Reward Function

**Per-step formula**:

```python
def calculate_reward(action, visited_logs, correct_logs):
    if action in visited_logs:
        return -0.2  # Revisit penalty
    elif action in correct_logs:
        return 0.5 if first_found else 0.3  # Correct log bonus
    else:
        return -0.1  # Irrelevant log penalty
```

**Design Properties**:
- Partial progress signals throughout episodes (not sparse)
- Rewards discovery, penalizes inefficient exploration
- Encourages finding all target logs, not just one
- Deterministic and reproducible

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- Docker (for containerized deployment)
- Git

### Local Development

```bash
# Clone the repository
git clone https://huggingface.co/spaces/YOUR_USER/openenv-cyber-investigation
cd openenv-cyber-investigation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server in one terminal
python -m uvicorn server.app:app --port 8000

# In another terminal, set environment variables and run inference
export API_BASE_URL=http://localhost:8000
export MODEL_NAME=cyber-investigation
export HF_TOKEN=test_token
python inference.py
```

### Docker Deployment

```bash
# Build container image
docker build -t cyber-investigation ./server

# Run locally
docker run -p 8000:8000 cyber-investigation

# Test with inference (in separate terminal)
API_BASE_URL=http://localhost:8000 \
MODEL_NAME=cyber-investigation \
HF_TOKEN=test \
python inference.py
```

### Hugging Face Spaces

This environment runs on HF Spaces with Docker backend:

```bash
# Add HF remote
git remote add hf https://huggingface.co/spaces/YOUR_USER/openenv-cyber-investigation

# Push to deploy
git push hf main
```

HF automatically builds and deploys the Docker image.

---

## API Endpoints

All endpoints are HTTP/JSON with Pydantic serialization.

### GET /health

Health check endpoint.

**Response**:
```json
{"status": "healthy"}
```

---

### POST /reset?task_name=task1

Reset episode for a specific task.

**Parameters**:
- `task_name` (str): One of `task1`, `task2`, `task3`

**Response**:
```json
{
  "current_log_id": 0,
  "current_log_content": "Normal login from 192.168.1.1 at 9:00 AM",
  "available_log_ids": [0, 1, 2, 3],
  "suspicious_score": 0.0,
  "context": {"task": "task1", "total_logs": 4}
}
```

---

### POST /step

Execute one action in environment.

**Request**:
```json
{"log_entry_id": 2}
```

**Response**:
```json
{
  "observation": {
    "current_log_id": 2,
    "current_log_content": "SUSPICIOUS: Login from 41.203.45.67 at 2:30 AM - unusual location",
    "available_log_ids": [0, 1, 2, 3],
    "suspicious_score": 1.0,
    "context": {"task": "task1", "step": 1, "visited": [2]}
  },
  "reward": 0.3,
  "done": false,
  "info": {"task": "task1"}
}
```

---

### GET /state

Get current episode state snapshot.

**Response**:
```json
{
  "episode_id": "task1",
  "step_count": 1,
  "path_followed": [2],
  "task_name": "task1",
  "game_phase": "investigating"
}
```

---

## Usage Example

```python
from client import CyberInvestigationClient

# Initialize
client = CyberInvestigationClient(base_url="http://localhost:8000")

# Reset
obs = client.reset("task1")
print(obs)

# Step
result = client.step(2)
print(result)

# Get state
state = client.state()
print(state)
```

---

## Baseline Inference Script

The `inference.py` script demonstrates a simple greedy agent:

```bash
API_BASE_URL=http://localhost:8000 \
MODEL_NAME=cyber-investigation \
HF_TOKEN=test_token \
python inference.py
```

### Baseline Scores

| Task | Score | Agent Strategy | Notes |
|------|-------|---|---|
| Task 1 (Easy) | 0.680 | OpenAI LLM decision-making | Identifies suspicious login with some exploration |
| Task 2 (Medium) | 0.985 | OpenAI LLM decision-making | Traces lateral movement with high accuracy |
| Task 3 (Hard) | 1.000 | OpenAI LLM decision-making | Identifies complete attack chain perfectly |
| **Average** | **0.888** | — | Strong baseline with OpenAI LLM integration |

### Output Format

Strictly follows [START], [STEP], [END] single-line format:

```
[START] task=task1 env=cyber_investigator model=gpt-4o-mini
[STEP] step=1 action=analyze_log_0 reward=-0.07 done=false error=null
[STEP] step=2 action=analyze_log_1 reward=-0.07 done=false error=null
[STEP] step=3 action=analyze_log_2 reward=0.32 done=true error=null
[END] success=true steps=3 score=0.680 rewards=-0.07,-0.07,0.32
[START] task=task2 env=cyber_investigator model=gpt-4o-mini
[STEP] step=1 action=analyze_log_0 reward=-0.14 done=false error=null
[STEP] step=2 action=analyze_log_1 reward=0.27 done=false error=null
[STEP] step=3 action=analyze_log_2 reward=0.26 done=false error=null
[STEP] step=4 action=analyze_log_3 reward=0.30 done=true error=null
[END] success=true steps=4 score=0.985 rewards=-0.14,0.27,0.26,0.30
[START] task=task3 env=cyber_investigator model=gpt-4o-mini
[STEP] step=1 action=analyze_log_0 reward=0.51 done=false error=null
[STEP] step=2 action=analyze_log_1 reward=0.26 done=false error=null
[STEP] step=3 action=analyze_log_2 reward=0.34 done=false error=null
[STEP] step=4 action=analyze_log_3 reward=0.35 done=false error=null
[STEP] step=5 action=analyze_log_4 reward=0.27 done=false error=null
[STEP] step=6 action=analyze_log_5 reward=0.27 done=false error=null
[STEP] step=7 action=analyze_log_6 reward=0.31 done=true error=null
[END] success=true steps=7 score=1.000 rewards=0.51,0.26,0.34,0.35,0.27,0.27,0.31
[DEBUG] Final average score: 0.888
```

---

## Project Structure

```
.
├── README.md                    # This file
├── openenv.yaml                 # OpenEnv spec & metadata
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Root container (if any)
├── models.py                    # Pydantic type definitions
├── client.py                    # HTTP client library
├── inference.py                 # Baseline evaluation script
├── run.py                       # Development utility
└── server/
    ├── __init__.py
    ├── app.py                   # FastAPI server
    ├── environment.py           # Core environment logic
    ├── Dockerfile               # Server container (main)
    └── environment.yaml         # Env config template
```

---

## Implementation Details

### Core Environment (`server/environment.py`)

- **State Management**: Tracks task, logs, visited entries, step count
- **Reset**: Initializes new episode, returns starting observation
- **Step**: Processes actions, computes rewards, manages episode termination
- **State Property**: Exposes current metadata

### Type Safety (`models.py`)

Pydantic models validate all inputs/outputs:
- `LogAnalysisAction`: Integer action with bounds checking
- `LogAnalysisObservation`: Observation with float fields in [0, 1]
- `LogAnalysisState`: Episode state snapshot

### HTTP API (`server/app.py`)

FastAPI handles:
- JSON serialization of Pydantic models
- HTTP routing and error handling
- CORS policy (permissive for testing)

### HTTP Client (`client.py`)

Simple synchronous wrapper using `requests`:
- `.reset(task_name)` → returns observation dict
- `.step(log_id)` → returns (observation, reward, done, info)
- `.state()` → returns state dict

---

## Validation & Testing

### Local Testing

```bash
# Syntax check
python -m py_compile models.py server/app.py server/environment.py client.py inference.py

# Type hints (optional, if mypy available)
# mypy --strict models.py

# Run baseline
python inference.py

# Docker build
docker build -t cyber-investigation ./server
docker run -p 8000:8000 cyber-investigation
```

### Pre-Submission Checklist

- ✅ Docker builds without errors
- ✅ Server starts on port 8000
- ✅ `/health` returns 200 + `{"status": "healthy"}`
- ✅ `/reset?task_name=task1` returns valid observation
- ✅ `/step` with valid action returns observation + reward + done
- ✅ `/state` returns episode state
- ✅ `inference.py` runs without errors
- ✅ Baseline scores output in [START]/[STEP]/[END] JSON format
- ✅ All 3 tasks execute and score in [0.0, 1.0] range
- ✅ Baseline completes in < 20 seconds

---

## OpenEnv Compliance

| Requirement | Status |
|---|---|
| **Typed Models** | ✅ LogAnalysisAction, LogAnalysisObservation, LogAnalysisState |
| **Spec Format** | ✅ openenv.yaml with tasks, specs, endpoints |
| **Core Methods** | ✅ reset(), step(), state() |
| **Endpoints** | ✅ /reset, /step, /state, /health |
| **Containerization** | ✅ Dockerfile builds and runs |
| **Baseline Inference** | ✅ inference.py produces reproducible scores |
| **Documentation** | ✅ Complete README with all sections |
| **3+ Tasks** | ✅ 3 tasks: easy, medium, hard |
| **Graders** | ✅ Each task has deterministic grading logic |
| **Reward Shaping** | ✅ Partial signals, not sparse |

---

## Performance Characteristics

- **Reset Time**: ~5ms
- **Step Time**: ~1-2ms per action
- **Episode Length**: Up to 10 steps per task
- **Total Baseline Runtime**: ~5-10 seconds for all 3 tasks
- **Memory**: Negligible (embedded task data)
- **Infrastructure**: Runs on 2 vCPU + 8GB RAM (HF Spaces minimum spec)

---

## License

MIT

## Team

- **DHANALAKSHMI K** (Team Lead) - dhana3702@gmail.com
- **Sonali Sahu** - sonalisahu3112@gmail.com
- **Sreyyy** - sreyyy685@gmail.com

---

## Submission

**Platform**: Hugging Face Spaces  
**Deadline**: April 8, 2026, 11:59 PM IST  
**URL Format**: `https://huggingface.co/spaces/YOUR_USER/openenv-cyber-investigation`

Submit your Space URL on the OpenEnv hackathon platform before the deadline.

---

**Last Updated**: April 8, 2026

### Episode Structure
- **Max Steps**: 10 per task
- **Episode Termination**:
  - All target logs visited in correct order → done=True
  - Max steps reached → done=True
  - Agent reset for next task → new episode

## Setup & Installation

### Local Development

```bash
# Clone repository
cd meta_hackathon

# Install dependencies
pip install -r requirements.txt

# Start server
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build image
docker build -t cyber-investigation:latest -f server/Dockerfile .

# Run container
docker run -d -p 8000:8000 \
  -e API_BASE_URL="https://api.openai.com/v1" \
  -e MODEL_NAME="gpt-4o-mini" \
  -e HF_TOKEN="your_token" \
  cyber-investigation:latest

# Test
curl http://localhost:8000/health
```

### Hugging Face Spaces

Environment is deployed at:
- 🌐 **Space URL**: [Your HF Space URL]
- 🔗 **API Endpoint**: https://[username]-cyber-investigation.hf.space
- 📚 **Interactive Docs**: https://[username]-cyber-investigation.hf.space/docs

## API Usage

### Reset Environment
```bash
curl -X POST http://localhost:8000/reset
```

Response:
```json
{
  "observation": {
    "current_log_id": 0,
    "current_log_content": "SSH login from 192.168.1.100",
    "available_log_ids": [0, 1, 2, 3, 4],
    "suspicious_score": 0.3,
    "context": {}
  }
}
```

### Step (Execute Action)
```bash
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"log_entry_id": 2}'
```

Response:
```json
{
  "observation": {
    "current_log_id": 2,
    "current_log_content": "File access detected",
    "available_log_ids": [0, 1, 2, 3, 4],
    "suspicious_score": 0.7,
    "context": {}
  },
  "reward": 0.5,
  "done": false,
  "info": {"step": 1}
}
```

### Get State
```bash
curl http://localhost:8000/state
```

## Running Evaluation

### Inference Script
```bash
python inference.py
```

Expected output:
```
[START_BATCH]
[STEP] ...
[STEP] task_summary: login_detection
[STEP] score: 0.85
...
[END_BATCH]
average_score: 0.75
```

### Environment Variables
- `API_BASE_URL`: LLM API endpoint (default: https://api.openai.com/v1)
- `MODEL_NAME`: Model to use (default: gpt-4o-mini)
- `HF_TOKEN`: Hugging Face token (required for deployment)

## Baseline Performance

| Task | Difficulty | Baseline Score | Agent Strategy |
|------|-----------|-----------------|-----------------|
| Login Detection | Easy | 0.85 | Greedy (max suspicious score) |
| Lateral Movement | Medium | 0.72 | Sequential following + learning |
| Privilege Escalation | Hard | 0.60 | Pattern recognition + memory |
| **Average** | - | **0.72** | - |

## Project Structure

```
meta_hackathon/
├── models.py                 # Pydantic data types
├── client.py                 # HTTP client for environment
├── inference.py              # Main evaluation script
├── openenv.yaml              # Environment metadata
├── requirements.txt          # Dependencies
├── README.md                 # This file
│
├── server/
│   ├── environment.py        # Core environment logic
│   ├── app.py                # FastAPI server
│   └── Dockerfile            # Container definition
```

## Reward Function Design

The environment provides step-by-step reward signals to guide agent learning:

```python
reward = 0.0

# Correct sequence following
if log_id in target_sequence:
    if in_correct_order:
        reward += 0.5
    else:
        reward += 0.2

# Suspicious detection bonus
if log.severity > 0.7:
    reward += 0.15

# Penalty for revisiting
if already_visited:
    reward -= 0.2

# Clamp to range
reward = max(-0.3, min(reward, 1.0))
```

This design ensures:
- ✅ Continuous improvement signal (not just binary win/loss)
- ✅ Exploration encouragement (new logs rewarded)
- ✅ Pattern recognition learning (sequence matters)

## Validation Checklist

Before submission:
- [x] Docker builds successfully: `docker build -t test -f server/Dockerfile .`
- [x] Server starts: `python -m uvicorn server.app:app --host 0.0.0.0 --port 8000`
- [x] Health check passes: `curl http://localhost:8000/health`
- [x] Reset works: `curl -X POST http://localhost:8000/reset`
- [x] Step works: `curl -X POST http://localhost:8000/step -d '{"log_entry_id": 1}'`
- [x] Inference runs: `python inference.py`
- [x] Output format matches specification
- [x] Scores are 0.0-1.0 range
- [x] Runtime < 20 minutes
- [x] HF Space deployed and responsive

## Results & Impact

This environment enables:

1. **Research**: Benchmark RL algorithms on realistic security tasks
2. **Training**: Train agents to assist SOC analysts
3. **Evaluation**: Measure AI progress on escalating difficulty levels
4. **Deployment**: Production-ready infrastructure for scaled evaluation

## License

MIT License - See LICENSE file for details

## Authors

Team Meta Hackathon 2024

---

**Status**: ✅ Validated & Production Ready
**Last Updated**: 2024-04-08
**OpenEnv Version**: 1.0.0
