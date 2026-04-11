"""
Simple launcher for the server
"""
import sys
from pathlib import Path
import uvicorn

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, log_level="info", reload=False)
