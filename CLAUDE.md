# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repo.

## Project Overview

GSU Transcript Agent — analyzes student transcript text for graduation eligibility, Computer Engineering dept, Galatasaray University. Uses Gemini AI for extraction + rule evaluation.

## Commands

### Run Everything
```bash
./run.sh   # starts backend (port 8000) + frontend (port 5173), Ctrl+C stops both
```

### Backend (FastAPI)
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev      # dev server at http://localhost:5173
npm run build    # production build
npm run preview  # preview production build
```

## Environment Setup

Copy `backend/.env.example` to `backend/.env`, fill:
- `GEMINI_API_KEY` — Google Gemini API key
- `DATABASE_URL` — PostgreSQL connection string (default: `postgresql://postgres:postgres@localhost:5432/transcript_db`)

PostgreSQL must run locally. DB schema auto-creates on backend startup via SQLAlchemy (`Base.metadata.create_all`).

## Architecture

```
backend/
  main.py      — FastAPI app, single POST /analyze-transcript endpoint
  agent.py     — Gemini client + Pydantic response schema (TranscriptAnalysisResult)
  database.py  — SQLAlchemy engine + session factory
  models.py    — StudentTranscript ORM model (DB persistence not yet wired in main.py)

frontend/
  src/App.jsx  — Currently default Vite starter (not yet connected to backend API)
```

### Request Flow

1. Client POSTs transcript `.txt` file to `POST /analyze-transcript`
2. `main.py` reads file bytes, decodes UTF-8, calls `analyze_transcript_with_gemini()`
3. `agent.py` sends transcript + system prompt to `gemini-2.5-pro` with structured JSON output (`response_schema=TranscriptAnalysisResult`)
4. Gemini returns JSON parsed into `TranscriptAnalysisResult` (Pydantic model)
5. API returns `{ status, student_info: { gpa, total_ects }, graduation_status, missing_conditions }`

### Graduation Rules (encoded in agent.py system prompt)

- Minimum GPA: 2.00
- Minimum ECTS: 240
- All mandatory 8-semester curriculum courses passed

### Key Constraint

DB saving intentionally commented out in `main.py:43-45` — `StudentTranscript` model exists but not populated. Frontend `App.jsx` still default Vite scaffold, no API integration.