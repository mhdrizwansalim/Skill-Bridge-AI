# Setup Guide

## Practical setup

1. Open the project root.
2. Create `.env` from `.env.example`.
3. Create and activate a Python 3.12 virtual environment.
4. Install `requirements.txt`.
5. Install dependencies in `frontend/frontend`.
6. Start the backend.
7. Start the frontend.
8. Open Swagger or the React dashboard.

## Backend

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend

```bash
cd frontend/frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in `frontend/frontend/.env` or the project `.env` only when the API is not on `http://127.0.0.1:8000`.

## Ollama mentor

Install and run Ollama separately if mentor generation is required. Configure:

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

The mentor endpoint returns a 503 when Ollama is unavailable.

## OCR

Install Tesseract on macOS:

```bash
brew install tesseract
```

Ensure the `tesseract` executable is on `PATH`. The parser uses English OCR (`eng`) for scanned PDFs and still returns an explicit 422 if OCR is unavailable or no text is extracted.

## Database

SQLAlchemy creates missing tables on FastAPI startup. SQLite is stored at `database/skillbridge.db` by default. Set `DATABASE_URL` to use another database.

## Troubleshooting

- **CORS error:** add the frontend origin to `CORS_ORIGINS`.
- **Resume upload says not enough text:** the PDF is likely scanned. OCR is not enabled by default.
- **Mentor unavailable:** verify Ollama and `OLLAMA_MODEL`.
- **No career report:** upload a resume or run the career notebook workflows.
- **Frontend cannot connect:** verify the backend health endpoint at `/health`.
