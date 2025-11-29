"""Enhanced caching with SQLite database."""
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


DB_PATH = ".cache/cache.db"


def init_cache_db():
    """Initialize SQLite cache database."""
    os.makedirs(".cache", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            ttl_seconds INTEGER NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


def get_from_cache(key: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve data from cache if valid.
    
    Args:
        key: Cache key
    
    Returns:
        Cached data or None if expired/missing
    """
    init_cache_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT value, timestamp, ttl_seconds FROM cache WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    value, timestamp, ttl_seconds = result
    cached_time = datetime.fromisoformat(timestamp)
    
    if datetime.now() - cached_time > timedelta(seconds=ttl_seconds):
        return None
    
    return json.loads(value)


def set_in_cache(key: str, value: Dict[str, Any], ttl_seconds: int):
    """
    Store data in cache.
    
    Args:
        key: Cache key
        value: Data to cache
        ttl_seconds: Time-to-live in seconds
    """
    init_cache_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO cache (key, value, timestamp, ttl_seconds)
        VALUES (?, ?, ?, ?)
    """, (key, json.dumps(value), datetime.now().isoformat(), ttl_seconds))
    
    conn.commit()
    conn.close()


def clear_cache():
    """Clear all cache entries."""
    init_cache_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cache")
    conn.commit()
    conn.close()