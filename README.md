# GSU Virtual Academic Advisor

Graduation analysis system for the Computer Engineering department at Galatasaray University. Paste a student transcript and the system uses the Groq API (Llama 3.3) to analyze it, then reports graduation status and missing courses.

## Requirements

- Python 3.10+
- Node.js 18+
- npm
- Groq API key (already embeddable in `run.sh` for zero extra setup on target machine)

Not: `run.sh`, `python3/node/npm` eksikse bunu algilar ve "otomatik kurayim mi?" sorusu sorar.
Desteklenen otomatik kurulumlar: macOS (Homebrew), Linux (apt/dnf/yum/pacman).

## One-command run (recommended for submission)

```bash
chmod +x run.sh
./run.sh
```

`run.sh` automatically:
- checks `python3`, `node`, `npm` and asks for auto-install if missing
- creates backend virtualenv if missing
- installs backend requirements
- installs frontend dependencies (with `npm ci` when lockfile exists)
- starts backend (`127.0.0.1:8000`) and frontend (`127.0.0.1:5173`)

## API key behavior

- If `GROQ_API_KEY` is already set in your shell, it is used directly.
- Else if `backend/.env` contains a valid `GROQ_API_KEY`, it is used.
- Else if `run.sh` contains a non-placeholder `EMBEDDED_GROQ_API_KEY`, `backend/.env` is created automatically and no extra key entry is required on the target machine.

Before delivery, you can put your key into this line in `run.sh`:

```bash
EMBEDDED_GROQ_API_KEY="${EMBEDDED_GROQ_API_KEY:-PASTE_YOUR_GROQ_API_KEY_HERE}"
```

## Manual run (optional)

```bash
# Backend (inside backend/, venv active)
uvicorn main:app --host 127.0.0.1 --port 8000

# Frontend (inside frontend/)
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173
- API Docs: http://127.0.0.1:8000/docs

## Testing

You can run predefined transcript analysis scenarios using the included test script. This will validate if the analysis pipeline correctly determines graduation status for different student edge cases.

```bash
# From the project root, using the backend virtual environment:
./backend/venv/bin/python test_scenarios.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/transcripts/upload` | Upload transcript text, returns `transcript_id` |
| POST | `/analysis/analyze/{id}` | Run analysis, returns `analysis_id` |
| GET | `/analysis/{id}` | Fetch analysis result |
| GET | `/analysis/history` | List all past analyses |
| DELETE | `/analysis/{id}` | Delete analysis result and associated transcript |

## Architecture

![Sequence Diagram](sequence-diagram.png)

Multi-agent analysis pipeline:

1. **Parse**: LLM (`TranscriptParserAgent`) extracts raw transcript text → structured JSON (student name, GPA, ECTS, completed courses).
2. **Evaluate**: Pure Python logic validates the structured data using `CourseVerifierAgent`, `ECTSVerifierAgent`, and `RequirementsAgent`.
3. **Report & Tool Calling**: LLM (`MasterAgent`) takes the validation results and generates a concise graduation report. **During this phase, the MasterAgent is equipped with native Tool Calling capabilities.** It can autonomously query the SQLite database (`check_student_history`) mid-generation to look up a student's past transcripts and adapt its final report based on their historical progress.

LLM calls use Groq API (`llama-3.3-70b-versatile`), dynamically switching between native Tool Calling and JSON mode for reliable structured output.

Database: SQLite (`backend/transcript_agent.db`), 3 tables: `students`, `transcripts`, `analysis_results`.

### Database Schema

![Database Schema](db_schema.png)
