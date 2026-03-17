# Vercel serverless function entry point for FastAPI backend
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.server import app

handler = app
