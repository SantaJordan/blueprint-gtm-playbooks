#!/usr/bin/env python3
"""
Test all Modal API keys to verify they are working correctly.

Usage:
    modal run test_api_keys.py
"""
import modal
import os
import asyncio
from typing import Dict, Tuple

# Define Modal app
app = modal.App("blueprint-api-key-tester")

# Define secrets (same as main worker)
secrets = modal.Secret.from_name("blueprint-secrets")
vercel_secrets = modal.Secret.from_name("blueprint-vercel")

# Container image with required dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        "httpx",
        "anthropic",
        "supabase",
    ])
)


async def test_anthropic() -> Tuple[bool, str]:
    """Test Claude API with minimal token request."""
    try:
        from anthropic import AsyncAnthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return False, "not configured"

        client = AsyncAnthropic(api_key=api_key)
        response = await client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=1,
            messages=[{"role": "user", "content": "Hi"}]
        )
        return True, f"model={response.model}"
    except Exception as e:
        return False, str(e)[:50]


async def test_serper() -> Tuple[bool, str]:
    """Test Serper search API."""
    try:
        import httpx
        api_key = os.environ.get("SERPER_API_KEY")
        if not api_key:
            return False, "not configured"

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api_key},
                json={"q": "test", "num": 1},
                timeout=10
            )
            if resp.status_code == 200:
                return True, f"status={resp.status_code}"
            return False, f"status={resp.status_code}, {resp.text[:30]}"
    except Exception as e:
        return False, str(e)[:50]


async def test_supabase() -> Tuple[bool, str]:
    """Test Supabase connection and query."""
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")

        if not url:
            return False, "SUPABASE_URL not configured"
        if not key:
            return False, "SUPABASE_SERVICE_KEY not configured"

        client = create_client(url, key)
        result = client.table("blueprint_jobs").select("id", count="exact").limit(1).execute()
        return True, f"jobs_count={result.count}"
    except Exception as e:
        return False, str(e)[:50]


async def test_github() -> Tuple[bool, str]:
    """Test GitHub API access to repository."""
    try:
        import httpx
        token = os.environ.get("GITHUB_TOKEN")
        owner = os.environ.get("GITHUB_OWNER", "SantaJordan")
        repo = os.environ.get("GITHUB_REPO", "blueprint-gtm-playbooks")

        if not token:
            return False, "GITHUB_TOKEN not configured"

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                return True, f"repo={data['full_name']}"
            return False, f"status={resp.status_code}"
    except Exception as e:
        return False, str(e)[:50]


async def test_vercel_url() -> Tuple[bool, str]:
    """Test Vercel API endpoint is reachable."""
    try:
        import httpx
        url = os.environ.get("VERCEL_API_URL")

        if not url:
            return False, "not configured"

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10, follow_redirects=True)
            # Any response is fine - we just want to verify the URL works
            return True, f"url={url}, status={resp.status_code}"
    except Exception as e:
        return False, str(e)[:50]


def test_webhook_secret() -> Tuple[bool, str]:
    """Test webhook secret is configured."""
    secret = os.environ.get("MODAL_WEBHOOK_SECRET")
    if not secret:
        return False, "not configured"
    return True, f"configured ({len(secret)} chars)"


def test_github_config() -> Tuple[bool, str, bool, str]:
    """Test GitHub owner and repo config."""
    owner = os.environ.get("GITHUB_OWNER")
    repo = os.environ.get("GITHUB_REPO")

    owner_ok = bool(owner)
    repo_ok = bool(repo)

    owner_msg = owner if owner else "not configured"
    repo_msg = repo if repo else "not configured"

    return owner_ok, owner_msg, repo_ok, repo_msg


async def test_openweb_ninja() -> Tuple[bool, str]:
    """Test OpenWeb Ninja API (optional)."""
    try:
        import httpx
        api_key = os.environ.get("OPENWEB_NINJA_KEY")

        if not api_key:
            return None, "not configured"  # None = skipped

        # Test the actual search endpoint (GET with query params)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.openwebninja.com/realtime-web-search/search-light",
                headers={"x-api-key": api_key},
                params={"q": "test", "limit": 1},
                timeout=15
            )
            if resp.status_code == 200:
                return True, "search works"
            return False, f"status={resp.status_code}"
    except Exception as e:
        return False, str(e)[:50]


async def test_rapidapi() -> Tuple[bool, str]:
    """Test RapidAPI key (optional)."""
    api_key = os.environ.get("RAPIDAPI_KEY")

    if not api_key:
        return None, "not configured"  # None = skipped

    # RapidAPI key is present - we'll just verify it's set
    return True, f"configured ({len(api_key)} chars)"


@app.function(
    image=image,
    secrets=[secrets, vercel_secrets],
    timeout=120,
)
async def test_all_keys() -> Dict:
    """Test all API keys and return results."""
    print("\n" + "=" * 50)
    print("        Modal API Key Test Results")
    print("=" * 50 + "\n")

    results = {}
    passed = 0
    failed = 0
    skipped = 0

    # Required keys
    print("Required Keys:")

    # Anthropic
    ok, msg = await test_anthropic()
    results["ANTHROPIC_API_KEY"] = {"ok": ok, "msg": msg}
    status = "PASS" if ok else "FAIL"
    icon = "+" if ok else "X"
    print(f"  [{icon}] ANTHROPIC_API_KEY     {status}  {msg}")
    if ok:
        passed += 1
    else:
        failed += 1

    # Serper
    ok, msg = await test_serper()
    results["SERPER_API_KEY"] = {"ok": ok, "msg": msg}
    status = "PASS" if ok else "FAIL"
    icon = "+" if ok else "X"
    print(f"  [{icon}] SERPER_API_KEY        {status}  {msg}")
    if ok:
        passed += 1
    else:
        failed += 1

    # Supabase
    ok, msg = await test_supabase()
    results["SUPABASE"] = {"ok": ok, "msg": msg}
    status = "PASS" if ok else "FAIL"
    icon = "+" if ok else "X"
    print(f"  [{icon}] SUPABASE              {status}  {msg}")
    if ok:
        passed += 1
    else:
        failed += 1

    # GitHub
    ok, msg = await test_github()
    results["GITHUB_TOKEN"] = {"ok": ok, "msg": msg}
    status = "PASS" if ok else "FAIL"
    icon = "+" if ok else "X"
    print(f"  [{icon}] GITHUB_TOKEN          {status}  {msg}")
    if ok:
        passed += 1
    else:
        failed += 1

    # GitHub config
    owner_ok, owner_msg, repo_ok, repo_msg = test_github_config()
    results["GITHUB_OWNER"] = {"ok": owner_ok, "msg": owner_msg}
    results["GITHUB_REPO"] = {"ok": repo_ok, "msg": repo_msg}

    status = "PASS" if owner_ok else "FAIL"
    icon = "+" if owner_ok else "X"
    print(f"  [{icon}] GITHUB_OWNER          {status}  {owner_msg}")
    if owner_ok:
        passed += 1
    else:
        failed += 1

    status = "PASS" if repo_ok else "FAIL"
    icon = "+" if repo_ok else "X"
    print(f"  [{icon}] GITHUB_REPO           {status}  {repo_msg}")
    if repo_ok:
        passed += 1
    else:
        failed += 1

    # Vercel URL
    ok, msg = await test_vercel_url()
    results["VERCEL_API_URL"] = {"ok": ok, "msg": msg}
    status = "PASS" if ok else "FAIL"
    icon = "+" if ok else "X"
    print(f"  [{icon}] VERCEL_API_URL        {status}  {msg}")
    if ok:
        passed += 1
    else:
        failed += 1

    # Webhook secret
    ok, msg = test_webhook_secret()
    results["MODAL_WEBHOOK_SECRET"] = {"ok": ok, "msg": msg}
    status = "PASS" if ok else "FAIL"
    icon = "+" if ok else "X"
    print(f"  [{icon}] MODAL_WEBHOOK_SECRET  {status}  {msg}")
    if ok:
        passed += 1
    else:
        failed += 1

    # Optional keys
    print("\nOptional Keys:")

    # OpenWeb Ninja
    ok, msg = await test_openweb_ninja()
    results["OPENWEB_NINJA_KEY"] = {"ok": ok, "msg": msg}
    if ok is None:
        print(f"  [-] OPENWEB_NINJA_KEY     SKIP  {msg}")
        skipped += 1
    elif ok:
        print(f"  [+] OPENWEB_NINJA_KEY     PASS  {msg}")
        passed += 1
    else:
        print(f"  [X] OPENWEB_NINJA_KEY     FAIL  {msg}")
        failed += 1

    # RapidAPI
    ok, msg = await test_rapidapi()
    results["RAPIDAPI_KEY"] = {"ok": ok, "msg": msg}
    if ok is None:
        print(f"  [-] RAPIDAPI_KEY          SKIP  {msg}")
        skipped += 1
    elif ok:
        print(f"  [+] RAPIDAPI_KEY          PASS  {msg}")
        passed += 1
    else:
        print(f"  [X] RAPIDAPI_KEY          FAIL  {msg}")
        failed += 1

    # Summary
    total_required = 8
    required_passed = sum(1 for k in ["ANTHROPIC_API_KEY", "SERPER_API_KEY", "SUPABASE",
                                       "GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO",
                                       "VERCEL_API_URL", "MODAL_WEBHOOK_SECRET"]
                         if results.get(k, {}).get("ok"))

    print("\n" + "=" * 50)
    print(f"Summary: {required_passed}/{total_required} required keys working")
    if failed > 0:
        print(f"         {failed} key(s) FAILED - action required!")
    if skipped > 0:
        print(f"         {skipped} optional key(s) skipped")
    print("=" * 50 + "\n")

    return {
        "results": results,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "all_required_ok": required_passed == total_required
    }


@app.local_entrypoint()
def main():
    """Run the API key tests."""
    result = test_all_keys.remote()

    if not result["all_required_ok"]:
        print("\n!!! Some required keys failed. Please fix them before running jobs. !!!\n")
        exit(1)
    else:
        print("\nAll required keys are working!\n")
