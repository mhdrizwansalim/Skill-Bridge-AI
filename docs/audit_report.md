# SkillBridge AI by Zequa - Initial Audit Report

## Audit scope

This report is based on an initial inspection of the workspace structure, backend entry points and routes, SQLite configuration, React entry points and navigation, project manifests, processed data, database schema, tests, and all 14 notebook files.

## Verification summary

| Check | Result |
|---|---|
| Backend Python syntax | Passed (`backend` and `src` compiled successfully) |
| Backend application startup | Passed for the health and data routes tested |
| Frontend production build | Passed |
| Frontend build warning | Bundle is larger than 500 KB |
| PDF resume extraction module | Implemented for embedded text; OCR is not implemented |
| Database tables | Seven candidate-related tables exist |
| Automated tests | None found |
| Python dependency manifest | Missing from the project root |
| Root README | Missing |
| `.gitignore` | Missing |
| `.env.example` | Missing at project root |

## Existing problems

### 1. End-to-end resume workflow is incomplete

- Resume upload only saves the PDF and does not create or parse a candidate profile.
- Parsing is exposed separately through `/resume/parse/{filename}`.
- The parser has no OCR fallback and returns an HTTP 422 message for scanned PDFs.
- The upload response does not include a profile or `profile_id`.
- Resume library refresh is manually driven by the frontend and not guaranteed after parsing.

**Root cause:** Upload and parsing are separate endpoints with no orchestration.

**Files:** `backend/api/routes/resume.py`, `backend/api/routes/resume_parser.py`, `frontend/frontend/src/pages/ModulePage.jsx`

### 2. Candidate profile data is inconsistent and sometimes sample-based

- Legacy profiles use `personal_details.full_name`, while newer profiles use top-level `name` and `email`.
- Candidate listing and profile retrieval support both formats in some places.
- The career report contains sample/test candidate details rather than a user-selected profile.
- The job analyzer report also uses the literal candidate name `Candidate`.
- The overview and sidebar contain hardcoded personal or identity values.

**Root cause:** Notebook-generated reports and frontend fallbacks are not tied to one canonical profile.

**Files:** `backend/api/routes/candidate.py`, `backend/api/routes/career.py`, `backend/api/routes/jobs.py`, `frontend/frontend/src/pages/Overview.jsx`, `frontend/frontend/src/components/Sidebar.jsx`, `data/processed/candidates/complete_candidate_career_report.json`, `data/processed/cv_builder/updated_candidate.json`

### 3. Career, skill-gap, job, interview, and CV APIs serve pre-generated files

- Career recommendations, skill gaps, job matches, mock-interview reports, and CV download depend on notebook-produced JSON/PDF files.
- Several endpoints expose raw report structures or dictionary keys from notebooks.
- The CV endpoint points to a PDF that may not match the active candidate.
- There are no interactive POST/PUT workflows for CV editing, job description analysis, interview answers, or interview history.

**Root cause:** Notebook outputs were wrapped with read-only API routes instead of being converted into application services.

**Files:** `backend/api/routes/career.py`, `backend/api/routes/skill_gap.py`, `backend/api/routes/jobs.py`, `backend/api/routes/cv.py`, `backend/api/routes/interview.py`

### 4. Career recommendation scores and report schemas need validation

- Recommendations contain capitalized, inconsistent keys such as `Career`, `Match Score`, `Matched Skills`, and `Missing Skills`.
- Skills are not shown through one normalized frontend model.
- The existing IoT example reports a 9.09% match based on 2 of 22 required skills.
- The report can include duplicate-looking, case-variant, or overlapping taxonomy terms.

**Root cause:** Notebook output is returned without a final normalized recommendation schema or skill taxonomy service.

**Files:** `backend/api/routes/career.py`, `data/processed/candidates/complete_candidate_career_report.json`

### 5. Frontend modules do not cover the complete requested workflow

- Navigation does not include Candidate Profile or CV Builder.
- The career, skill-gap, job, and interview pages render raw JSON previews.
- The resume profile page also renders raw JSON.
- Upload UI does not call the parser endpoint and therefore does not complete parsing.
- Activity and job matching data are partly illustrative or unavailable.
- The overview includes fallback text/name such as `Rizwan` instead of a neutral empty state.

**Root cause:** The frontend is a starter dashboard connected to legacy report endpoints, not a complete module suite.

**Files:** `frontend/frontend/src/App.jsx`, `frontend/frontend/src/components/Sidebar.jsx`, `frontend/frontend/src/pages/Overview.jsx`, `frontend/frontend/src/pages/ModulePage.jsx`, `frontend/frontend/src/api.js`

### 6. Mentor behavior is basic and not a modular RAG implementation

- The endpoint sends the entire saved JSON profile plus a question directly to Ollama.
- It does not retrieve context through the processed FAISS/text artifacts in a documented service.
- Conversation history is not persisted.
- Ollama URL and model are hardcoded in backend configuration.
- Service errors expose the underlying request exception text.

**Root cause:** The route lacks configuration validation and a separate RAG/service layer.

**Files:** `backend/api/routes/mentor.py`, `backend/config.py`, `data/processed/career_mentor/`

### 7. Database models are not initialized or integrated

- SQLAlchemy tables exist in the SQLite file, but model relationships and relationships collections are missing.
- No startup initialization is shown in `backend/main.py`.
- Candidate and resume JSON workflows do not persist through the SQLAlchemy session.
- CRUD functions create standalone sessions correctly but do not use FastAPI dependency injection.
- No duplicate prevention or candidate/resume uniqueness policy is implemented.

**Root cause:** Database scaffolding exists separately from API workflows.

**Files:** `backend/main.py`, `backend/database.py`, `backend/crud.py`, `backend/models/*.py`

### 8. Backend schema and response handling are inconsistent

- Most routes have no Pydantic request/response schemas.
- Several routes use raw dictionaries and raw JSON file contents.
- Exception handling varies and some service errors leak implementation details.
- CORS is hardcoded to `http://localhost:5173`.
- Resume upload validates content type, filename, signature, and size, but does not reject a filename outside normal limits or validate PDF parsing before saving.

**Root cause:** The backend was assembled as route scripts rather than through centralized schema, service, and configuration layers.

**Files:** `backend/main.py`, `backend/config.py`, `backend/api/routes/*.py`, `backend/schemas/`

### 9. Security and GitHub readiness are weak

- No root `.gitignore` is present.
- No root `.env.example` is present.
- SQLite database and generated resume JSON/PDF files containing personal information are in the workspace.
- Uploaded resumes and resume-library files are not excluded by configuration.
- Virtual environment and frontend `node_modules` are present in the workspace and would be huge Git additions.
- The existing profile exposes a real-looking email and phone number in processed files.
- The workspace is not currently a Git repository, so commit history/readiness could not be audited.

**Root cause:** Environment, privacy, and repository policies were not configured.

**Files:** project root, `database/skillbridge.db`, `data/processed/uploaded_resumes/`, `data/processed/cv_builder/resume_library/`

### 10. Dependency and setup documentation is incomplete

- No root `requirements.txt` is present.
- No root `README.md` is present.
- The frontend package has a nested active app at `frontend/frontend`.
- A starter zip and separate lockfile exist near the frontend but do not establish the canonical setup.
- `docs/setup_guide.md` and `docs/architecture.md` are missing.
- Existing dataset documentation is not an application setup guide.

**Root cause:** The project was developed incrementally from notebooks and a starter frontend without final workspace packaging.

**Files:** project root, `frontend/`, `frontend/frontend/package.json`, `frontend/package-lock.json`, `docs/`

### 11. Notebook structure has naming and syntax issues

- Notebooks 03, 08, 09, 10, and 12 use renamed/fixed filenames instead of the canonical 14 names.
- Notebook 05 has 7 code cells that do not compile as plain Python.
- Notebook 06 has 1 such cell.
- Notebook 07 has 3.
- Notebook 12 has 1.
- Notebook 13 and 14 have an initial code cell that uses notebook-specific syntax.
- Some failures are expected IPython magics such as `%pip`, shell commands, or notebook display syntax, but they still require structural classification and safe execution order.
- Paths, external model downloads, expensive training, and local Ollama assumptions need explicit notebook instructions.

**Root cause:** Fixed variants and notebook magics were added without canonical naming or structural validation.

**Files:** `notebooks/*.ipynb`

## Missing functionality

- Candidate Profile module and CV Builder sidebar pages
- Uploaded-resume-to-parsed-profile pipeline
- OCR status and optional OCR support
- Database-backed candidate/resume CRUD
- Interactive job description analysis
- Interactive CV editing and generated output
- Functional mock interview question/answer workflow and history
- True RAG retrieval for the mentor
- Normalized career, skill-gap, and job-match response schemas
- Interactive skill-gap controls and visual charts
- Upload validation and parser integration tests
- Backend unit and integration tests
- Environment configuration and privacy documentation

## Recommended implementation order

1. **Protect the workspace and centralize configuration**
   - Add `.gitignore`, `.env.example`, configuration validation, and environment-driven paths/services.
   - Document private database, resume, upload, report, and generated-artifact exclusions.

2. **Build the canonical backend foundation**
   - Centralize FastAPI startup, CORS, logging, exception handling, Pydantic schemas, and database initialization.
   - Define one normalized candidate-profile shape and one response envelope.

3. **Complete resume upload and parsing**
   - Make upload validate and parse in one workflow.
   - Support embedded text and explicit scanned-PDF errors.
   - Save JSON and database records and return the created profile.

4. **Implement normalized recommendation and skill-gap services**
   - Replace raw report returns with normalized career cards.
   - Normalize/deduplicate skills and validate match calculations.

5. **Implement job analysis and CV workflows**
   - Add text/upload parsing endpoints and candidate comparison.
   - Add editable CV data and PDF/DOCX generation without invented fields.

6. **Implement mock interview workflows**
   - Generate questions, accept answers, calculate transparent feedback, and persist history.

7. **Refactor mentor into a modular RAG service**
   - Retrieve profile/career context, maintain conversation history, and handle Ollama absence explicitly.

8. **Rebuild and integrate the React modules**
   - Add Candidate Profile and CV Builder pages.
   - Replace raw JSON previews with professional cards, forms, tables, charts, loading states, and empty states.
   - Remove all hardcoded candidate identity fallbacks.

9. **Normalize and validate notebooks**
   - Canonicalize the 14 filenames.
   - Preserve workflows while documenting external dependencies and avoiding expensive training by default.

10. **Add tests and acceptance documentation**
   - Add API/database/unit/integration tests.
   - Add startup, setup, architecture, API, privacy, and troubleshooting documentation.
   - Run backend, frontend, test, notebook, and Git-readiness checks.

## Files most likely to be corrected first

- `backend/main.py`
- `backend/config.py`
- `backend/database.py`
- `backend/crud.py`
- `backend/api/routes/resume.py`
- `backend/api/routes/resume_parser.py`
- `backend/api/routes/candidate.py`
- `backend/api/routes/career.py`
- `backend/api/routes/skill_gap.py`
- `backend/api/routes/jobs.py`
- `backend/api/routes/cv.py`
- `backend/api/routes/interview.py`
- `backend/api/routes/mentor.py`
- `frontend/frontend/src/App.jsx`
- `frontend/frontend/src/components/Sidebar.jsx`
- `frontend/frontend/src/pages/Overview.jsx`
- `frontend/frontend/src/pages/ModulePage.jsx`
- `frontend/frontend/src/api.js`

## Major architectural change requiring confirmation

The implementation should consolidate notebook-generated report files behind backend services and add database-backed persistence. This is a substantial change but preserves existing notebook artifacts and legacy profile formats during migration. No destructive cleanup or file deletion should occur before the existing data and active frontend are mapped to the canonical APIs.
