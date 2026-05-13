# GSU Virtual Academic Advisor

Graduation analysis system for the Computer Engineering department at Galatasaray University. Upload a student transcript and the system parses it, evaluates graduation eligibility against curriculum rules, and generates a report — with historical comparison via tool calling.

## Requirements

- Python 3.10+
- Node.js 18+
- npm
- Groq API key

Not: `run.sh`, `python3/node/npm` eksikse bunu algilar ve "otomatik kurayim mi?" sorusu sorar.
Desteklenen otomatik kurulumlar: macOS (Homebrew), Linux (apt/dnf/yum/pacman).

## One-command run (recommended)

```bash
chmod +x run.sh
./run.sh
```

`run.sh` automatically:
- checks `python3`, `node`, `npm` and asks for auto-install if missing
- creates backend virtualenv if missing
- installs backend and frontend dependencies
- starts backend (`127.0.0.1:8000`) and frontend (`127.0.0.1:5173`)

## API key behavior

- If `GROQ_API_KEY` is set in your shell, it is used directly.
- Else if `backend/.env` contains `GROQ_API_KEY`, it is used.
- Else the script prompts once, saves to `backend/.env`, and continues.
- Else if `run.sh` contains a non-placeholder `EMBEDDED_GROQ_API_KEY`, `backend/.env` is created automatically.

Before delivery, embed your key into this line in `run.sh`:

```bash
EMBEDDED_GROQ_API_KEY="${EMBEDDED_GROQ_API_KEY:-PASTE_YOUR_GROQ_API_KEY_HERE}"
```

## Manual run

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Frontend (separate terminal)
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173
- API Docs: http://127.0.0.1:8000/docs

## Testing

Five test suites cover parsing, validation, rule logic, and the full pipeline.

### No API key needed (pure-logic tests)

```bash
# Deterministic parser — verifies tab-separated GSU transcript parsing
./backend/venv/bin/python -m pytest test_parse.py -v

# Transcript validation — duplicate detection, single-file enforcement
./backend/venv/bin/python -m pytest test_transcript_validation.py -v

# Curriculum rules + course equivalency
./backend/venv/bin/python -m pytest test_requirements_equivalency.py -v

# MasterAgent report review logic (no real LLM call)
./backend/venv/bin/python -m pytest test_master_report_agent.py -v
```

### Requires Groq API key (end-to-end LLM pipeline)

These run the full multi-agent pipeline against 20 real transcript scenarios.

```bash
# Set key first if not in backend/.env
export GROQ_API_KEY=your_key_here

./backend/venv/bin/python test_scenarios.py
```

Each scenario has an expected pass/fail outcome. Results print to stdout with PASS/FAIL per case.

### Scenario files

20 transcript scenarios live in `analysis-input-scenarios/`:

| File | Case |
|------|------|
| `01-legacy-baseline-pass.txt` | Legacy curriculum, full pass |
| `07-low-gpa-fail.txt` | GPA below 2.00 |
| `08-language-requirement-fail.txt` | Missing B2 language |
| `09-ects-below-240.txt` | ECTS under 240 |
| `13-inf112-failed-but-recovered-pass.txt` | Failed + retaken course |
| `16-2020-code-equivalency-pass.txt` | Course code migration pass |
| ... | (see `analysis-input-scenarios/README.md` for full list) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/transcripts/upload` | Upload transcript text, returns `transcript_id` |
| POST | `/analysis/analyze/{id}` | Run analysis pipeline, returns `analysis_id` |
| GET | `/analysis/{id}` | Fetch analysis result |
| GET | `/analysis/history` | List all past analyses |
| DELETE | `/analysis/{id}` | Delete analysis result and transcript |

## Architecture

![Sequence Diagram](sequence-diagram.png)

Multi-agent pipeline:

1. **Parse**: Deterministic parser first (`_parse_tab_format`); falls back to `TranscriptParserAgent` (Groq LLM) for non-standard formats. Extracts student name, GPA, ECTS, completed courses.
2. **Evaluate**: Pure Python agents — `CourseVerifierAgent`, `ECTSVerifierAgent`, `RequirementsAgent` — validate structured data against `gsu_requirements.py` (curriculum rules, equivalency maps, legacy/modern curriculum detection).
3. **Report + Tool Calling**: `MasterAgent` (Groq LLM) generates the graduation report. Equipped with native Tool Calling — can query SQLite (`check_student_history`) mid-generation to compare against the student's past transcripts.

LLM: Groq API (`llama-3.3-70b-versatile`, fallback `llama-3.1-8b-instant`).

Database: SQLite (`backend/transcript_agent.db`), 3 tables: `students`, `transcripts`, `analysis_results`.

### Database Schema

![Database Schema](db_schema.png)
