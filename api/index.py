"""
Vercel Serverless Function Entry Point for FIFA World Cup 2026 Nexus AI
"""

import sys
import os

# Add root project path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app

# Vercel serverless exposes the FastAPI ASGI app directly
