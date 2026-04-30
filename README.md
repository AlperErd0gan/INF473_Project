# GSU Virtual Academic Advisor

Graduation analysis system for the Computer Engineering department at Galatasaray University. Paste a student transcript and the system uses the Gemini API to analyze it, then reports graduation status and missing courses.

## Requirements

- Python 3.10+
- Node.js 18+
- Google Gemini API key

## Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

### Frontend

```bash
cd frontend
npm install
```

## Running

Start both services with one command:

```bash
./run.sh
```

Or separately:

```bash
# Backend (inside backend/, venv active)
uvicorn main:app --reload --port 8000

# Frontend (inside frontend/)
npm run dev
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/transcripts/upload` | Upload transcript text, returns `transcript_id` |
| POST | `/analysis/analyze/{id}` | Run analysis, returns `analysis_id` |
| GET | `/analysis/{id}` | Fetch analysis result |
| GET | `/analysis/history` | List all past analyses |

## Architecture

Two-stage Gemini API pipeline:

1. **Parse**: Raw transcript text → structured JSON (student name, GPA, ECTS, completed courses)
2. **Analyze**: Structured data + hardcoded GSU BIL requirements → graduation report (output in Turkish)

Both calls use `gemini-2.5-pro` with Pydantic `response_schema` for structured output.

Database: SQLite (`backend/transcript_agent.db`), 3 tables: `students`, `transcripts`, `analysis_results`.
