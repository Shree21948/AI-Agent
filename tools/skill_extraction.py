"""Tools for extracting and classifying skills from job descriptions."""
from typing import List, Dict, Any


def extract_skills_from_descriptions(descriptions: List[str]) -> List[Dict[str, Any]]:
    """
    Extract skills from job descriptions.
    
    Args:
        descriptions: List of job description texts
    
    Returns:
        List of extracted skills with metadata
    """
    # This will be enhanced by LLM analysis
    # For now, return empty list - will be filled by llm_analysis
    return []


def classify_skill_type(skill_name: str) -> str:
    """
    Classify a skill into categories.
    
    Args:
        skill_name: Name of the skill
    
    Returns:
        Skill type (language|framework|tool|cloud|db|concept)
    """
    skill_lower = skill_name.lower()
    
    # Simple classification logic
    languages = ['python', 'java', 'javascript', 'sql', 'r', 'c++', 'go', 'rust']
    frameworks = ['react', 'django', 'flask', 'tensorflow', 'pytorch', 'spring']
    cloud = ['aws', 'azure', 'gcp', 'cloud']
    databases = ['mysql', 'postgresql', 'mongodb', 'redis', 'sql']
    
    if any(lang in skill_lower for lang in languages):
        return 'language'
    elif any(fw in skill_lower for fw in frameworks):
        return 'framework'
    elif any(c in skill_lower for c in cloud):
        return 'cloud'
    elif any(db in skill_lower for db in databases):
        return 'db'
    else:
        return 'concept'