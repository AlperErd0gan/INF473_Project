import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from agent import analyze_transcript_with_gemini

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
    try:
        analysis_result = analyze_transcript_with_gemini(transcript_text)
        
        # 3. Save to database (optional at this point, but good to have)
        # new_transcript = StudentTranscript(raw_text=transcript_text, gpa=..., is_graduated=...)
        # db.add(new_transcript)
        # db.commit()
        
        return {
            "status": "success",
            "student_info": {
                "gpa": analysis_result.student_info.gpa,
                "total_ects": analysis_result.student_info.total_ects,
            },
            "graduation_status": "Graduated" if analysis_result.is_graduated else "Not Graduated",
            "missing_conditions": analysis_result.missing_conditions
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
