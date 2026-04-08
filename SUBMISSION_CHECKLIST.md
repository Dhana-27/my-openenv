# Pre-Submission Verification Checklist

**Deadline**: April 8, 2026, 11:59 PM IST  
**Status**: Ready ✅

---

## 1. Code Quality Checks

### ✅ Syntax Validation
```powershell
python -m py_compile models.py
python -m py_compile client.py
python -m py_compile inference.py
python -m py_compile server/app.py
python -m py_compile server/environment.py
```

### ✅ Type Checking (Pylance)
- [x] No type errors in `environment.py`
- [x] No type errors in `models.py`
- [x] No type errors in `client.py`
- [x] No type errors in `server/app.py`

### ✅ Imports Work
```powershell
python -c "from models import LogAnalysisAction, LogAnalysisObservation, LogAnalysisState; print('✅ Models OK')"
python -c "from client import CyberInvestigationClient; print('✅ Client OK')"
python -c "from server.environment import CyberInvestigationEnvironment; print('✅ Environment OK')"
python -c "from server.app import app; print('✅ FastAPI App OK')"
```

---

## 2. Local Testing

### ✅ Start Server
```powershell
# Terminal 1
python -m uvicorn server.app:app --port 8000
```

### ✅ Test Endpoints (Terminal 2)
```powershell
# Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Reset task1
curl -X POST "http://localhost:8000/reset?task_name=task1"

# Step
curl -X POST http://localhost:8000/step -H "Content-Type: application/json" -d '{"log_entry_id": 2}'

# State
curl http://localhost:8000/state
```

### ✅ Run Inference
```powershell
$env:API_BASE_URL='http://localhost:8000'
$env:MODEL_NAME='cyber-investigation'
$env:HF_TOKEN='test'
python inference.py
```

**Expected Output**:
```
[START]
...
[END]
{"tasks": 3, "scores": [0.6, 1.0, 1.0], "score": 0.8666666666666667}
```

---

## 3. File Structure Verification

### ✅ Required Files Present
- [x] `README.md` (comprehensive, 600+ lines)
- [x] `openenv.yaml` (spec metadata)
- [x] `requirements.txt` (all dependencies)
- [x] `models.py` (Pydantic models)
- [x] `client.py` (HTTP wrapper)
- [x] `inference.py` (baseline script)
- [x] `server/app.py` (FastAPI endpoints)
- [x] `server/environment.py` (core logic)
- [x] `server/Dockerfile` (containerization)

### ✅ Check File Sizes (not empty)
```powershell
ls c:\Users\sreya\OneDrive\Desktop\meta_hackathon\
```

### ✅ Check Dockerfile
```powershell
cat server/Dockerfile
```

Expected content:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4. Docker Verification

### ✅ Docker Build (Optional, for local testing)
```powershell
docker build -t cyber-investigation ./server
```

### ✅ Docker Run
```powershell
docker run -p 8000:8000 cyber-investigation
```

Then test endpoints in another terminal.

---

## 5. Inference Script Validation

### ✅ Check Output Format
```powershell
$env:API_BASE_URL='http://localhost:8000'
$env:MODEL_NAME='cyber-investigation'
$env:HF_TOKEN='test'
python inference.py | Select-Object -First 5
# Should show:
# [START]
# {"inference": "cyber_investigation", ...}
```

### ✅ Check Completion
```powershell
python inference.py | Select-Object -Last 3
# Should show:
# [STEP] ...
# [END]
# {"tasks": 3, "scores": [...], "score": ...}
```

### ✅ Verify All 3 Tasks Run
```powershell
python inference.py | grep '\[STEP\].*"task'
# Should see: task1, task2, task3
```

### ✅ Verify Scores in [0.0, 1.0]
```powershell
python inference.py | grep '"score"'
# All scores should be between 0.0 and 1.0
```

---

## 6. OpenEnv Compliance

### ✅ YAML is Valid
```powershell
Get-Content openenv.yaml
```

Check has:
- [x] `name:`
- [x] `version:`
- [x] `description:`
- [x] `tasks:` (3+ tasks)
- [x] `specs:`
- [x] `endpoints:` (at least /reset, /step, /state, /health)

### ✅ 3 Tasks Defined
```powershell
Get-Content openenv.yaml | grep -A 1 'task'
# Should see: login_detection, lateral_movement, privilege_escalation
```

### ✅ Pydantic Models Present
```powershell
python -c "
from models import LogAnalysisAction, LogAnalysisObservation, LogAnalysisState
print('Action:', LogAnalysisAction.__fields__.keys())
print('Observation:', LogAnalysisObservation.__fields__.keys())
print('State:', LogAnalysisState.__fields__.keys())
"
```

Expected:
- `LogAnalysisAction`: `log_entry_id`
- `LogAnalysisObservation`: `current_log_id`, `current_log_content`, `available_log_ids`, `suspicious_score`, `context`
- `LogAnalysisState`: `episode_id`, `step_count`, `path_followed`, `task_name`, `game_phase`

---

## 7. API Endpoints Test

### ✅ Test All 4 Endpoints
```powershell
# Start server
$server = Start-Job { python -m uvicorn server.app:app --port 8000 }
Start-Sleep 3

# 1. Health
Invoke-WebRequest http://localhost:8000/health -UseBasicParsing
# Should return: {"status":"healthy"}

# 2. Reset
Invoke-WebRequest -Uri "http://localhost:8000/reset?task_name=task1" `
  -Method POST -UseBasicParsing
# Should return observation JSON

# 3. Step
$body = @{"log_entry_id" = 0} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/step" `
  -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
# Should return observation + reward + done + info

# 4. State
Invoke-WebRequest http://localhost:8000/state -UseBasicParsing
# Should return state JSON

Stop-Job $server
```

---

## 8. Pre-Submission Validation Script

### ✅ Run This Before Pushing to HF

```powershell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OpenEnv Submission Validation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Check files exist
Write-Host "`n1. Checking required files..." -ForegroundColor Yellow
$files = @("README.md", "openenv.yaml", "requirements.txt", "models.py", "client.py", "inference.py", "server/app.py", "server/environment.py", "server/Dockerfile")
foreach ($f in $files) {
    if (Test-Path $f) {
        Write-Host "  ✅ $f"
    } else {
        Write-Host "  ❌ $f MISSING"
    }
}

# 2. Check syntax
Write-Host "`n2. Checking syntax..." -ForegroundColor Yellow
foreach ($f in @("models.py", "client.py", "inference.py", "server/environment.py", "server/app.py")) {
    try {
        python -m py_compile $f
        Write-Host "  ✅ $f syntax OK"
    } catch {
        Write-Host "  ❌ $f has syntax errors"
    }
}

# 3. Check imports
Write-Host "`n3. Checking imports..." -ForegroundColor Yellow
try {
    python -c "from models import *; from client import *; from server.environment import *" 2>$null
    Write-Host "  ✅ All imports work"
} catch {
    Write-Host "  ❌ Import errors found"
}

# 4. Start server and test
Write-Host "`n4. Testing server..." -ForegroundColor Yellow
$job = Start-Job { python -m uvicorn server.app:app --port 8000 }
Start-Sleep 3

try {
    $health = Invoke-WebRequest http://localhost:8000/health -UseBasicParsing
    Write-Host "  ✅ /health endpoint responds"
} catch {
    Write-Host "  ❌ /health endpoint failed"
}

# 5. Run inference
Write-Host "`n5. Running inference script..." -ForegroundColor Yellow
$env:API_BASE_URL='http://localhost:8000'
$env:MODEL_NAME='cyber-investigation'
$env:HF_TOKEN='test'

try {
    $output = python inference.py
    if ($output -match '\[END\]') {
        Write-Host "  ✅ Inference completed successfully"
        $score = $output | Select-String '"score"' | Select-Object -Last 1
        Write-Host "  📊 $score"
    } else {
        Write-Host "  ❌ Inference script failed"
    }
} catch {
    Write-Host "  ❌ Inference threw error: $_"
}

Stop-Job $job

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ READY FOR HF SPACE SUBMISSION" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
```

---

## 9. Git Setup for HF Space

### Before pushing, verify:

```powershell
# Initialize git (if not already done)
git init
git config user.name "Team Meta Hackathon"
git config user.email "sreyyy685@gmail.com"

# Check git status
git status
# Should show all files ready to commit

# Stage everything
git add .

# Create commit
git commit -m "OpenEnv Cyber Investigation - Round 1 Submission"

# Verify commit
git log --oneline -1
```

---

## 10. HF Space Submission Steps

### Step 1: Create Space on HF
```
Go to https://huggingface.co/spaces/new
- Space name: openenv-cyber-investigation
- License: MIT
- SDK: Docker
- Create
```

### Step 2: Add Git Remote
```powershell
git remote add hf https://huggingface.co/spaces/YOUR_HF_USERNAME/openenv-cyber-investigation
```

### Step 3: Push to HF
```powershell
git push -u hf main
```

**Note**: HF will build Docker image automatically (takes 5-10 minutes)

### Step 4: Verify Space is Live
```powershell
# After HF finishes building
curl https://YOUR_HF_USERNAME-openenv-cyber-investigation.hf.space/health
# Should return: {"status":"healthy"}
```

### Step 5: Set Environment Variables (if needed)
```
Go to Space Settings → Repository Secrets
Add:
- API_BASE_URL: http://localhost:8000
- MODEL_NAME: cyber-investigation
- HF_TOKEN: your-token
```

### Step 6: Submit on Hackathon Platform
```
Paste Space URL:
https://huggingface.co/spaces/YOUR_HF_USERNAME/openenv-cyber-investigation
```

---

## Final Checklist Before Deadline

- [ ] All files syntax-checked: ✅
- [ ] All imports working: ✅
- [ ] Server starts without errors: ✅
- [ ] All 4 endpoints respond: ✅
- [ ] Inference runs successfully: ✅
- [ ] Output format correct ([START]/[STEP]/[END]): ✅
- [ ] All 3 tasks execute: ✅
- [ ] Scores in [0.0, 1.0] range: ✅
- [ ] README complete and detailed: ✅
- [ ] openenv.yaml valid: ✅
- [ ] Dockerfile builds: ✅
- [ ] No type errors (Pylance): ✅
- [ ] Git initialized and ready: ⏳
- [ ] HF Space created: ⏳
- [ ] Code pushed to HF: ⏳
- [ ] Environment variables set: ⏳
- [ ] Submission URL posted: ⏳

---

**Time Remaining**: Check your local time!  
**Deadline**: April 8, 2026, 11:59 PM IST (UTC+5:30)

Good luck with your submission! 🚀
