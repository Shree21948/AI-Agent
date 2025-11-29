"""Tools for fetching YouTube learning resources via YouTube Data API v3."""
import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Whitelisted trusted channels
TRUSTED_CHANNELS = {
    "freecodecamp": "UC8butISFwT-Wl7EV0hUK0BQ",
    "google_cloud": "UCTMRxtyHoE3LPcrl-kT4AQQ",
    "cs50": "UCcabW7890RKdqK30I2r-0Aa",
    "mit_ocw": "UCEBb1b_L6zDS3xTUrIALZOw",
    "coursera": "UC4Snw5yrSDMXys31I18U3gg",
    "traversy_media": "UC29ju8bIPH5as8OGnQzwJyA",
    "programming_with_mosh": "UCWv7vMbMWH4-V0ZXdmDpPBA"
}


def search_youtube_resources(
    skill: str,
    user_level: str = "Junior",
    max_results: int = 3
) -> List[Dict[str, Any]]:
    """
    Search YouTube for learning resources on a specific skill.
    
    Args:
        skill: Skill name to search for
        user_level: User experience level (Student|Junior|Mid|Senior)
        max_results: Maximum number of resources to return per skill
    
    Returns:
        List of video resources with metadata
    """
    if not YOUTUBE_API_KEY:
        return [{
            "error": "YouTube API key not configured",
            "skill": skill
        }]
    
    base_url = "https://www.googleapis.com/youtube/v3/search"
    
    # Build search query based on user level
    level_keywords = {
        "Student": "beginner tutorial basics introduction",
        "Junior": "beginner tutorial project",
        "Mid": "intermediate advanced tutorial",
        "Senior": "advanced expert mastery deep dive"
    }
    
    search_query = f"{skill} {level_keywords.get(user_level, 'tutorial')}"
    
    resources = []
    
    # Search across trusted channels
    for channel_name, channel_id in list(TRUSTED_CHANNELS.items())[:5]:
        params = {
            "part": "snippet",
            "q": search_query,
            "channelId": channel_id,
            "type": "video",
            "maxResults": 2,
            "order": "relevance",
            "key": YOUTUBE_API_KEY
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get("items", []):
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]
                
                # Get video details (duration, views)
                video_details = get_video_details(video_id)
                
                if video_details:
                    resources.append({
                        "title": snippet["title"],
                        "channel": snippet["channelTitle"],
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "duration_minutes": video_details.get("duration_minutes", 0),
                        "difficulty": estimate_difficulty(snippet["title"], user_level),
                        "views": video_details.get("views", 0),
                        "upload_date": snippet["publishedAt"][:10],
                        "recommendation_reason": generate_recommendation_reason(
                            video_details, user_level
                        )
                    })
        
        except Exception as e:
            print(f"Error searching YouTube for {skill} on {channel_name}: {e}")
            continue
    
    # Filter and rank resources
    filtered = filter_resources(resources, user_level)
    
    return sorted(filtered, key=lambda x: x["views"], reverse=True)[:max_results]


def get_video_details(video_id: str) -> Dict[str, Any]:
    """
    Get detailed video information (duration, views, etc.).
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        Dictionary with video details
    """
    if not YOUTUBE_API_KEY:
        return {}
    
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "contentDetails,statistics",
        "id": video_id,
        "key": YOUTUBE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("items"):
            return {}
        
        item = data["items"][0]
        duration_iso = item["contentDetails"]["duration"]
        stats = item["statistics"]
        
        return {
            "duration_minutes": parse_duration(duration_iso),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0))
        }
    
    except Exception as e:
        print(f"Error fetching video details for {video_id}: {e}")
        return {}


def parse_duration(iso_duration: str) -> int:
    """
    Parse ISO 8601 duration (PT1H30M20S) to minutes.
    
    Args:
        iso_duration: ISO 8601 duration string
    
    Returns:
        Duration in minutes
    """
    import re
    
    hours = re.search(r'(\d+)H', iso_duration)
    minutes = re.search(r'(\d+)M', iso_duration)
    seconds = re.search(r'(\d+)S', iso_duration)
    
    total_minutes = 0
    if hours:
        total_minutes += int(hours.group(1)) * 60
    if minutes:
        total_minutes += int(minutes.group(1))
    if seconds:
        total_minutes += int(seconds.group(1)) / 60
    
    return int(total_minutes)


def estimate_difficulty(title: str, user_level: str) -> str:
    """
    Estimate video difficulty based on title and user level.
    
    Args:
        title: Video title
        user_level: User experience level
    
    Returns:
        Difficulty level (Beginner|Intermediate|Advanced|Expert)
    """
    title_lower = title.lower()
    
    if any(word in title_lower for word in ["beginner", "introduction", "basics", "101", "crash course"]):
        return "Beginner"
    elif any(word in title_lower for word in ["advanced", "expert", "mastery", "deep dive"]):
        return "Advanced"
    elif any(word in title_lower for word in ["intermediate", "beyond basics"]):
        return "Intermediate"
    else:
        # Default based on user level
        level_map = {
            "Student": "Beginner",
            "Junior": "Beginner",
            "Mid": "Intermediate",
            "Senior": "Advanced"
        }
        return level_map.get(user_level, "Intermediate")


def filter_resources(resources: List[Dict[str, Any]], user_level: str) -> List[Dict[str, Any]]:
    """
    Filter resources based on quality criteria.
    
    Args:
        resources: List of video resources
        user_level: User experience level
    
    Returns:
        Filtered list of resources
    """
    from datetime import datetime, timedelta
    
    five_years_ago = datetime.now() - timedelta(days=365*5)
    
    filtered = []
    for resource in resources:
        # Filter criteria
        upload_date = datetime.strptime(resource["upload_date"], "%Y-%m-%d")
        views = resource["views"]
        
        # Prefer videos <5 years old and >100k views
        if upload_date >= five_years_ago and views >= 100000:
            filtered.append(resource)
        elif upload_date >= five_years_ago and views >= 50000:
            # Allow slightly lower views for recent videos
            filtered.append(resource)
    
    return filtered


def generate_recommendation_reason(video_details: Dict[str, Any], user_level: str) -> str:
    """
    Generate a recommendation reason for a video.
    
    Args:
        video_details: Video metadata
        user_level: User experience level
    
    Returns:
        Recommendation reason string
    """
    duration = video_details.get("duration_minutes", 0)
    views = video_details.get("views", 0)
    
    reasons = []
    
    if duration > 180:
        reasons.append("comprehensive deep dive")
    elif duration > 60:
        reasons.append("thorough tutorial")
    else:
        reasons.append("concise introduction")
    
    if views > 1000000:
        reasons.append("highly popular")
    elif views > 500000:
        reasons.append("well-received")
    
    reasons.append(f"suitable for {user_level.lower()} level")
    
    return "; ".join(reasons).capitalize()