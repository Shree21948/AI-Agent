"""Resume Extractor Agent - Orchestrates resume parsing."""
import json
import os
from typing import Dict, Any
from agents.base import BaseAgent
from tools.resume_tools import extract_resume
from textwrap import dedent


def create_resume_extractor_agent() -> BaseAgent:
    """
    Create the Resume Extractor Agent.
    
    Returns:
        BaseAgent instance configured as Resume Extractor
    """
    instructions = dedent("""
        You are the Resume Extractor Agent, specialized in parsing resumes and 
        extracting structured information using Gemini's multimodal capabilities.
        
        **Your Core Responsibilities:**
        - Parse PDF, DOCX, and TXT resume files
        - Extract candidate information, work history, skills, projects, and education
        - Normalize skill names (e.g., "ML" → "Machine Learning")
        - Estimate dates when only partial information is available
        - Return strictly valid JSON matching the schema
        - Handle missing fields gracefully (null or empty arrays)
        
        **Extraction Rules:**
        - Experience level: Calculate from work history years
        - Skills: Classify into language/framework/library/tool/cloud/db/concept
        - Projects: Extract tech stack and outcomes
        - Confidence: Rate parsing quality 0.0-1.0
        
        **Privacy:**
        - Email is optional and can be redacted
        - No caching of resume data (contains PII)
        
        Help users understand their current skill profile accurately.
    """)
    
    tools = [extract_resume]
    
    return BaseAgent(
        name="Resume Extractor Agent",
        role="Resume parser",
        context="resume_extraction",
        instructions=instructions,
        tools=tools,
        add_memory=False
    )


class ResumeExtractorAgent(BaseAgent):
    """Extended Resume Extractor Agent with custom run method."""
    
    def run(self, file_path: str) -> Dict[str, Any]:
        """
        Execute resume extraction.
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Structured resume data
        """
        print(f"\n📄 {self.name} extracting resume...")
        print(f"File: {file_path}\n")
        
        result = extract_resume(file_path)
        
        if "error" in result:
            print(f"❌ Extraction failed: {result['error']}")
            return result
        
        print("✓ Extraction complete!")
        print(f"📊 Found {len(result.get('skills', []))} skills")
        print(f"💼 Found {len(result.get('roles_detected', []))} roles")
        print(f"🎓 Found {len(result.get('education', []))} education entries\n")
        
        return result


if __name__ == "__main__":
    # Test the agent
    agent = ResumeExtractorAgent(
        name="Resume Extractor Agent",
        role="Resume parser",
        context="resume_extraction",
        instructions="",
        tools=[],
        add_memory=False
    )
    
    print(f"✓ {agent.name} loaded successfully.\n")
    
    # Test with a sample file
    test_file = input("Enter path to your resume file (PDF/TXT): ").strip()
    
    if test_file and os.path.exists(test_file):
        result = agent.run(test_file)
        
        print("\n" + "=" * 60)
        print("📄 EXTRACTED DATA")
        print("=" * 60)
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ File not found or no path provided")
        print("\n💡 To test, run again and provide a valid resume file path.")