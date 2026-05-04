from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    student_number = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transcripts = relationship("Transcript", back_populates="student")


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    raw_text = Column(String, nullable=False)
    text_hash = Column(String, nullable=True, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="transcripts")
    analysis = relationship("AnalysisResult", back_populates="transcript", uselist=False)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"), nullable=False)
    gpa = Column(Float, nullable=True)
    transcript_total_ects = Column(Integer, nullable=True)
    required_ects = Column(Integer, default=240)
    is_graduated = Column(Boolean, default=False)
    completed_courses = Column(JSON, default=list)
    missing_courses = Column(JSON, default=list)
    missing_conditions = Column(JSON, default=list)
    agent_verdicts = Column(JSON, default=dict)
    report_text = Column(String, nullable=True)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    transcript = relationship("Transcript", back_populates="analysis")
