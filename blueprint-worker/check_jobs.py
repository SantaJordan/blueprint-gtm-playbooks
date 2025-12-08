#!/usr/bin/env python3
"""Check Supabase blueprint_jobs status."""
import urllib.request
import json

SUPABASE_URL = "https://hvuwlhdaswixbkglnrxu.supabase.co"
APIKEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2dXdsaGRhc3dpeGJrZ2xucnh1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMzMjI0NzQsImV4cCI6MjA3ODg5ODQ3NH0.MEdFuiFtz6tMwcVz5tql6BjklvfZzNopwEEUvtLRqsA"

def check_jobs():
    url = f"{SUPABASE_URL}/rest/v1/blueprint_jobs?order=created_at.desc&limit=10&select=id,company_url,status,created_at,started_at,completed_at,playbook_url,error_message"
    headers = {
        "apikey": APIKEY,
        "Authorization": f"Bearer {APIKEY}"
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            print(f"Found {len(data)} jobs:\n")
            for job in data:
                print(f"ID: {job['id'][:8]}...")
                print(f"  Company: {job.get('company_url', 'N/A')}")
                print(f"  Status: {job.get('status', 'N/A')}")
                print(f"  Created: {job.get('created_at', 'N/A')}")
                if job.get('playbook_url'):
                    print(f"  Playbook: {job['playbook_url']}")
                if job.get('error_message'):
                    print(f"  Error: {job['error_message'][:100]}...")
                print()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_jobs()
