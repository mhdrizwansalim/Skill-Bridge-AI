import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

APP_NAME = "SkillBridge AI Career Platform"
APP_VERSION = "1.0.0"
APP_ENV = os.getenv("APP_ENV", "development")

DATA_PATH = PROJECT_ROOT / "data" / "processed"
MODEL_PATH = PROJECT_ROOT / "models"

CV_PATH = DATA_PATH / "cv_builder"
CAREER_PATH = DATA_PATH / "candidates"
MENTOR_PATH = DATA_PATH / "career_mentor"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

def get_cors_origins():
    configured = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in configured.split(",") if origin.strip()]