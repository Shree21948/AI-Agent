import os
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

CAREERONESTOP_USER_ID = os.getenv("CAREERONESTOP_USER_ID")
CAREERONESTOP_API_KEY = os.getenv("CAREERONESTOP_API_KEY")


def map_role_with_careeronestop(title: str):
    """
    Takes a user's job title,sends it to CareerOneStop, and returns the standardized
    job title + SOC code.
    """

    # To remove extra spaces 
    keyword = title.strip()

    # Make the keyword safe for a URL
    encoded_keyword = urllib.parse.quote(keyword)

    # Minimal URL (no splitting)
    url = f"https://api.careeronestop.org/v1/occupation/{CAREERONESTOP_USER_ID}/{encoded_keyword}/N/0/1"

   
    headers = {
        "Authorization": f"Bearer {CAREERONESTOP_API_KEY}",
        "Accept": "application/json"
    }

    params = {
        "datasettype": "soc",
        "searchby": "title"
    }

    # API request
    response = requests.get(url, headers={"Authorization": f"Bearer {CAREERONESTOP_API_KEY}","Accept": "application/json"
    }, params={"datasettype": "soc","searchby": "title"})
    response.raise_for_status()

    data = response.json()

    # To read the list of possible job matches.
    soc_list = data.get("SocOccupationList") or []

    # If no matches, return empty result
    if not soc_list:
        return {
            "input_title": keyword,
            "standard_title": None,
            "soc_code": None
        }

    # Pick the best match: the first result
    primary = soc_list[0]

    # Extract only what you NEED
    standard_title = primary.get("Title")
    soc_code = primary.get("Code")

    # Return ONLY the essential fields
    return {
        "input_title": keyword,
        "standard_title": standard_title,
        "soc_code": soc_code
    }