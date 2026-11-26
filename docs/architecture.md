# SkillBridge Architecture

## Runtime flow

1. React sends API requests through a centralized API client.
2. FastAPI validates and routes requests.
3. Route modules orchestrate services and database models.
4. Resume services extract and normalize PDF profile data.
5. SQLAlchemy persists candidates, resumes, job matches, interviews, and mentor conversations.
6. Career, CV, interview, job, and mentor modules consume normalized profile data.

## Backend modules

- `backend/main.py`: application initialization and route registration.
- `backend/config.py`: environment and project-path configuration.
- `backend/database.py`: SQLAlchemy engine and session factory.
- `backend/api/routes/`: FastAPI endpoints.
- `backend/services/`: application logic and integrations.
- `backend/models/`: SQLAlchemy persistence models.
- `backend/schemas/`: Pydantic models.
- `backend/crud.py`: candidate CRUD helpers.

## Profile formats

The application supports:

- New profiles with top-level `name`, `email`, `phone`, and `skills`.
- Legacy profiles with `personal_details` and list-based education, experience, projects, or languages.

Normalization is handled by candidate/CV services before rendering or generation.

## Data and privacy

Private database files, uploaded resumes, resume libraries, generated CVs, and generated reports should remain untracked. The SQLite database and notebook output are local application state, not source data.

## Optional AI services

- Ollama is optional for mentor responses.
- FAISS/text artifacts are read as retrieved context.
- External AI failures must return an explicit unavailable status, never fabricated success.
