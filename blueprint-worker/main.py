"""
Blueprint GTM Worker - Modal.com serverless function

Processes Blueprint GTM jobs triggered by Supabase webhook.
Executes full 5-wave methodology using Claude API.
"""
import modal
import os
import time
from datetime import datetime
from typing import Dict

# Define Modal app (v2 - threshold fix)
app = modal.App("blueprint-gtm-worker")

# Define secrets (created via: modal secret create blueprint-secrets ...)
secrets = modal.Secret.from_name("blueprint-secrets")
vercel_secrets = modal.Secret.from_name("blueprint-vercel")

# Define container image with dependencies and local Python modules
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        "httpx",
        "anthropic",
        "supabase",
        "python-dateutil",
        "fastapi",
    ])
    .add_local_python_source("waves")
    .add_local_python_source("tools")
)


@app.function(
    image=image,
    secrets=[secrets, vercel_secrets],
    timeout=2700,  # 45 minute timeout (increased from 30)
    cpu=2,
    memory=2048,
)
@modal.fastapi_endpoint(method="POST")
async def process_blueprint_job(request: Dict) -> Dict:
    """
    Main entry point - webhook endpoint called by Supabase on INSERT.

    Expected request format (from Supabase webhook):
    {
        "type": "INSERT",
        "table": "blueprint_jobs",
        "record": {
            "id": "uuid",
            "company_url": "https://...",
            "status": "pending",
            "created_at": "..."
        }
    }
    """
    try:
        from anthropic import AsyncAnthropic
        from supabase import create_client
    except ImportError as e:
        print(f"[Blueprint Worker] Import error: {e}")
        return {"success": False, "error": f"Import error: {e}"}

    # Initialize clients
    try:
        claude = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        supabase = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_KEY"]
        )
    except Exception as e:
        print(f"[Blueprint Worker] Client init error: {e}")
        return {"success": False, "error": f"Client init error: {e}"}

    # Extract job details
    record = request.get("record", request)  # Handle both webhook and direct call formats
    job_id = record.get("id")
    company_url = record.get("company_url")

    if not job_id or not company_url:
        return {"success": False, "error": "Missing job_id or company_url"}

    print(f"[Blueprint Worker] Starting job {job_id} for {company_url}")
    job_start = time.time()

    try:
        # Update status to processing
        supabase.table("blueprint_jobs").update({
            "status": "processing",
            "started_at": datetime.now().isoformat()
        }).eq("id", job_id).execute()

        # Import wave modules
        from waves import (
            Wave1CompanyResearch,
            Wave05ProductFit,
            Wave15NicheConversion,
            Wave2DataLandscape,
            Wave25SituationFallback,
            Synthesis,
            HardGates,
            Wave3Messages,
            Wave4HTML,
            Wave45Publish
        )
        from tools import WebFetch, WebSearch, DualProviderSearch

        # Initialize tools
        serper_key = os.environ.get("SERPER_API_KEY", "")
        rapidapi_key = os.environ.get("RAPIDAPI_KEY", "")
        openweb_ninja_key = os.environ.get("OPENWEB_NINJA_KEY", "")  # Native ak_ format key
        web_fetch = WebFetch()

        # Use dual-provider search with OpenWeb Ninja native API (preferred) or RapidAPI
        if openweb_ninja_key:
            print("[Tools] Using dual-provider search (Serper + OpenWeb Ninja native API)")
            web_search = DualProviderSearch(serper_key, openweb_ninja_key, use_native=True)
        elif rapidapi_key:
            print("[Tools] Using dual-provider search (Serper + OpenWeb Ninja via RapidAPI)")
            web_search = DualProviderSearch(serper_key, rapidapi_key, use_native=False)
        else:
            print("[Tools] Using Serper-only search")
            web_search = WebSearch(serper_key)

        # ========== WAVE 1: Company Intelligence ==========
        wave_start = time.time()
        print("[Wave 1] Gathering company intelligence...")
        wave1 = Wave1CompanyResearch(claude, web_fetch, web_search)
        company_context = await wave1.execute(company_url)
        print(f"[Wave 1] Complete in {time.time() - wave_start:.1f}s: {company_context.get('company_name', 'Unknown')}")

        # ========== WAVE 0.5: Product Fit Analysis ==========
        wave_start = time.time()
        print("[Wave 0.5] Analyzing product fit...")
        wave05 = Wave05ProductFit(claude)
        product_fit = await wave05.execute(company_context)
        print(f"[Wave 0.5] Complete in {time.time() - wave_start:.1f}s: {len(product_fit.get('valid_domains', []))} valid domains")

        # ========== WAVE 1.5: Niche Conversion ==========
        wave_start = time.time()
        print("[Wave 1.5] Converting niches...")
        wave15 = Wave15NicheConversion(claude, web_search)
        niches = await wave15.execute(company_context, product_fit)
        print(f"[Wave 1.5] Complete in {time.time() - wave_start:.1f}s: {len(niches.get('qualified_niches', []))} qualified niches")

        # ========== WAVE 2.5: Situation Fallback (if needed) ==========
        situation_segments = []
        if niches.get("fallback_needed", False):
            wave_start = time.time()
            print("[Wave 2.5] Niche fallback triggered - generating situation segments...")
            wave25 = Wave25SituationFallback(claude, web_search)
            situation_result = await wave25.execute(company_context, product_fit)
            situation_segments = situation_result.get("situation_segments", [])
            print(f"[Wave 2.5] Complete in {time.time() - wave_start:.1f}s: {len(situation_segments)} situation segments")

        # ========== WAVE 2: Data Landscape ==========
        wave_start = time.time()
        print("[Wave 2] Mapping data landscape...")
        wave2 = Wave2DataLandscape(claude, web_search)
        data_landscape = await wave2.execute(
            niches.get("qualified_niches", [{}])[0] if niches.get("qualified_niches") else {},
            company_context
        )
        print(f"[Wave 2] Complete in {time.time() - wave_start:.1f}s: {sum(len(v) for v in data_landscape.values() if isinstance(v, list))} sources found")

        # ========== SYNTHESIS: Sequential Thinking ==========
        wave_start = time.time()
        print("[Synthesis] Generating pain segments...")
        synthesis = Synthesis(claude)
        segments_result = await synthesis.generate_segments(
            company_context,
            data_landscape,
            product_fit
        )
        segments = segments_result.get("segments", [])
        print(f"[Synthesis] Complete in {time.time() - wave_start:.1f}s: {len(segments)} segments generated")

        # Combine with situation segments if available
        if situation_segments:
            # Convert situation segments to match synthesis segment format
            for sit_seg in situation_segments:
                segments.append({
                    "name": sit_seg.get("name", "Situation Segment"),
                    "description": sit_seg.get("pain_hypothesis", ""),
                    "data_sources": [s.get("source", "") for s in sit_seg.get("data_sources", [])],
                    "fields": [],
                    "message_type": sit_seg.get("message_type", "PQS"),
                    "trigger_event": sit_seg.get("trigger_event", ""),
                    "is_situation_based": True
                })
            print(f"[Synthesis] Added {len(situation_segments)} situation segments")

        # ========== HARD GATES: Validation ==========
        wave_start = time.time()
        print("[Hard Gates] Validating segments...")
        hard_gates = HardGates(claude)
        validated_segments = await hard_gates.validate(segments, product_fit)
        print(f"[Hard Gates] Complete in {time.time() - wave_start:.1f}s: {len(validated_segments)}/{len(segments)} segments passed")

        if len(validated_segments) < 1:
            # Fallback: take best unvalidated segment if all failed
            print("[Hard Gates] All segments failed - using top 2 with warnings...")
            validated_segments = segments[:2] if segments else [{
                "name": "Sales Engagement Leaders",
                "description": "Companies using multiple sales tools seeking consolidation",
                "data_sources": ["G2", "LinkedIn"],
                "fields": ["company_name", "technology_stack"],
                "message_type": "PQS"
            }]

        # ========== WAVE 3: Message Generation ==========
        wave_start = time.time()
        print("[Wave 3] Generating messages...")
        wave3 = Wave3Messages(claude)
        messages = await wave3.generate(validated_segments[:4], company_context)  # Process 4 segments instead of 2
        print(f"[Wave 3] Complete in {time.time() - wave_start:.1f}s: {len(messages)} messages generated")

        # ========== WAVE 4: HTML Assembly ==========
        wave_start = time.time()
        print("[Wave 4] Assembling HTML playbook...")
        wave4 = Wave4HTML()
        html_content = wave4.generate(company_context, messages)
        print(f"[Wave 4] Complete in {time.time() - wave_start:.1f}s: {len(html_content)} bytes")

        # ========== WAVE 4.5: Publish to GitHub ==========
        wave_start = time.time()
        print("[Wave 4.5] Publishing to GitHub Pages...")
        wave45 = Wave45Publish(
            github_token=os.environ.get("GITHUB_TOKEN", ""),
            repo=os.environ.get("GITHUB_REPO", "blueprint-gtm-playbooks"),
            owner=os.environ.get("GITHUB_OWNER", "SantaJordan")
        )
        company_slug = company_url.split("//")[-1].split("/")[0].replace(".", "-").replace("www-", "")
        playbook_url = await wave45.publish(html_content, company_slug)
        print(f"[Wave 4.5] Complete in {time.time() - wave_start:.1f}s: {playbook_url}")

        # ========== WAVE 5: Capture Payment (if applicable) ==========
        payment_intent_id = record.get("stripe_payment_intent_id")
        if payment_intent_id:
            import httpx
            wave_start = time.time()
            print("[Wave 5] Capturing payment...")
            vercel_api_url = os.environ.get("VERCEL_API_URL", "")
            modal_webhook_secret = os.environ.get("MODAL_WEBHOOK_SECRET", "")

            if vercel_api_url and modal_webhook_secret:
                try:
                    async with httpx.AsyncClient(timeout=30) as client:
                        response = await client.post(
                            f"{vercel_api_url}/api/capture-payment",
                            headers={
                                "Authorization": f"Bearer {modal_webhook_secret}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "job_id": job_id,
                                "playbook_url": playbook_url
                            }
                        )
                        if response.status_code == 200:
                            print(f"[Wave 5] Payment captured successfully in {time.time() - wave_start:.1f}s")
                        else:
                            print(f"[Wave 5] Payment capture failed: {response.text}")
                except Exception as payment_err:
                    print(f"[Wave 5] Payment capture error: {payment_err}")
            else:
                print("[Wave 5] Payment capture skipped - missing VERCEL_API_URL or MODAL_WEBHOOK_SECRET")
        else:
            print("[Wave 5] Skipped - no payment intent (test job or legacy)")

        # Update job as completed
        supabase.table("blueprint_jobs").update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "playbook_url": playbook_url
        }).eq("id", job_id).execute()

        total_time = time.time() - job_start
        print(f"[Blueprint Worker] Job {job_id} completed in {total_time:.1f}s ({total_time/60:.1f} min)")
        return {"success": True, "playbook_url": playbook_url}

    except Exception as e:
        error_msg = str(e)
        print(f"[Blueprint Worker] Job {job_id} failed: {error_msg}")

        # Update job as failed
        try:
            supabase.table("blueprint_jobs").update({
                "status": "failed",
                "error_message": error_msg[:1000]  # Limit error message length
            }).eq("id", job_id).execute()
        except Exception as update_err:
            print(f"[Blueprint Worker] Failed to update job status: {update_err}")

        return {"success": False, "error": error_msg}


@app.function(image=image, secrets=[secrets, vercel_secrets], schedule=modal.Cron("*/5 * * * *"))
async def poll_pending_jobs():
    """
    Backup cron job that polls for pending jobs every 5 minutes.
    This handles cases where the webhook fails.
    """
    from supabase import create_client

    supabase = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"]
    )

    # Find pending jobs
    result = supabase.table("blueprint_jobs").select("*").eq("status", "pending").limit(1).execute()

    if result.data:
        job = result.data[0]
        print(f"[Cron] Found pending job: {job['id']}")

        # Process the job
        await process_blueprint_job.remote.aio({
            "record": job
        })


# Local testing entry point
@app.local_entrypoint()
def main(company_url: str = "https://owner.com"):
    """Test the worker locally with a company URL."""
    import asyncio

    result = asyncio.run(process_blueprint_job.remote.aio({
        "record": {
            "id": "test-job-001",
            "company_url": company_url
        }
    }))

    print(f"Result: {result}")
