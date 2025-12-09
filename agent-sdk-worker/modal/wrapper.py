"""
Modal Python Wrapper for Agent SDK Worker

This wrapper deploys the TypeScript Agent SDK worker to Modal.
It spawns Node.js as a subprocess to run the TypeScript code.
"""

import modal
import subprocess
import os
import json
import sys

# Define the Modal app
app = modal.App("blueprint-agent-sdk-worker")

# Get the agent-sdk-worker directory path and parent (Blueprint-GTM-Skills)
AGENT_WORKER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLUEPRINT_SKILLS_DIR = os.path.dirname(AGENT_WORKER_DIR)  # Parent directory with .claude/

# Create a custom image with Node.js and required packages
image = (
    modal.Image.debian_slim(python_version="3.11")
    # Install Node.js 20
    .apt_install("curl", "git")
    .run_commands([
        # Install Node.js 20 via NodeSource
        "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -",
        "apt-get install -y nodejs",
        # Verify installation
        "node --version",
        "npm --version",
    ])
    # Install global npm packages
    .run_commands([
        "npm install -g tsx",
        "npm install -g @modelcontextprotocol/server-sequential-thinking",
    ])
    # Install Python dependencies for Supabase health checks and web endpoints
    .pip_install(["supabase", "httpx", "fastapi"])
    # Add the agent-sdk-worker source code to the image
    .add_local_dir(
        AGENT_WORKER_DIR,
        remote_path="/app/agent-sdk-worker",
        ignore=["node_modules", "dist", ".git", "__pycache__", "*.pyc"],
    )
    # Add the .claude/ skills directory (from parent Blueprint-GTM-Skills)
    .add_local_dir(
        os.path.join(BLUEPRINT_SKILLS_DIR, ".claude"),
        remote_path="/app/blueprint-skills/.claude",
    )
    # Add CLAUDE.md from parent
    .add_local_file(
        os.path.join(BLUEPRINT_SKILLS_DIR, "CLAUDE.md"),
        remote_path="/app/blueprint-skills/CLAUDE.md",
    )
)

# Modal secrets - uses the same secrets as the existing blueprint-worker
secrets = [
    modal.Secret.from_name("blueprint-secrets"),
]


@app.function(
    image=image,
    secrets=secrets,
    timeout=2700,  # 45 minutes (Blueprint Turbo + overhead)
    cpu=2,
    memory=4096,
)
@modal.fastapi_endpoint(method="POST")
async def process_blueprint_job(request: dict):
    """
    Webhook endpoint for Supabase to trigger job processing.

    Expects a Supabase webhook payload with the job record.
    """
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("agent-sdk-worker")

    logger.info(f"Received webhook request: {json.dumps(request, indent=2)[:500]}")

    # Extract job from webhook payload
    record = request.get("record", request)
    job_id = record.get("id")
    company_url = record.get("company_url")

    if not job_id or not company_url:
        logger.error(f"Invalid request - missing id or company_url: {request}")
        return {"success": False, "error": "Invalid request - missing id or company_url"}

    logger.info(f"Processing job {job_id} for {company_url}")

    # Create symlinks so Agent SDK can find .claude directory from worker's cwd
    logger.info("Setting up symlinks for skills directory...")
    try:
        subprocess.run(
            ["ln", "-sf", "/app/blueprint-skills/.claude", "/app/agent-sdk-worker/.claude"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["ln", "-sf", "/app/blueprint-skills/CLAUDE.md", "/app/agent-sdk-worker/CLAUDE.md"],
            check=True,
            capture_output=True,
        )
        logger.info("Symlinks created successfully")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Symlink creation failed (may already exist): {e}")

    # Initialize git repo for publishing (Wave 4.5)
    logger.info("Setting up git repo for GitHub Pages publishing...")
    try:
        github_token = os.environ.get("GITHUB_TOKEN", "")
        if github_token:
            subprocess.run(
                ["git", "init"],
                cwd="/app/agent-sdk-worker",
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "blueprint-worker@modal.com"],
                cwd="/app/agent-sdk-worker",
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Blueprint Worker"],
                cwd="/app/agent-sdk-worker",
                check=True,
                capture_output=True,
            )
            # Add remote for publishing playbooks
            subprocess.run(
                ["git", "remote", "add", "publish",
                 f"https://{github_token}@github.com/SantaJordan/blueprint-gtm-playbooks.git"],
                cwd="/app/agent-sdk-worker",
                check=True,
                capture_output=True,
            )
            logger.info("Git repo initialized with publish remote")
        else:
            logger.warning("GITHUB_TOKEN not found, skipping git setup")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Git setup failed: {e}")

    # Install npm dependencies
    logger.info("Installing npm dependencies...")
    try:
        subprocess.run(
            ["npm", "install"],
            cwd="/app/agent-sdk-worker",
            check=True,
            capture_output=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        logger.error("npm install timed out")
        return {"success": False, "error": "npm install timed out"}
    except subprocess.CalledProcessError as e:
        logger.error(f"npm install failed: {e.stderr.decode()}")
        return {"success": False, "error": f"npm install failed: {e.stderr.decode()[:500]}"}

    # Run the TypeScript worker via tsx
    logger.info("Running Agent SDK worker...")
    env = os.environ.copy()
    env["JOB_DATA"] = json.dumps(record)

    try:
        result = subprocess.run(
            ["npx", "tsx", "src/index.ts"],
            cwd="/app/agent-sdk-worker",
            env=env,
            capture_output=True,
            text=True,
            timeout=2400,  # 40 minutes
        )

        logger.info(f"Worker stdout (full): {result.stdout}")
        if result.stderr:
            logger.warning(f"Worker stderr: {result.stderr[-1000:]}")

        if result.returncode == 0:
            # Try to parse the JSON output
            try:
                # Look for JSON in the last few lines of output
                for line in reversed(result.stdout.strip().split("\n")):
                    line = line.strip()
                    if line.startswith("{") and "playbookUrl" in line:
                        output = json.loads(line)
                        logger.info(f"Job completed: {output}")
                        return output
            except json.JSONDecodeError:
                pass

            # If no JSON found, return success with last output
            return {"success": True, "output": result.stdout[-500:]}
        else:
            # Include both stdout and stderr in error for debugging
            error_msg = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            logger.error(f"Worker failed with code {result.returncode}: {error_msg[-2000:]}")
            return {"success": False, "error": error_msg[-3000:]}

    except subprocess.TimeoutExpired:
        logger.error("Worker execution timed out")
        return {"success": False, "error": "Execution timed out after 25 minutes"}
    except Exception as e:
        logger.error(f"Worker exception: {str(e)}")
        return {"success": False, "error": str(e)}


@app.function(
    image=image,
    secrets=secrets,
    timeout=1800,
    cpu=2,
    memory=4096,
    schedule=modal.Period(minutes=5),  # Poll every 5 minutes as backup
)
async def poll_pending_jobs():
    """
    Cron job to poll for pending jobs that weren't triggered by webhook.
    This is a backup in case the webhook fails.
    """
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("agent-sdk-worker-cron")

    logger.info("Polling for pending jobs...")

    # Create symlinks so Agent SDK can find .claude directory from worker's cwd
    try:
        subprocess.run(
            ["ln", "-sf", "/app/blueprint-skills/.claude", "/app/agent-sdk-worker/.claude"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["ln", "-sf", "/app/blueprint-skills/CLAUDE.md", "/app/agent-sdk-worker/CLAUDE.md"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        logger.warning(f"Symlink creation failed (may already exist): {e}")

    # Install npm dependencies
    try:
        subprocess.run(
            ["npm", "install"],
            cwd="/app/agent-sdk-worker",
            check=True,
            capture_output=True,
            timeout=120,
        )
    except Exception as e:
        logger.error(f"npm install failed: {e}")
        return {"success": False, "error": str(e)}

    # Run the worker in poll mode (no JOB_DATA = poll for oldest pending)
    env = os.environ.copy()

    try:
        result = subprocess.run(
            ["npx", "tsx", "src/index.ts"],
            cwd="/app/agent-sdk-worker",
            env=env,
            capture_output=True,
            text=True,
            timeout=1500,
        )

        logger.info(f"Poll result: {result.stdout[-500:]}")
        return {"success": result.returncode == 0, "output": result.stdout[-500:]}

    except Exception as e:
        logger.error(f"Poll exception: {e}")
        return {"success": False, "error": str(e)}


@app.local_entrypoint()
def main(job_id: str = None, url: str = None, poll: bool = False):
    """
    Local CLI for testing the Modal functions.

    Usage:
        modal run modal/wrapper.py --job-id <job-id>
        modal run modal/wrapper.py --url https://example.com
        modal run modal/wrapper.py --poll
    """
    import asyncio

    if url:
        # Create a mock job - use .local() for webhook functions
        result = asyncio.run(process_blueprint_job.local({
            "id": "test-" + str(hash(url))[:8],
            "company_url": url,
            "status": "pending",
        }))
        print(f"Result: {result}")
    elif job_id:
        result = asyncio.run(process_blueprint_job.local({
            "id": job_id,
            "company_url": "placeholder",  # Will be fetched from Supabase
            "status": "pending",
        }))
        print(f"Result: {result}")
    elif poll:
        result = poll_pending_jobs.remote()
        print(f"Poll result: {result}")
    else:
        print("Usage:")
        print("  modal run modal/wrapper.py --job-id <job-id>")
        print("  modal run modal/wrapper.py --url https://example.com")
        print("  modal run modal/wrapper.py --poll")


if __name__ == "__main__":
    # For local testing without Modal
    print("This script should be run via Modal:")
    print("  modal deploy modal/wrapper.py")
    print("  modal run modal/wrapper.py --help")
