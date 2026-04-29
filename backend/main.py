from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GSU Transcript Agent API")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to GSU Transcript Agent API"}

@app.post("/analyze-transcript")
async def analyze_transcript(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Read transcript text from file
    content = await file.read()
    transcript_text = content.decode("utf-8") # simplified for text files
    
    # 2. Call LLM Agent to process transcript and evaluate rules
    # This is a stub for the agent logic
    # result = analyze_with_llm(transcript_text)
    
    # Stub response
    return {
        "status": "success",
        "student_info": {
            "gpa": 3.12,
            "total_ects": 210,
        },
        "graduation_status": "Not Graduated",
        "missing_conditions": [
            "Missing 30 ECTS",
            "Missing ISG402 course"
        ]
    }
