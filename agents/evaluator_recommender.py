# agents/evaluator_recommender_agent.py
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.append(str(Path(__file__).parent.parent))


import os
import json
from typing import List, Dict, Any

# local tool to call Gemini (should be the file you just updated)
from tools.llm_analysis import evaluate_user_skills_with_gemini

# helper: safe json parse
def safe_json_parse(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        # try minor cleanup
        cleaned = text.strip().strip("```").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return None

# Rules-based fallback evaluator
def rules_evaluator(
    resume_skills: List[Dict[str, Any]],
    short_term_skills: List[Dict[str, Any]],
    long_term_forecast: Dict[str, Any],
) -> Dict[str, Any]:
    resume_names = {s.get("name", "").lower(): s for s in resume_skills}
    top_skills = short_term_skills[:20] if short_term_skills else []
    role_outlook = long_term_forecast.get("category", "Unknown")

    gap_analysis = []
    for idx, s in enumerate(top_skills[:20]):
        name = s.get("name")
        if not name:
            continue
        lname = name.lower()
        market_rank = idx + 1
        if lname in resume_names:
            continue
        # priority rules
        if role_outlook.lower().startswith("high") or "future" in role_outlook.lower():
            if market_rank <= 10:
                pr = "High"
            else:
                pr = "Medium" if market_rank <= 20 else "Low"
        elif role_outlook.lower().startswith("stable"):
            pr = "Medium" if market_rank <= 10 else "Low"
        else:
            pr = "Low"
        gap_analysis.append({
            "skill": name,
            "current_level": None,
            "market_rank": market_rank,
            "priority": pr,
            "reasoning": f"Rank #{market_rank} in short-term demand; role outlook: {role_outlook}."
        })

    # pick top 3-5 recommendations
    sorted_gaps = sorted(gap_analysis, key=lambda x: ({"High": 1, "Medium": 2, "Low": 3}[x["priority"]], x["market_rank"]))
    recommended_learning_path = [g["skill"] for g in sorted_gaps[:5]]

    estimated_time_weeks = 12
    confidence = 0.75 if gap_analysis else 0.4
    return {
        "role_outlook": role_outlook,
        "gap_analysis": gap_analysis,
        "recommended_learning_path": recommended_learning_path,
        "estimated_time_weeks": estimated_time_weeks,
        "confidence": round(confidence, 2)
    }

# Agent class
class EvaluatorRecommenderAgent:
    def __init__(self):
        self.name = "evaluator_recommender_agent"
        self.description = "Compares resume skills vs market skills and recommends an upskilling path"

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Payload expected keys:
          - resume_skills: List[dict]  (each dict: {name, type, proficiency, ...})
          - short_term_skills: List[dict] (each dict: {name, type, frequency, mention_count})
          - long_term_forecast: dict (contains 'category' key)
        """
        # Basic validation / defaults
        resume_skills = payload.get("resume_skills", [])
        short_term_skills = payload.get("short_term_skills", [])
        long_term_forecast = payload.get("long_term_forecast", {})

        # Try LLM-based refinement first (preferred)
        try:
            llm_response = evaluate_user_skills_with_gemini(
                [s.get("name") for s in resume_skills],
                short_term_skills,
                long_term_forecast.get("category", "")
            )

            # If the tool returns text, try to parse JSON
            if isinstance(llm_response, str):
                parsed = safe_json_parse(llm_response)
                if isinstance(parsed, dict):
                    return parsed
                # if LLM returned string but not valid JSON, fallback to rules
            elif isinstance(llm_response, dict):
                return llm_response

        except Exception as e:
            # log and fallback
            print(f"[Evaluator] LLM call failed: {e}")

        # Fallback deterministic rules engine
        fallback = rules_evaluator(resume_skills, short_term_skills, long_term_forecast)
        return fallback

# Exported agent instance
evaluator_recommender_agent = EvaluatorRecommenderAgent()

# Quick test harness when run directly
if __name__ == "__main__":
    print("=== Evaluator & Recommender Agent — Test Mode ===")
    sample_payload = {
        "resume_skills": [
            {"name": "Python"}, {"name": "Docker"}, {"name": "SQL"}
        ],
        "short_term_skills": [
            {"name": "Python", "type": "language", "frequency": 95, "mention_count": 95},
            {"name": "AWS", "type": "cloud", "frequency": 80, "mention_count": 80},
            {"name": "Kubernetes", "type": "tool", "frequency": 70, "mention_count": 70},
            {"name": "Docker", "type": "tool", "frequency": 65, "mention_count": 65},
            {"name": "CI/CD", "type": "tool", "frequency": 60, "mention_count": 60},
        ],
        "long_term_forecast": {
            "category": "High growth (Future-safe)"
        }
    }

    out = evaluator_recommender_agent.run(sample_payload)
    print(json.dumps(out, indent=2))
