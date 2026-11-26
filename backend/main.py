from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import APP_ENV, APP_VERSION, get_cors_origins
from backend.database import Base, engine
from backend.api.routes import mentor
from backend.api.routes import interview
from backend.api.routes import jobs
from backend.api.routes import cv
from backend.api.routes import skill_gap
from backend.api.routes import career
from backend.api.routes import resume_parser
from backend.api.routes import resume
from backend.api.routes import candidate
def initialize_database():
    """Create SQLAlchemy tables that do not already exist."""
    from backend.models import candidate  # noqa: F401
    from backend.models import career_recommendation  # noqa: F401
    from backend.models import interview_history  # noqa: F401
    from backend.models import job_match  # noqa: F401
    from backend.models import mentor_conversation  # noqa: F401
    from backend.models import resume  # noqa: F401
    from backend.models import skill  # noqa: F401

    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="SkillBridge AI Career Platform",
    description="AI-powered career development and job matching platform",
    version=APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    return {
        "message": "Welcome to SkillBridge AI Career Platform",
        "status": "Running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "SkillBridge",
        "environment": APP_ENV,
        "version": APP_VERSION,
    }
app.include_router(candidate.router)

app.include_router(resume.router)

app.include_router(resume_parser.router)

app.include_router(career.router)

app.include_router(skill_gap.router)

app.include_router(cv.router)

app.include_router(jobs.router)

app.include_router(interview.router)

app.include_router(mentor.router)
