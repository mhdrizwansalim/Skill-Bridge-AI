# SkillBridge AI by Zequa

SkillBridge AI is a full-stack career intelligence platform for resume analysis, career recommendations, skill-gap assessment, job-description matching, CV generation, mock interviews, and RAG-assisted career mentoring.

## Technology stack

- **Backend:** FastAPI, SQLAlchemy, Pydantic, PyMuPDF
- **Database:** SQLite
- **Frontend:** React 18, Vite, Recharts, Lucide
- **AI/ML:** Ollama, Sentence Transformers, FAISS, spaCy, scikit-learn
- **Documents:** ReportLab and python-docx
- **Notebooks:** Jupyter workflows for data preparation and model analysis

## Architecture

- `backend/` contains the FastAPI application, routes, services, database models, schemas, and configuration.
- `frontend/frontend/` contains the active React/Vite application.
- `notebooks/` contains the 14 analytical and integration workflows.
- `data/` contains raw and processed datasets, reports, uploads, and generated artifacts.
- `database/` contains the local SQLite database.
- `models/` contains trained models and tokenizer/model artifacts.
- `tests/` contains backend test coverage.
- `docs/` contains architecture and setup documentation.

## Installation

Create an environment and install backend dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd frontend/frontend
npm install
```

Copy the environment template:

```bash
cp .env.example .env
```

Never commit `.env`, uploaded resumes, local databases, private datasets, or generated private reports.

## Run the application

Backend:

```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Swagger UI: `http://127.0.0.1:8000/docs`

Frontend:

```bash
cd frontend/frontend
npm run dev
```

Frontend: `http://localhost:5173`

## Environment configuration

| Variable | Purpose | Default |
|---|---|---|
| `APP_ENV` | Application environment label | `development` |
| `CORS_ORIGINS` | Comma-separated frontend origins | localhost origins |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./database/skillbridge.db` |
| `OLLAMA_URL` | Ollama service URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama generation model | `llama3.2:3b` |
| `VITE_API_BASE_URL` | Frontend API base URL | `http://127.0.0.1:8000` |

## Core API areas

- Candidate profiles: `/candidate`
- Resume upload and parsing: `/resume`
- Career recommendations and skill gaps: `/career`
- Job matching and analysis: `/jobs`
- CV profile and PDF generation: `/cv`
- Mock interviews: `/interview`
- Career mentor and history: `/mentor`

## Resume processing

PDF uploads are validated for MIME type, `.pdf` extension, `%PDF` signature, and a 10 MB size limit. Embedded text is extracted with PyMuPDF. If a PDF has no readable text, the parser renders pages and uses a local Tesseract executable with English OCR when available. Scanned PDFs without OCR return an HTTP 422 with a clear installation requirement instead of crashing.

## Testing

Run backend tests:

```bash
source .venv/bin/activate
pytest -q
```

Build the frontend:

```bash
cd frontend/frontend
npm run build
```

## Notebooks

The notebooks in `notebooks/` preserve the analytical workflow. Do not execute expensive training or model-download cells unless you intentionally need them. Notebook-specific dependencies are not all required for the web application; use `requirements.txt` for the backend and activate notebook dependencies separately.

## Known limitations

- Scanned-PDF OCR requires a local Tesseract executable and English language data.
- Mentor responses depend on a running Ollama service.
- Mock-interview feedback is a transparent local rule-based score, not an external AI assessment.
- Notebook-generated reports may be historical and should be validated against a live uploaded profile.
- Large private datasets, model binaries, and uploaded resumes are excluded from Git.
