import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import Student, Transcript, AnalysisResult
from agent import run_analysis_pipeline

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GSU Academic Advisor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranscriptUpload(BaseModel):
    text: str


@app.get("/")
def read_root():
    return {"message": "GSU Academic Advisor API"}


@app.post("/transcripts/upload")
def upload_transcript(body: TranscriptUpload, db: Session = Depends(get_db)):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty")

    transcript = Transcript(raw_text=body.text.strip())
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return {"transcript_id": transcript.id}


@app.post("/analysis/analyze/{transcript_id}")
def analyze_transcript(transcript_id: int, db: Session = Depends(get_db)):
    transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    existing = db.query(AnalysisResult).filter(
        AnalysisResult.transcript_id == transcript_id
    ).first()
    if existing:
        return _format_analysis(existing, transcript_id)

    try:
        result = run_analysis_pipeline(transcript.raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

    if result.get("student_name") or result.get("student_number"):
        student = Student(
            name=result.get("student_name"),
            student_number=result.get("student_number"),
        )
        db.add(student)
        db.flush()
        transcript.student_id = student.id

    analysis = AnalysisResult(
        transcript_id=transcript_id,
        gpa=result.get("gpa"),
        total_ects=result.get("total_ects"),
        is_graduated=result.get("is_graduated", False),
        completed_courses=result.get("completed_mandatory_courses", []),
        missing_courses=result.get("missing_courses", []),
        missing_conditions=result.get("missing_conditions", []),
        report_text=result.get("report_text"),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return _format_analysis(analysis, transcript_id)


@app.get("/analysis/history")
def get_history(db: Session = Depends(get_db)):
    results = (
        db.query(AnalysisResult, Transcript)
        .join(Transcript, AnalysisResult.transcript_id == Transcript.id)
        .outerjoin(Student, Transcript.student_id == Student.id)
        .order_by(AnalysisResult.analyzed_at.desc())
        .limit(50)
        .all()
    )

    history = []
    for analysis, transcript in results:
        student = transcript.student
        history.append({
            "analysis_id": analysis.id,
            "transcript_id": transcript.id,
            "student_name": student.name if student else None,
            "student_number": student.student_number if student else None,
            "gpa": analysis.gpa,
            "total_ects": analysis.total_ects,
            "is_graduated": analysis.is_graduated,
            "analyzed_at": analysis.analyzed_at.isoformat() if analysis.analyzed_at else None,
        })
    return history


@app.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return _format_analysis(analysis, analysis.transcript_id)


@app.delete("/analysis/{analysis_id}")
def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    transcript_id = analysis.transcript_id
    db.delete(analysis)
    
    transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if transcript:
        db.delete(transcript)
        
    db.commit()
    return {"message": "Analysis deleted"}


def _format_analysis(analysis: AnalysisResult, transcript_id: int) -> dict:
    return {
        "analysis_id": analysis.id,
        "transcript_id": transcript_id,
        "gpa": analysis.gpa,
        "total_ects": analysis.total_ects,
        "is_graduated": analysis.is_graduated,
        "completed_courses": analysis.completed_courses or [],
        "missing_courses": analysis.missing_courses or [],
        "missing_conditions": analysis.missing_conditions or [],
        "report_text": analysis.report_text,
        "analyzed_at": analysis.analyzed_at.isoformat() if analysis.analyzed_at else None,
    }
