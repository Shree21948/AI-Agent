"""Base agent class for all specialized agents."""
from typing import List, Callable, Any, Optional
import json


class BaseAgent:
    """Base class for all agents in the system."""
    
    def __init__(
        self, 
        name: str, 
        role: str = "",
        context: str = "",
        instructions: str = "", 
        tools: Optional[List[Callable]] = None,
        add_memory: bool = False
    ):
        self.name = name
        self.role = role
        self.context = context
        self.instructions = instructions
        self.tools = tools or []
        self.add_memory = add_memory
        self.memory = [] if add_memory else None
    
    def run(self, query: str) -> dict:
        """
        Execute the agent's main functionality.
        
        Args:
            query: User query or task description
            
        Returns:
            Dictionary with analysis results
        """
        print(f"\n🤖 {self.name} executing task...")
        print(f"Query: {query}\n")
        
        # Parse query to extract role
        role = self._extract_role_from_query(query)
        
        # Check cache first
        from tools.cache_tools import get_cached_skills
        cached = get_cached_skills(role)
        if cached:
            print("✓ Found cached results (valid for 24h)")
            return cached
        
        # Fetch job postings
        print("📥 Fetching job postings from Adzuna...")
        from tools.adzuna_tools import fetch_job_postings
        job_descriptions = fetch_job_postings(role, max_results=150)
        print(f"✓ Collected {len(job_descriptions)} job descriptions\n")
        
        if not job_descriptions:
            return {
                "error": "No job postings found",
                "role": role,
                "confidence": 0.0
            }
        
        # Extract skills using Gemini
        print("🔍 Analyzing skills with Gemini AI...")
        from tools.llm_analysis import analyze_skills_with_gemini
        skills_json = analyze_skills_with_gemini(job_descriptions)
        
        try:
            skills_data = json.loads(skills_json)
        except json.JSONDecodeError:
            skills_data = {"skills": []}
        
        # Build result
        result = {
            "role": role,
            "top_skills": skills_data.get("skills", [])[:20],
            "data_source": f"Adzuna (90d, {len(job_descriptions)} jobs)",
            "confidence": self._calculate_confidence(len(job_descriptions)),
            "cache_ttl_seconds": 86400
        }
        
        # Cache the result
        from tools.cache_tools import cache_skills_data
        cache_skills_data(role, result)
        
        print("✓ Analysis complete!\n")
        return result
    
    def _extract_role_from_query(self, query: str) -> str:
        """Extract role name from query string."""
        # Simple extraction - looks for "for <role>" pattern
        if " for " in query.lower():
            parts = query.lower().split(" for ")
            if len(parts) > 1:
                return parts[1].strip().title()
        
        # Fallback: assume query is the role itself
        return query.strip().title()
    
    def _calculate_confidence(self, num_jobs: int) -> float:
        """Calculate confidence score based on sample size."""
        if num_jobs >= 100:
            return 0.95
        elif num_jobs >= 50:
            return 0.85
        elif num_jobs >= 25:
            return 0.70
        else:
            return 0.50
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', role='{self.role}')>"