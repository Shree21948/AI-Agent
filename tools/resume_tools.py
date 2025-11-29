"""Tools for extracting structured data from resume files."""
import os
from typing import Dict, Any
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


RESUME_EXTRACTOR_PROMPT = """
You are a resume extraction expert. Parse the provided resume and extract:
1. Candidate info (name, email, location, experience level)
2. Work history (roles, companies, timelines, responsibilities)
3. Skills (language, framework, tool, cloud, db—with proficiency and last-used year)
4. Projects (name, tech stack, outcomes, links)
5. Education (degree, major, institution, graduation year)

Rules:
· If a field is missing, return null or empty array.
· Normalize skill names (e.g., "ML" → "Machine Learning", "Py" → "Python").
· Extract exact years; estimate if only months given.
· Return strictly valid JSON per the provided schema.
If validation fails, repair and resubmit.

**Output Schema:**
{
  "candidate": {
    "name": "string",
    "email": "string (optional, redactable)",
    "location": "string (city, country)",
    "experience_level": "Student|Junior|Mid|Senior"
  },
  "roles_detected": [
    {
      "title": "string",
      "company": "string",
      "seniority": "string",
      "start_year": "integer",
      "end_year": "integer",
      "responsibilities": ["string"]
    }
  ],
  "skills": [
    {
      "name": "string",
      "type": "language|framework|library|tool|cloud|db|concept",
      "proficiency": "Beginner|Intermediate|Advanced|Expert",
      "last_used_year": "integer"
    }
  ],
  "projects": [
    {
      "name": "string",
      "description": "string",
      "tech_stack": ["string"],
      "outcomes": ["string"],
      "links": ["string (URL)"]
    }
  ],
  "education": [
    {
      "degree": "string",
      "major": "string",
      "institution": "string",
      "grad_year": "integer"
    }
  ],
  "meta": {
    "parsing_confidence": 0.0,
    "pages_parsed": 0,
    "redactions_applied": [],
    "source_file": "string"
  }
}
"""


def extract_from_pdf(file_path: str) -> Dict[str, Any]:
    """
    Extract structured data from PDF resume.
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        Structured resume data
    """
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        # Upload file to Gemini
        uploaded_file = client.files.upload(path=file_path)
        
        # Extract with Gemini
        response = client.models.generate_content(
            model='models/gemini-1.5-pro',
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(
                            file_uri=uploaded_file.uri,
                            mime_type=uploaded_file.mime_type
                        ),
                        types.Part.from_text(RESUME_EXTRACTOR_PROMPT)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2048,
                response_mime_type="application/json"
            )
        )
        
        # Parse response
        result = response.text
        import json
        parsed = json.loads(result)
        
        # Add metadata
        if "meta" not in parsed:
            parsed["meta"] = {}
        
        parsed["meta"]["source_file"] = os.path.basename(file_path)
        
        return parsed
    
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return {
            "error": str(e),
            "source_file": file_path
        }


def extract_from_text(file_path: str) -> Dict[str, Any]:
    """
    Extract structured data from text resume.
    
    Args:
        file_path: Path to text file
    
    Returns:
        Structured resume data
    """
    try:
        # Read text file
        with open(file_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
        
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        prompt = f"{RESUME_EXTRACTOR_PROMPT}\n\nRESUME TEXT:\n{resume_text}"
        
        response = client.models.generate_content(
            model='models/gemini-1.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2048,
                response_mime_type="application/json"
            )
        )
        
        import json
        parsed = json.loads(response.text)
        
        if "meta" not in parsed:
            parsed["meta"] = {}
        
        parsed["meta"]["source_file"] = os.path.basename(file_path)
        
        return parsed
    
    except Exception as e:
        print(f"Error extracting text: {e}")
        return {
            "error": str(e),
            "source_file": file_path
        }


def extract_resume(file_path: str) -> Dict[str, Any]:
    """
    Main function to extract resume regardless of format.
    
    Args:
        file_path: Path to resume file
    
    Returns:
        Structured resume data
    """
    if not os.path.exists(file_path):
        return {"error": "File not found", "file_path": file_path}
    
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.pdf':
        return extract_from_pdf(file_path)
    elif file_ext in ['.txt', '.docx']:
        return extract_from_text(file_path)
    else:
        return {
            "error": f"Unsupported file format: {file_ext}",
            "supported_formats": [".pdf", ".txt", ".docx"]
        }