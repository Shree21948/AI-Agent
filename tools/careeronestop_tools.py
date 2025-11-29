"""Tools for mapping job titles to official SOC codes via CareerOneStop API."""
import os
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

CAREERONESTOP_USER_ID = os.getenv("CAREERONESTOP_USER_ID")
CAREERONESTOP_TOKEN = os.getenv("CAREERONESTOP_TOKEN")


def search_occupation(job_title: str) -> Dict[str, Any]:
    """
    Search for official occupation title and SOC code.
    
    Args:
        job_title: Job title from resume (e.g., "Data Scientist")
    
    Returns:
        Dictionary with official title, SOC code, and confidence
    """
    if not CAREERONESTOP_USER_ID or not CAREERONESTOP_TOKEN:
        return {
            "error": "CareerOneStop API credentials not configured",
            "official_title": None,
            "soc_code": None,
            "confidence": 0.0
        }
    
    # CareerOneStop Occupation Search endpoint
    url = f"https://api.careeronestop.org/v1/occupation/{CAREERONESTOP_USER_ID}/{job_title}/0/0"
    
    headers = {
        "Authorization": f"Bearer {CAREERONESTOP_TOKEN}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Parse results
        occupations = data.get("OccupationList", [])
        
        if not occupations:
            # Fallback: try fuzzy matching
            return fuzzy_match_occupation(job_title)
        
        # Pick best match
        best_match = select_best_match(job_title, occupations)
        
        return {
            "official_title": best_match["title"],
            "soc_code": best_match["code"],
            "alternate_titles": best_match.get("alternate_titles", []),
            "confidence": best_match["confidence"],
            "notes": best_match.get("notes", ""),
            "data_source": "CareerOneStop"
        }
    
    except Exception as e:
        print(f"Error calling CareerOneStop API: {e}")
        # Fallback to local mapping
        return fuzzy_match_occupation(job_title)


def select_best_match(query: str, occupations: List[Dict]) -> Dict[str, Any]:
    """
    Select the best matching occupation from API results.
    
    Args:
        query: Original job title query
        occupations: List of occupation matches from API
    
    Returns:
        Best match with confidence score
    """
    query_lower = query.lower()
    
    # Priority keywords for common roles
    priority_keywords = {
        "data scientist": ["data scien", "15-2051"],
        "software engineer": ["software dev", "software eng", "15-1252"],
        "machine learning": ["data scien", "15-2051"],
        "cloud engineer": ["network", "cloud", "15-1244"],
        "devops": ["software dev", "15-1252"],
        "data analyst": ["data anal", "operations research", "15-2041"],
        "web developer": ["web dev", "15-1254"],
    }
    
    # Check for exact or priority matches
    for occupation in occupations:
        occ_title = occupation.get("OccupationTitle", "").lower()
        occ_code = occupation.get("OnetCode", "")
        
        # Exact match
        if query_lower == occ_title:
            return {
                "title": occupation.get("OccupationTitle"),
                "code": format_soc_code(occ_code),
                "confidence": 1.0,
                "notes": "Exact match found"
            }
        
        # Priority keyword match
        for key, keywords in priority_keywords.items():
            if key in query_lower:
                for keyword in keywords:
                    if keyword in occ_title or keyword in occ_code:
                        return {
                            "title": occupation.get("OccupationTitle"),
                            "code": format_soc_code(occ_code),
                            "confidence": 0.9,
                            "notes": f"Matched via priority keywords: {key}"
                        }
    
    # Default to first result
    if occupations:
        first = occupations[0]
        return {
            "title": first.get("OccupationTitle"),
            "code": format_soc_code(first.get("OnetCode", "")),
            "confidence": 0.75,
            "notes": "Best available match from API results"
        }
    
    return {
        "title": query,
        "code": None,
        "confidence": 0.3,
        "notes": "No suitable match found"
    }


def format_soc_code(onet_code: str) -> str:
    """
    Convert O*NET code to SOC code format.
    
    Args:
        onet_code: O*NET code (e.g., "15-2051.01")
    
    Returns:
        SOC code (e.g., "15-2051")
    """
    # O*NET codes are more detailed; SOC codes are first 7 chars
    if not onet_code:
        return None
    
    # Remove .XX suffix if present
    parts = onet_code.split(".")
    return parts[0] if parts else onet_code


def fuzzy_match_occupation(job_title: str) -> Dict[str, Any]:
    """
    Fallback: Match job title to common occupations when API fails.
    
    Args:
        job_title: Job title to match
    
    Returns:
        Best guess mapping
    """
    # Common role mappings (fallback database)
    common_mappings = {
        "data scientist": {"title": "Data Scientists", "soc": "15-2051", "confidence": 0.85},
        "machine learning engineer": {"title": "Data Scientists", "soc": "15-2051", "confidence": 0.80},
        "ml engineer": {"title": "Data Scientists", "soc": "15-2051", "confidence": 0.80},
        "software engineer": {"title": "Software Developers", "soc": "15-1252", "confidence": 0.85},
        "software developer": {"title": "Software Developers", "soc": "15-1252", "confidence": 0.90},
        "developer": {"title": "Software Developers", "soc": "15-1252", "confidence": 0.75},
        "full stack developer": {"title": "Software Developers", "soc": "15-1252", "confidence": 0.85},
        "frontend developer": {"title": "Web Developers", "soc": "15-1254", "confidence": 0.85},
        "backend developer": {"title": "Software Developers", "soc": "15-1252", "confidence": 0.85},
        "web developer": {"title": "Web Developers", "soc": "15-1254", "confidence": 0.90},
        "devops engineer": {"title": "Software Developers", "soc": "15-1252", "confidence": 0.75},
        "mlops engineer": {"title": "Software Developers", "soc": "15-1252", "confidence": 0.70},
        "cloud engineer": {"title": "Network and Computer Systems Administrators", "soc": "15-1244", "confidence": 0.80},
        "cloud architect": {"title": "Computer Network Architects", "soc": "15-1241", "confidence": 0.85},
        "data analyst": {"title": "Data Analysts", "soc": "15-2051", "confidence": 0.85},
        "data engineer": {"title": "Database Architects", "soc": "15-1243", "confidence": 0.80},
        "business analyst": {"title": "Management Analysts", "soc": "13-1111", "confidence": 0.80},
        "product manager": {"title": "Computer and Information Systems Managers", "soc": "11-3021", "confidence": 0.75},
    }
    
    title_lower = job_title.lower().strip()
    
    # Check for exact match
    if title_lower in common_mappings:
        mapping = common_mappings[title_lower]
        return {
            "official_title": mapping["title"],
            "soc_code": mapping["soc"],
            "confidence": mapping["confidence"],
            "notes": "Matched via fallback database (API unavailable)",
            "data_source": "Local mapping"
        }
    
    # Check for partial matches
    for key, mapping in common_mappings.items():
        if key in title_lower or title_lower in key:
            return {
                "official_title": mapping["title"],
                "soc_code": mapping["soc"],
                "confidence": mapping["confidence"] - 0.1,  # Lower confidence for partial match
                "notes": f"Partial match: '{job_title}' → '{key}'",
                "data_source": "Local mapping"
            }
    
    # No match found
    return {
        "official_title": job_title,
        "soc_code": None,
        "confidence": 0.3,
        "notes": "No match found. Manual mapping recommended.",
        "data_source": "No match"
    }