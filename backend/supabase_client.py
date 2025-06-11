import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def insert_session(data: dict):
    url = f"{SUPABASE_URL}/rest/v1/sessions"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code >= 400:
        return {"error": response.text}
    return response.json()

