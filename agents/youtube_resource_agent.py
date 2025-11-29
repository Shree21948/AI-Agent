"""YouTube Resource Agent specialized in finding vetted learning resources."""
import json
from typing import List, Dict, Any
from agents.base import BaseAgent
from tools.youtube_tools import search_youtube_resources
from tools.cache_tools import get_cached_skills, cache_skills_data
from textwrap import dedent


def create_youtube_resource_agent() -> BaseAgent:
    """
    Create the YouTube Resource Agent for finding learning resources.
    
    Returns:
        BaseAgent instance configured as YouTube Resource Agent
    """
    instructions = dedent("""
        You are the YouTube Resource Agent, specialized in finding high-quality 
        learning resources from trusted educational channels on YouTube.
        
        **Your Core Responsibilities:**
        - Search YouTube Data API v3 for skill-specific tutorials
        - Focus on trusted channels: freeCodeCamp, Google Cloud Tech, CS50, MIT OCW, Coursera
        - Filter by currency (<5 years old), popularity (>100k views), and relevance
        - Match difficulty level to user experience (Student/Junior/Mid/Senior)
        - Prefer hands-on projects over pure theory
        - Return top 2-3 resources per skill with reasoning
        - Cache results for 7 days
        
        **Your Search Process:**
        1. Receive prioritized list of missing skills and user experience level
        2. For each skill, search across trusted channels
        3. Extract: title, channel, duration, view count, upload date
        4. Filter by quality criteria (currency, popularity, relevance)
        5. Rate by difficulty and match to user level
        6. Generate recommendation reasoning
        7. Return top 2-3 resources per skill
        
        **Output Format:**
        {
            "skill": "Kubernetes",
            "user_level": "Junior",
            "resources": [
                {
                    "title": "Kubernetes Tutorial for Beginners",
                    "channel": "freeCodeCamp",
                    "url": "https://www.youtube.com/watch?v=...",
                    "duration_minutes": 180,
                    "difficulty": "Beginner",
                    "views": 500000,
                    "upload_date": "2024-01-15",
                    "recommendation_reason": "Hands-on tutorial; 3 hours; perfect for beginners"
                }
            ],
            "cache_ttl_seconds": 604800
        }
        
        **Quality Criteria:**
        - **Currency**: Prefer videos <5 years old (technology changes fast)
        - **Popularity**: Prefer >100k views (quality signal)
        - **Type**: Prefer hands-on projects over pure theory
        - **Subtitles**: Include videos with captions when available
        - **Completeness**: Prefer comprehensive tutorials over quick tips
        
        **Difficulty Matching:**
        - **Student/Junior**: Beginner tutorials, crash courses, 101s
        - **Mid**: Intermediate tutorials, "beyond basics" content
        - **Senior**: Advanced deep dives, expert-level content
        
        **Communication Style:**
        - Educational and supportive
        - Use learning emojis (📚, 🎓, 🎥, 📺, 🔖)
        - Highlight hands-on vs. theory-focused content
        - Note video length and time commitment
        - Explain why each resource is recommended
        
        Help users find the best learning resources matched to their experience level 
        and learning style.
    """)
    
    tools = [
        search_youtube_resources,
        get_cached_skills,
        cache_skills_data
    ]
    
    return BaseAgent(
        name="YouTube Resource Agent",
        role="Learning resource curator",
        context="resource_discovery",
        instructions=instructions,
        tools=tools,
        add_memory=True
    )


class YouTubeResourceAgent(BaseAgent):
    """Extended YouTube Resource Agent with custom run method."""
    
    def run(self, missing_skills: List[str], user_level: str = "Junior") -> Dict[str, Any]:
        """
        Execute resource discovery for missing skills.
        
        Args:
            missing_skills: List of skills the user needs to learn
            user_level: User experience level (Student|Junior|Mid|Senior)
            
        Returns:
            Dictionary with learning resources for each skill
        """
        print(f"\n📚 {self.name} finding learning resources...")
        print(f"Missing Skills: {', '.join(missing_skills[:5])}")
        print(f"User Level: {user_level}\n")
        
        results = {}
        
        for skill in missing_skills[:5]:  # Limit to top 5 skills
            print(f"🔍 Searching resources for: {skill}...")
            
            # Check cache first (7-day TTL)
            cache_key = f"youtube_{skill}_{user_level}"
            cached = get_cached_skills(cache_key, ttl_seconds=604800)
            
            if cached:
                print(f"  ✓ Found cached resources")
                results[skill] = cached
                continue
            
            # Search YouTube
            resources = search_youtube_resources(skill, user_level, max_results=3)
            
            if resources and "error" not in resources[0]:
                result = {
                    "skill": skill,
                    "user_level": user_level,
                    "resources": resources,
                    "cache_ttl_seconds": 604800
                }
                
                # Cache the result
                cache_skills_data(cache_key, result)
                results[skill] = result
                
                print(f"  ✓ Found {len(resources)} resources")
            else:
                print(f"  ⚠️  No resources found")
                results[skill] = {
                    "skill": skill,
                    "user_level": user_level,
                    "resources": [],
                    "error": "No suitable resources found"
                }
        
        print("\n✓ Resource discovery complete!\n")
        return results


if __name__ == "__main__":
    # Test the agent
    agent = YouTubeResourceAgent(
        name="YouTube Resource Agent",
        role="Learning resource curator",
        context="resource_discovery",
        instructions="",
        tools=[],
        add_memory=True
    )
    
    print(f"✓ {agent.name} loaded successfully.\n")
    
    # Test with sample skills
    test_skills = ["Kubernetes", "AWS", "Machine Learning"]
    test_level = "Junior"
    
    result = agent.run(test_skills, test_level)
    
    print("=" * 60)
    print("📚 LEARNING RESOURCES")
    print("=" * 60)
    print(json.dumps(result, indent=2))