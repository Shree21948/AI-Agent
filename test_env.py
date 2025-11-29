import os
from dotenv import load_dotenv

load_dotenv()

print("GOOGLE:", os.getenv("GOOGLE_API_KEY"))
print("ADZUNA ID:", os.getenv("ADZUNA_APP_ID"))
print("ADZUNA KEY:", os.getenv("ADZUNA_API_KEY"))