# SkillBridge by Zequa — React frontend

This is the first frontend implementation for the existing SkillBridge project. It is designed to live in the repository's existing `frontend/` folder and consume the FastAPI backend on port 8000.

## 1. Install Node.js

Use Node.js 20 LTS or newer. Check:

```bash
node -v
npm -v
```

## 2. Put these files in your project

Extract the contents of this archive into your existing `SkillBridgeByZequa/` folder. The archive contains a `frontend/` directory. It does not contain or overwrite your backend, database, data, models, notebooks, or virtual environment.

## 3. Install frontend dependencies

```bash
cd frontend
npm install
```

## 4. Start the backend

Open a terminal at the project root:

```bash
source .venv/bin/activate
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

If `uvicorn` is not installed in the virtual environment, install the backend requirements used by your project first.

## 5. Start the frontend

Open a second terminal:

```bash
cd frontend
npm run dev
```

Open:

- Dashboard: http://localhost:5173
- FastAPI docs: http://127.0.0.1:8000/docs

## Notes about this first version

- The dashboard reads from the existing API routes: `/health`, `/candidate/resumes`, `/candidate/profile`, `/career/recommendations`, `/career/skill-gap`, `/jobs/matches`, and `/interview/report`.
- Resume upload posts to `/resume/upload`.
- The AI mentor posts to `/mentor/ask`. Ollama must be running with the configured model for this feature to answer.
- Empty states are intentional. They appear when the corresponding report JSON has not yet been generated.
- The weekly activity chart is explicitly illustrative until the backend exposes real activity-history data.
- The current backend candidate endpoint reads `personal_details.full_name`; the frontend also checks top-level `name` and `full_name` as a compatibility fallback.
- This frontend is a local development prototype. It does not yet include authentication, authorization, production deployment hardening, or persistent activity analytics.

## Next integration tasks

1. Verify all existing API routes against the current files in `data/processed/`.
2. Align candidate profile serialization with the output from Notebook 08/09.
3. Add database-backed endpoints for saved job matches, skill records, interview history, and mentor conversations.
4. Add authentication before exposing personal resume information beyond localhost.
