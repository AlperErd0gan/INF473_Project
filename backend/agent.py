import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Ensure GEMINI_API_KEY is set in your environment variables
client = genai.Client()

class StudentInfo(BaseModel):
    gpa: float = Field(description="The student's Cumulative Grade Point Average (CGPA)")
    total_ects: int = Field(description="The total accumulated ECTS credits by the student")

class TranscriptAnalysisResult(BaseModel):
    student_info: StudentInfo
    is_graduated: bool = Field(description="True if the student meets all graduation requirements, False otherwise")
    missing_conditions: list[str] = Field(description="List of strings explaining which graduation conditions are not met. Empty if graduated.")

def analyze_transcript_with_gemini(transcript_text: str) -> TranscriptAnalysisResult:
    # This is a sample prompt. We inject the GSU rules here.
    system_instruction = """
    You are an expert academic advisor for the Computer Engineering Department at Galatasaray University (GSU).
    Your task is to analyze unstructured student transcript text and determine if the student meets the graduation requirements.
    
    GSU Computer Engineering Graduation Requirements:
    1. The student must have a minimum GPA of 2.00.
    2. The student must have accumulated at least 240 ECTS credits.
    3. The student must have taken and passed all mandatory courses in the 8-semester curriculum.
    
    Analyze the following transcript text. Extract the GPA and total ECTS. Check if the rules are satisfied.
    Return your findings in a structured format.
    """

    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=transcript_text,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=TranscriptAnalysisResult,
            temperature=0.0
        ),
    )
    
    # The response.text is a JSON string matching the Pydantic schema
    return TranscriptAnalysisResult.model_validate_json(response.text)
