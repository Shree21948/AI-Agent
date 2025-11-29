"""Long-Term Forecast Agent specialized in 10-year job growth projections."""
import json
from agents.base import BaseAgent
from tools.bls_tools import fetch_job_projections
#from tools.datausa_tools import fetch_job_projections
from tools.cache_tools import get_cached_skills, cache_skills_data
from textwrap import dedent


def create_long_term_forecast_agent() -> BaseAgent:
    """
    Create the Long-Term Forecast Agent for 10-year job growth projections.
    
    Returns:
        BaseAgent instance configured as Long-Term Forecast Agent
    """
    instructions = dedent("""
        You are the Long-Term Forecast Agent, specialized in analyzing 10-year job growth 
        projections using Bureau of Labor Statistics (BLS) data via Data USA API.
        
        **Your Core Responsibilities:**
        - Query Data USA API for occupation growth projections by SOC code
        - Extract 10-year growth percentages and absolute job changes
        - Calculate median wages and workforce size
        - Categorize occupations: Future-safe (≥10% growth), Stable (0-10%), Declining (<0%)
        - Provide confidence scores based on data quality
        - Cache results for 7 days (projections change infrequently)
        
        **Your Analysis Process:**
        1. Receive SOC code and official job title from Role Mapper
        2. Check cache (7-day TTL) for existing projections
        3. Query Data USA API for historical and projected workforce data
        4. Calculate growth percentage: ((new - old) / old) * 100
        5. Determine absolute job change (new workforce - old workforce)
        6. Categorize occupation stability
        7. Return structured JSON output
        
        **Output Format:**
        {
            "soc_code": "15-1252.00",
            "job_title": "Software Developers",
            "growth_percent": 21.5,
            "absolute_job_change": 409500,
            "current_workforce": 1847900,
            "median_wage": 120730,
            "category": "Future-safe",
            "projection_years": "2021-2031",
            "data_source": "Data USA (BLS-derived)",
            "confidence": 0.9,
            "cache_ttl_seconds": 604800
        }
        
        **Category Definitions:**
        - **Future-safe**: ≥10% growth over 10 years (strong demand, invest heavily)
        - **Stable**: 0-10% growth (moderate demand, maintain skills)
        - **Declining**: <0% growth (shrinking field, pivot recommended)
        
        **Available Tools:**
        - Data USA API for BLS-derived projections
        - Caching system (7-day TTL for performance)
        - Growth categorization engine
        
        **Communication Style:**
        - Forward-looking and analytical
        - Use future-focused emojis (📈, 🔮, 💼, 🎯, ⏳)
        - Provide clear growth metrics
        - Highlight industry trends
        - Note confidence levels
        
        **Quality Guidelines:**
        - Minimum 5 years of historical data for reliable projections
        - Confidence score increases with data completeness
        - Flag low-confidence results (<0.7)
        - Cache for 7 days (BLS updates quarterly/annually)
        - Distinguish between short-term fluctuations vs. long-term trends
        
        Help users understand long-term career viability and make informed decisions 
        about skill investment and career planning.
    """)
    
    tools = [
        fetch_job_projections,
        get_cached_skills,
        cache_skills_data
    ]
    
    return BaseAgent(
        name="Long-Term Forecast Agent",
        role="10-year job growth analyzer",
        context="growth_projections",
        instructions=instructions,
        tools=tools,
        add_memory=True
    )


class LongTermForecastAgent(BaseAgent):
    """Extended Long-Term Forecast Agent with custom run method."""
    
    def run(self, soc_code: str, job_title: str) -> dict:
        """
        Execute long-term forecast analysis.
        
        Args:
            soc_code: Standard Occupational Classification code
            job_title: Official job title
            
        Returns:
            Dictionary with growth projections
        """
        print(f"\n🔮 {self.name} executing forecast...")
        print(f"SOC Code: {soc_code}")
        print(f"Job Title: {job_title}\n")
        
        # Check cache first (7-day TTL)
        cache_key = f"forecast_{soc_code}"
        cached = get_cached_skills(cache_key, ttl_seconds=604800)
        if cached:
            print("✓ Found cached projections (valid for 7 days)")
            return cached
        
        # Fetch projections from Data USA
        print("📊 Fetching 10-year growth projections from BLS...")
        result = fetch_job_projections(soc_code, job_title)
        
        if "error" in result:
            print(f"⚠️  {result['error']}")
            return result
        
        # Add cache TTL
        result["cache_ttl_seconds"] = 604800
        
        # Cache the result
        cache_skills_data(cache_key, result)
        
        print(f"✓ Analysis complete!")
        print(f"📈 Growth: {result['growth_percent']}%")
        print(f"🏷️  Category: {result['category']}\n")
        
        return result


if __name__ == "__main__":
    # Test the agent
    agent = LongTermForecastAgent(
        name="Long-Term Forecast Agent",
        role="10-year job growth analyzer",
        context="growth_projections",
        instructions="",
        tools=[],
        add_memory=True
    )
    
    print(f"✓ {agent.name} loaded successfully.\n")
    
    # Test with Data Scientist role
    test_soc = "15-2051"
    test_title = "Data Scientists"
    
    result = agent.run(test_soc, test_title)
    
    print("=" * 60)
    print("📊 FORECAST RESULTS")
    print("=" * 60)
    print(json.dumps(result, indent=2))