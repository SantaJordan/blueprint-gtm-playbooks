#!/usr/bin/env python3
"""Create a new pending test job in Supabase."""
import urllib.request
import json
import uuid
from datetime import datetime

SUPABASE_URL = "https://hvuwlhdaswixbkglnrxu.supabase.co"
APIKEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2dXdsaGRhc3dpeGJrZ2xucnh1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMzMjI0NzQsImV4cCI6MjA3ODg5ODQ3NH0.MEdFuiFtz6tMwcVz5tql6BjklvfZzNopwEEUvtLRqsA"

def create_job(company_url: str):
    job_id = str(uuid.uuid4())
    data = json.dumps({
        "id": job_id,
        "company_url": company_url,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }).encode()

    url = f"{SUPABASE_URL}/rest/v1/blueprint_jobs"
    headers = {
        "apikey": APIKEY,
        "Authorization": f"Bearer {APIKEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            print(f"Created job: {result}")
            return job_id
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    import sys
    company = sys.argv[1] if len(sys.argv) > 1 else "https://owner.com"
    job_id = create_job(company)
    if job_id:
        print(f"\nJob ID: {job_id}")
        print(f"Status: pending (cron will pick up in ~5 min)")
