"""Tools for fetching job postings from Adzuna API."""
import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")


def fetch_job_postings(role: str, max_results: int = 150) -> List[str]:
    """
    Fetch job postings from Adzuna API.
    
    Args:
        role: Job title to search for
        max_results: Maximum number of job descriptions to return
    
    Returns:
        List of job descriptions
    """
    url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
        "results_per_page": 50,
        "what": role,
        "max_days_old": 90
    }

    results = []
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        postings = data.get("results", [])
        for post in postings:
            job_desc = post.get("description", "")
            if job_desc:
                results.append(job_desc)

        # Paginate if needed
        page = 2
        while len(results) < max_results:
            url = f"https://api.adzuna.com/v1/api/jobs/us/search/{page}"
            r = requests.get(url, params=params)
            
            if r.status_code != 200:
                break

            d = r.json().get("results", [])
            if not d:
                break

            for p in d:
                desc = p.get("description", "")
                if desc:
                    results.append(desc)

            page += 1

    except Exception as e:
        print(f"Error fetching Adzuna jobs: {e}")

    return results[:max_results]


def search_jobs_by_soc(role: str, soc_code: str, max_results: int = 150) -> List[str]:
    """
    Search jobs by role title and SOC code.
    
    Args:
        role: Job title
        soc_code: Standard Occupational Classification code
        max_results: Maximum results to return
    
    Returns:
        List of job descriptions
    """
    # Note: Adzuna doesn't directly support SOC codes in search
    # So we just search by role
    return fetch_job_postings(role, max_results)