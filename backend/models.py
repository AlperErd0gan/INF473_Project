from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from database import Base

class StudentTranscript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    gpa = Column(Float)
    total_ects = Column(Integer)
    is_graduated = Column(Boolean, default=False)
    missing_conditions = Column(JSON) # Store list of missing conditions
    raw_text = Column(String) # Store the original text for reference
