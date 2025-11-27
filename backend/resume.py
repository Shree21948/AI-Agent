# backend/resume.py
from dotenv import load_dotenv
import pathlib
from pathlib import Path
from google import genai
from google.genai import types

import os
import json
from typing import List, Optional

from pdfminer.high_level import extract_text as extract_pdf #extract_text is a function rename to extract_pdf
from docx import Document

from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini

from google.genai import types


# --------------------------
# LOAD .env AND API KEY
# --------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH)

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError(
        f"GOOGLE_API_KEY not found. Make sure your .env file contains:\n"
        f"GOOGLE_API_KEY=your_real_key"
    )


# --------------------------
# 1. File Reader
# --------------------------

def read_resume(file_path: str) -> str:
    """
    Reads text from a resume file.
    Supports: .pdf, .docx, .txt (or any plain text file).
    """
    file_path = file_path.strip()

    if file_path.lower().endswith(".pdf"):
        return extract_pdf(file_path)

    if file_path.lower().endswith(".docx"):
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    # default: treat as plain text
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# --------------------------
# 2. Structured Output Schema (Pydantic)
# --------------------------

class ResumeOutput(BaseModel):
    roles: List[str] = Field(
        default_factory=list,
        description="List of job titles inferred from the resume, most recent first.",
    )
    skills: List[str] = Field(
        default_factory=list,
        description="List of key skills in lowercase (technical + relevant soft skills).",
    )
    experience_years: Optional[int] = Field(
        default=None,
        description="Total years of relevant experience, or null if unclear.",
    )
    education_level: Optional[str] = Field(
        default=None,
        description="Highest education level (e.g., Bachelor's, Master's, PhD), or null.",
    )


# --------------------------
# 3. LLM Prompt (simple, because schema does the structure work)
# --------------------------

RESUME_PROMPT = """
You are a resume parsing agent for a career guidance system.

You will be given the full text of a candidate's resume.
Your job is to understand their background and fill in this structured output:

- roles: list of job titles inferred from the resume (most recent first)
- skills: list of skills in lowercase (technical + clear soft skills, no duplicates)
- experience_years: integer total years of experience, or null if unsure
- education_level: highest education level, or null if not clear

Focus on being accurate and concise. Do not invent details that are not supported by the resume.
"""


# --------------------------
# 4. ADK Agent with Structured Output
# --------------------------

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

resume_agent = Agent(
    name="resume_extractor_agent",
    description="Extracts structured job roles, skills, and experience from resume text.",
    instruction=RESUME_PROMPT,
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
    ),
    # ⭐ THIS is the important part: ADK enforces this schema
    output_schema=ResumeOutput,
)


# --------------------------
# 5. Core Runner
# --------------------------

def run_resume_agent(file_path: str) -> dict:
    """
    Full pipeline:
    - read resume file
    - send resume text to the Gemini model
    - parse the structured JSON response
    - return a Python dict you can pass to other agents
    """
    resume_text = read_resume(file_path)

    # Create a GenAI client with your API key
    client = genai.Client(api_key=API_KEY)

    # Ask Gemini to return JSON shaped like ResumeOutput
    config = types.GenerateContentConfig(
        system_instruction=RESUME_PROMPT.strip(),
        response_mime_type="application/json",
        response_schema=ResumeOutput,  # Pydantic schema
        temperature=0.1,
    )

    # Send the resume text as the user message
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=resume_text,
        config=config,
    )

    # With response_schema, this should already be a ResumeOutput instance
    parsed = response.parsed

    if isinstance(parsed, ResumeOutput):
        data = parsed.model_dump()
    else:
        # Fallback: try parsing the raw text as JSON if something unexpected happens
        data = json.loads(response.text)

    # Ensure consistent structure and add raw_text for downstream agents
    data["raw_text"] = resume_text
    return data

