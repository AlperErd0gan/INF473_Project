# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GSU Transcript Agent — analyzes student transcript text to determine graduation eligibility for the Computer Engineering department at Galatasaray University. Uses Gemini AI for extraction and rule evaluation.

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

Copy `backend/.env.example` to `backend/.env` and fill in:
- `GEMINI_API_KEY` — Google Gemini API key
- `DATABASE_URL` — PostgreSQL connection string (default: `postgresql://postgres:postgres@localhost:5432/transcript_db`)

PostgreSQL must be running locally. The DB schema auto-creates on backend startup via SQLAlchemy (`Base.metadata.create_all`).

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

1. Client POSTs a transcript `.txt` file to `POST /analyze-transcript`
2. `main.py` reads file bytes, decodes as UTF-8, calls `analyze_transcript_with_gemini()`
3. `agent.py` sends transcript + system prompt to `gemini-2.5-pro` with structured JSON output (`response_schema=TranscriptAnalysisResult`)
4. Gemini returns JSON parsed into `TranscriptAnalysisResult` (Pydantic model)
5. API returns `{ status, student_info: { gpa, total_ects }, graduation_status, missing_conditions }`

### Graduation Rules (encoded in agent.py system prompt)

- Minimum GPA: 2.00
- Minimum ECTS: 240
- All mandatory 8-semester curriculum courses passed

### Key Constraint

DB saving is intentionally commented out in `main.py:43-45` — `StudentTranscript` model exists but is not populated yet. Frontend `App.jsx` is still the default Vite scaffold with no API integration.
