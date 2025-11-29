"""Tools for analyzing skills using Gemini LLM."""
import os
import json
from typing import List, Dict, Any
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def analyze_skills_with_gemini(job_descriptions: List[str]) -> str:
    """
    Use Gemini to extract and analyze skills from job descriptions.
    
    Args:
        job_descriptions: List of job description texts
    
    Returns:
        JSON string with extracted skills
    """
    sample = job_descriptions[:10]
    
    prompt = f"""
You are an expert job-analysis system.
Given the following job descriptions, extract skill mentions and output JSON with:

skills: [{{
    "name": "",
    "type": "language|framework|tool|cloud|db|concept",
    "frequency": int,
    "mention_count": int
}}]

Only return valid JSON. DO NOT include narrative text.

Job Descriptions:
{sample}
"""

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        response = client.models.generate_content(
            model='models/gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        return response.text
    
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return '{"skills": []}'


def evaluate_user_skills_with_gemini(
    user_skills: List[str],
    required_skills: List[Dict],
    job_title: str
) -> Dict:
    """
    Evaluate user skills against required skills using Gemini.
    
    Args:
        user_skills: List of user's current skills
        required_skills: List of required skill dicts with name, type, frequency
        job_title: Target job title
    
    Returns:
        Dictionary with skill gaps, matches, and recommendations
    """
    try:
        # Use Gemini 2.0 Flash
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Format skills for prompt
        user_skills_str = ", ".join(user_skills)
        required_skills_str = "\n".join([
            f"- {s['name']} ({s['type']}): {s['frequency']}% of jobs require this"
            for s in required_skills[:15]
        ])
        
        prompt = f"""You are a career advisor analyzing skill gaps for a {job_title} role.

**User's Current Skills:**
{user_skills_str}

**Required Skills for {job_title} (from job market analysis):**
{required_skills_str}

Analyze the skill match and provide:
1. Skills the user already has (matching skills)
2. Critical skill gaps (high-frequency skills the user lacks)
3. Nice-to-have gaps (lower-frequency skills the user lacks)
4. Actionable learning recommendations with priorities

Return ONLY valid JSON in this exact format:
{{
  "match_score": 75,
  "matching_skills": ["Python", "SQL"],
  "critical_gaps": [
    {{"skill": "AWS", "frequency": 72, "priority": "high", "reason": "Required by 72% of jobs"}}
  ],
  "nice_to_have_gaps": [
    {{"skill": "Docker", "frequency": 45, "priority": "medium"}}
  ],
  "recommendations": [
    {{"skill": "AWS", "action": "Complete AWS Solutions Architect course", "timeframe": "2-3 months", "priority": "high"}}
  ],
  "summary": "You have strong foundational skills but need to develop cloud platform expertise..."
}}"""

        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        
        if json_match:
            import json
            result = json.loads(json_match.group(0))
            result["job_title"] = job_title
            result["analysis_method"] = "Gemini 2.0 Flash"
            return result
        else:
            raise ValueError("Could not extract JSON from Gemini response")
            
    except Exception as e:
        print(f"[Gemini Evaluator Error] {e}")
        # Fallback to basic analysis
        return basic_skill_evaluation(user_skills, required_skills, job_title)


def basic_skill_evaluation(
    user_skills: List[str],
    required_skills: List[Dict],
    job_title: str
) -> Dict:
    """
    Fallback basic skill evaluation without LLM.
    
    Args:
        user_skills: User's skills
        required_skills: Required skills
        job_title: Job title
    
    Returns:
        Basic evaluation dict
    """
    # Normalize for comparison
    user_skills_lower = [s.lower() for s in user_skills]
    
    matching = []
    critical_gaps = []
    nice_gaps = []
    
    for req_skill in required_skills:
        skill_name = req_skill['name'].lower()
        
        if skill_name in user_skills_lower:
            matching.append(req_skill['name'])
        elif req_skill['frequency'] >= 50:
            critical_gaps.append({
                "skill": req_skill['name'],
                "frequency": req_skill['frequency'],
                "priority": "high",
                "reason": f"Required by {req_skill['frequency']}% of jobs"
            })
        else:
            nice_gaps.append({
                "skill": req_skill['name'],
                "frequency": req_skill['frequency'],
                "priority": "medium"
            })
    
    match_score = int((len(matching) / len(required_skills)) * 100) if required_skills else 0
    
    return {
        "match_score": match_score,
        "matching_skills": matching,
        "critical_gaps": critical_gaps[:5],
        "nice_to_have_gaps": nice_gaps[:5],
        "recommendations": [
            {
                "skill": gap["skill"],
                "action": f"Learn {gap['skill']} fundamentals",
                "timeframe": "1-2 months",
                "priority": gap["priority"]
            }
            for gap in critical_gaps[:3]
        ],
        "summary": f"You match {match_score}% of required skills for {job_title}. Focus on critical gaps first.",
        "job_title": job_title,
        "analysis_method": "Basic keyword matching (LLM unavailable)"
    }