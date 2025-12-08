#!/usr/bin/env python3
"""Monitor a specific job status."""
import urllib.request
import json
import time
import sys
from datetime import datetime

SUPABASE_URL = "https://hvuwlhdaswixbkglnrxu.supabase.co"
APIKEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2dXdsaGRhc3dpeGJrZ2xucnh1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMzMjI0NzQsImV4cCI6MjA3ODg5ODQ3NH0.MEdFuiFtz6tMwcVz5tql6BjklvfZzNopwEEUvtLRqsA"

def check_job(job_id: str):
    url = f"{SUPABASE_URL}/rest/v1/blueprint_jobs?id=eq.{job_id}&select=id,status,company_url,started_at,completed_at,playbook_url,error_message"
    headers = {
        "apikey": APIKEY,
        "Authorization": f"Bearer {APIKEY}"
    }

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode())
        if data:
            return data[0]
        return None

def monitor(job_id: str, interval: int = 30, max_checks: int = 60):
    print(f"=== HAIKU SPEED TEST ===")
    print(f"Job ID: {job_id}")
    print(f"Model: claude-opus-4-5-20251101 (fastest)")
    print(f"Started monitoring: {datetime.now().strftime('%H:%M:%S')}")
    print()

    for i in range(1, max_checks + 1):
        try:
            job = check_job(job_id)
            if not job:
                print(f"[{i}] Job not found")
                time.sleep(interval)
                continue

            status = job.get('status', 'unknown')
            now = datetime.now().strftime('%H:%M:%S')
            print(f"[{now}] Status: {status}")

            if status == 'completed':
                print(f"\n=== SUCCESS! ===")
                print(f"Playbook: {job.get('playbook_url')}")
                print(f"Completed at: {job.get('completed_at')}")
                return True
            elif status == 'failed':
                print(f"\n=== FAILED ===")
                print(f"Error: {job.get('error_message')}")
                return False

        except Exception as e:
            print(f"[Error] {e}")

        time.sleep(interval)

    print("\nMonitoring timeout reached")
    return False

if __name__ == "__main__":
    job_id = sys.argv[1] if len(sys.argv) > 1 else "43f1ad98-db3b-496e-a3b2-9ce5037bb529"
    monitor(job_id, interval=30)
