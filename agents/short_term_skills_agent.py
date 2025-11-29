"""Short-term skills agent specialized in analyzing current job market trends."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
from agents.base import BaseAgent
from tools.adzuna_tools import fetch_job_postings, search_jobs_by_soc
import json
from agents.base import BaseAgent
from tools.adzuna_tools import fetch_job_postings, search_jobs_by_soc
from tools.skill_extraction import extract_skills_from_descriptions, classify_skill_type
from tools.cache_tools import get_cached_skills, cache_skills_data
from tools.llm_analysis import analyze_skills_with_gemini
from textwrap import dedent


def create_short_term_skills_agent():
    """
    Create the Short-Term Skills Agent specialized in analyzing current job market data.
    
    Returns:
        BaseAgent instance configured as Short-Term Skills Agent
    """
    instructions = dedent("""
        You are the Short-Term Skills Agent, a specialized AI assistant focused on analyzing
        real-time job market data to identify trending technical skills for specific roles.
        
        **Your Core Responsibilities:**
        - Query the Adzuna API for recent job postings (last 90 days)
        - Collect 100+ job postings for comprehensive analysis
        - Extract skill mentions from job descriptions
        - Rank skills by frequency and relevance
        - Classify skills into categories: language, framework, tool, cloud, database, concept
        - Provide confidence scores based on data quality
        - Cache results for 24 hours to optimize performance
        
        Help users understand what skills are currently in-demand for their target roles.
    """)
    
    tools = [
        fetch_job_postings,
        search_jobs_by_soc,
        extract_skills_from_descriptions,
        classify_skill_type,
        analyze_skills_with_gemini,
        get_cached_skills,
        cache_skills_data
    ]
    
    return BaseAgent(
        name="Short-Term Skills Agent",
        role="Job market skills trend analyzer",
        context="skills_analysis",
        instructions=instructions,
        tools=tools,
        add_memory=True
    )


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 SHORT-TERM SKILLS AGENT - TEST MODE")
    print("=" * 60)
    
    try:
        # Create the agent
        print("\n📦 Creating agent...")
        agent = create_short_term_skills_agent()
        print(f"✓ {agent.name} loaded successfully!")
        print(f"✓ Role: {agent.role}")
        print(f"✓ Context: {agent.context}")
        
        print("\n✅ Agent ready to analyze job market trends!")
        print("=" * 60)
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nMissing dependencies or files:")
        print("  - Check agents/base.py exists")
        print("  - Check tools/ directory structure")
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()