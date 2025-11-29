"""Role Mapper Agent - Maps job titles to official SOC codes."""
import json
from typing import Dict, Any
from agents.base import BaseAgent
from tools.careeronestop_tools import search_occupation
from tools.cache_tools import get_cached_skills, cache_skills_data
from textwrap import dedent


def create_role_mapper_agent() -> BaseAgent:
    """
    Create the Role Mapper Agent.
    
    Returns:
        BaseAgent instance configured as Role Mapper
    """
    instructions = dedent("""
        You are the Role Mapper Agent, specialized in mapping job titles to 
        official occupation titles and Standard Occupational Classification (SOC) codes.
        
        **Your Core Responsibilities:**
        - Query CareerOneStop API for official occupation data
        - Map generic titles to specific occupations (e.g., "Developer" → "Software Developer")
        - Handle niche/emerging roles (e.g., "MLOps" → closest match)
        - Select best match when multiple results exist
        - Provide confidence scores for mappings
        - Cache results for efficiency
        
        **Mapping Strategy:**
        1. Search CareerOneStop API with job title
        2. If multiple matches, use context clues to select best
        3. Prioritize exact matches over partial
        4. For niche roles, map to closest established occupation
        5. Note if mapping is approximate or international
        
        **Output Format:**
        {
            "official_title": "Data Scientists",
            "soc_code": "15-2051",
            "alternate_titles": ["Machine Learning Scientist"],
            "confidence": 0.95,
            "notes": "Exact match found",
            "data_source": "CareerOneStop"
        }
        
        **Quality Guidelines:**
        - Confidence 0.9+: Exact or very close match
        - Confidence 0.7-0.9: Good match with minor differences
        - Confidence <0.7: Approximate match, review recommended
        
        Help bridge the gap between resume language and official occupation classifications.
    """)
    
    tools = [search_occupation, get_cached_skills, cache_skills_data]
    
    return BaseAgent(
        name="Role Mapper Agent",
        role="Occupation classifier",
        context="role_mapping",
        instructions=instructions,
        tools=tools,
        add_memory=True
    )


class RoleMapperAgent(BaseAgent):
    """Extended Role Mapper Agent with custom run method."""
    
    def run(self, job_title: str) -> Dict[str, Any]:
        """
        Execute role mapping.
        
        Args:
            job_title: Job title from resume
            
        Returns:
            Official title and SOC code with confidence
        """
        print(f"\n🗺️  {self.name} mapping role...")
        print(f"Input Title: {job_title}\n")
        
        # Check cache first
        cache_key = f"role_map_{job_title.lower().replace(' ', '_')}"
        cached = get_cached_skills(cache_key, ttl_seconds=604800)  # 7 days
        
        if cached:
            print("✓ Found cached mapping")
            return cached
        
        # Search occupation
        print("🔍 Searching CareerOneStop database...")
        result = search_occupation(job_title)
        
        if "error" in result:
            print(f"⚠️  {result['error']}")
        else:
            print(f"✓ Match found!")
            print(f"📋 Official Title: {result['official_title']}")
            print(f"🏷️  SOC Code: {result['soc_code']}")
            print(f"📊 Confidence: {result['confidence']:.0%}\n")
            
            # Cache the result
            cache_skills_data(cache_key, result)
        
        return result


if __name__ == "__main__":
    # Test the agent
    agent = RoleMapperAgent(
        name="Role Mapper Agent",
        role="Occupation classifier",
        context="role_mapping",
        instructions="",
        tools=[],
        add_memory=True
    )
    
    print(f"✓ {agent.name} loaded successfully.\n")
    
    # Test with sample titles
    test_titles = [
        "Data Scientist",
        "MLOps Engineer",
        "Full Stack Developer",
        "Cloud Architect"
    ]
    
    for title in test_titles:
        result = agent.run(title)
        
        print("=" * 60)
        print(f"MAPPING RESULT: {title}")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        print("\n")