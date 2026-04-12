#!/usr/bin/env python
"""
Entry point for HuggingFace Spaces - Exposes FastAPI app
"""
from server.app import app, main

# Explicitly export app for HF Spaces detection
__all__ = ['app']

if __name__ == "__main__":
    main()
