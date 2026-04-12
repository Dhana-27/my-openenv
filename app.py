#!/usr/bin/env python
"""
Entry point for HuggingFace Spaces - Exposes FastAPI app
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from server.app import app, main
except Exception as e:
    # Fallback: create basic app if imports fail
    from fastapi import FastAPI
    app = FastAPI(title="Cyber Investigation Environment")
    
    @app.get("/")
    async def root():
        return {"error": f"Failed to load main app: {str(e)}"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    def main():
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=7860)

# Explicitly export app for HF Spaces detection
__all__ = ['app']

if __name__ == "__main__":
    main()
