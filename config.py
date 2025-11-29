# ============================================
# config.py - Configuration Management
# ============================================

"""Configuration management for Short-Term Skills Agent."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # API Keys
    ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
    ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # API Settings
    ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    ADZUNA_DEFAULT_COUNTRY = "us"
    ADZUNA_MAX_DAYS_OLD = 90
    ADZUNA_RESULTS_PER_PAGE = 50
    ADZUNA_MAX_PAGES = 3
    
    # Analysis Settings
    MIN_JOB_COUNT = 100
    TOP_SKILLS_COUNT = 20
    MIN_SKILL_FREQUENCY = 5  # Minimum 5% frequency
    
    # Cache Settings
    CACHE_DIR = Path("cache/skills")
    CACHE_TTL_SECONDS = 86400  # 24 hours
    
    # Gemini Settings
    GEMINI_MODEL = "gemini-2.0-flash-exp"
    GEMINI_MAX_TOKENS = 8192
    USE_GEMINI_BY_DEFAULT = True
    
    # Output Settings
    OUTPUT_DIR = Path("output")
    SAVE_JSON_OUTPUT = True
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        missing = []
        
        if not cls.ADZUNA_APP_ID:
            missing.append("ADZUNA_APP_ID")
        if not cls.ADZUNA_APP_KEY:
            missing.append("ADZUNA_APP_KEY")
        if cls.USE_GEMINI_BY_DEFAULT and not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY (required when USE_GEMINI_BY_DEFAULT=True)")
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please create a .env file with these variables."
            )
        
        return True
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories."""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_info(cls) -> dict:
        """Get configuration information (safe for logging)."""
        return {
            "adzuna_configured": bool(cls.ADZUNA_APP_ID and cls.ADZUNA_APP_KEY),
            "gemini_configured": bool(cls.GEMINI_API_KEY),
            "gemini_model": cls.GEMINI_MODEL,
            "cache_dir": str(cls.CACHE_DIR),
            "cache_ttl_hours": cls.CACHE_TTL_SECONDS / 3600,
            "min_job_count": cls.MIN_JOB_COUNT,
            "top_skills_count": cls.TOP_SKILLS_COUNT
        }