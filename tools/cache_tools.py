"""Tools for caching skill analysis results."""
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


CACHE_DIR = ".cache"
CACHE_FILE = os.path.join(CACHE_DIR, "skills_cache.json")


def get_cached_skills(role: str, ttl_seconds: int = 86400) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached skills data if available and not expired.
    
    Args:
        role: Job role to look up
        ttl_seconds: Time-to-live in seconds (default 24 hours)
    
    Returns:
        Cached data if valid, None otherwise
    """
    if not os.path.exists(CACHE_FILE):
        return None
    
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        
        if role not in cache:
            return None
        
        cached_data = cache[role]
        cached_time = datetime.fromisoformat(cached_data['timestamp'])
        
        if datetime.now() - cached_time > timedelta(seconds=ttl_seconds):
            return None
        
        return cached_data['data']
    
    except Exception as e:
        print(f"Error reading cache: {e}")
        return None


def cache_skills_data(role: str, data: Dict[str, Any]) -> None:
    """
    Cache skills data for a role.
    
    Args:
        role: Job role
        data: Skills data to cache
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    try:
        # Load existing cache
        cache = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
        
        # Add new entry
        cache[role] = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        # Save cache
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    
    except Exception as e:
        print(f"Error writing cache: {e}")