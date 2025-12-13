#!/usr/bin/env python3
"""
Run MillionVerifier on all emails found in contact-finder output files.
Extracts emails from JSON files and verifies them.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import aiohttp


class EmailResult(Enum):
    """MillionVerifier result codes"""
    OK = "ok"
    CATCH_ALL = "catch_all"
    UNKNOWN = "unknown"
    INVALID = "invalid"
    DISPOSABLE = "disposable"


class EmailQuality(Enum):
    """MillionVerifier quality assessment"""
    GOOD = "good"
    RISKY = "risky"
    BAD = "bad"


@dataclass
class VerificationResult:
    """Result from MillionVerifier API"""
    email: str
    result: EmailResult
    quality: EmailQuality
    resultcode: int
    is_free: bool
    is_role: bool
    did_you_mean: Optional[str]
    credits_remaining: int
    execution_time_seconds: float
    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return self.result == EmailResult.OK

    @property
    def is_deliverable(self) -> bool:
        return self.result in (EmailResult.OK, EmailResult.CATCH_ALL)

    @property
    def confidence_score(self) -> int:
        if self.result == EmailResult.OK:
            if self.quality == EmailQuality.GOOD:
                return 100
            elif self.quality == EmailQuality.RISKY:
                return 70
            else:
                return 50
        elif self.result == EmailResult.CATCH_ALL:
            return 60
        elif self.result == EmailResult.UNKNOWN:
            return 30
        else:
            return 0


class MillionVerifierClient:
    """Client for MillionVerifier Single API"""

    BASE_URL = "https://api.millionverifier.com/api/v3/"

    def __init__(self, api_key: str, timeout_seconds: int = 20, max_concurrent: int = 10):
        self.api_key = api_key
        self.timeout_seconds = max(2, min(60, timeout_seconds))
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds + 5)
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_credits(self) -> int:
        session = await self._get_session()
        try:
            async with session.get(
                "https://api.millionverifier.com/api/v3/credits",
                params={"api": self.api_key}
            ) as response:
                data = await response.json()
                return data.get("credits", 0)
        except Exception:
            return 0

    async def verify_email(self, email: str) -> VerificationResult:
        async with self._semaphore:
            session = await self._get_session()

            params = {
                "api": self.api_key,
                "email": email.lower().strip(),
                "timeout": self.timeout_seconds
            }

            try:
                async with session.get(self.BASE_URL, params=params) as response:
                    data = await response.json()

                    if data.get("error"):
                        return VerificationResult(
                            email=email, result=EmailResult.UNKNOWN, quality=EmailQuality.BAD,
                            resultcode=0, is_free=False, is_role=False, did_you_mean=None,
                            credits_remaining=data.get("credits", 0),
                            execution_time_seconds=data.get("executiontime", 0),
                            error=data.get("error")
                        )

                    result_str = data.get("result", "unknown").lower()
                    try:
                        result = EmailResult(result_str)
                    except ValueError:
                        result = EmailResult.UNKNOWN

                    quality_str = data.get("quality", "bad").lower()
                    try:
                        quality = EmailQuality(quality_str)
                    except ValueError:
                        quality = EmailQuality.BAD

                    return VerificationResult(
                        email=data.get("email", email),
                        result=result,
                        quality=quality,
                        resultcode=data.get("resultcode", 0),
                        is_free=data.get("free", False),
                        is_role=data.get("role", False),
                        did_you_mean=data.get("didyoumean") or None,
                        credits_remaining=data.get("credits", 0),
                        execution_time_seconds=data.get("executiontime", 0)
                    )

            except asyncio.TimeoutError:
                return VerificationResult(
                    email=email, result=EmailResult.UNKNOWN, quality=EmailQuality.BAD,
                    resultcode=0, is_free=False, is_role=False, did_you_mean=None,
                    credits_remaining=0, execution_time_seconds=self.timeout_seconds,
                    error="timeout"
                )
            except Exception as e:
                return VerificationResult(
                    email=email, result=EmailResult.UNKNOWN, quality=EmailQuality.BAD,
                    resultcode=0, is_free=False, is_role=False, did_you_mean=None,
                    credits_remaining=0, execution_time_seconds=0,
                    error=str(e)
                )


async def extract_emails_from_json(file_path: Path) -> list[dict]:
    """Extract all emails with context from a JSON file."""
    emails = []

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  Error reading {file_path.name}: {e}")
        return []

    # Handle different JSON structures
    if isinstance(data, list):
        results = data
    else:
        results = data.get('results', [])

    for result in results:
        company_name = result.get('company_name', 'Unknown')
        domain = result.get('domain', '')

        # Check contacts array
        contacts = result.get('contacts', [])
        for contact in contacts:
            email = contact.get('email')
            if email and '@' in email:
                emails.append({
                    'email': email.lower().strip(),
                    'company_name': company_name,
                    'domain': domain,
                    'contact_name': contact.get('name'),
                    'contact_title': contact.get('title'),
                    'source_file': file_path.name
                })

        # Also check top-level email fields
        if 'contact_email' in result and result['contact_email']:
            email = result['contact_email']
            if '@' in email:
                emails.append({
                    'email': email.lower().strip(),
                    'company_name': company_name,
                    'domain': domain,
                    'contact_name': result.get('contact_name'),
                    'contact_title': result.get('contact_title'),
                    'source_file': file_path.name
                })

    return emails


async def scan_for_emails(base_path: Path) -> list[dict]:
    """Scan all JSON files in contact-finder output folders for emails."""
    all_emails = []
    seen_emails = set()

    # Directories to scan
    scan_dirs = [
        base_path / 'evaluation' / 'results',
        base_path / 'evaluation' / 'data',
        base_path / 'evaluation' / 'data' / 'pipeline_results',
    ]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue

        print(f"\nScanning: {scan_dir}")

        for json_file in scan_dir.glob('*.json'):
            emails = await extract_emails_from_json(json_file)

            for email_data in emails:
                email = email_data['email']
                if email not in seen_emails:
                    seen_emails.add(email)
                    all_emails.append(email_data)

            if emails:
                print(f"  Found {len(emails)} emails in {json_file.name}")

    return all_emails


async def verify_emails(emails: list[dict], api_key: str) -> list[dict]:
    """Verify all emails using MillionVerifier."""

    client = MillionVerifierClient(
        api_key=api_key,
        timeout_seconds=30,
        max_concurrent=10
    )

    valid_emails = []
    results_all = []

    try:
        print(f"\nVerifying {len(emails)} emails with MillionVerifier...")

        # Get initial credits
        credits = await client.get_credits()
        print(f"Available credits: {credits}")

        if credits < len(emails):
            print(f"WARNING: Not enough credits ({credits}) for all emails ({len(emails)})")

        for i, email_data in enumerate(emails):
            email = email_data['email']

            print(f"[{i+1}/{len(emails)}] Verifying: {email}", end=" ")

            result = await client.verify_email(email)

            email_data['verification_result'] = result.result.value
            email_data['verification_quality'] = result.quality.value
            email_data['verification_confidence'] = result.confidence_score
            email_data['is_valid'] = result.is_valid
            email_data['is_deliverable'] = result.is_deliverable
            email_data['is_free'] = result.is_free
            email_data['is_role'] = result.is_role
            email_data['did_you_mean'] = result.did_you_mean

            results_all.append(email_data)

            status = "✓ VALID" if result.is_valid else ("⚠ CATCH-ALL" if result.result == EmailResult.CATCH_ALL else "✗ INVALID")
            print(f"-> {status} ({result.quality.value})", flush=True)

            if result.is_valid or result.result == EmailResult.CATCH_ALL:
                valid_emails.append(email_data)

            # Small delay between requests
            await asyncio.sleep(0.1)

        print(f"\nCredits remaining: {result.credits_remaining}")

    finally:
        await client.close()

    return valid_emails, results_all


async def main():
    # Get API key
    api_key = os.environ.get('MILLIONVERIFIER_API_KEY')
    if not api_key:
        print("ERROR: MILLIONVERIFIER_API_KEY not set")
        print("Usage: MILLIONVERIFIER_API_KEY=your_key python run_millionverifier.py")
        sys.exit(1)

    # Find base path
    base_path = Path(__file__).parent.parent

    print("=" * 60)
    print("MillionVerifier Email Validation")
    print("=" * 60)

    # Extract emails
    emails = await scan_for_emails(base_path)

    if not emails:
        print("\nNo emails found to verify!")
        sys.exit(0)

    print(f"\nTotal unique emails found: {len(emails)}")

    # Verify emails
    valid_emails, all_results = await verify_emails(emails, api_key)

    # Output results
    print("\n" + "=" * 60)
    print("VALID EMAILS (deliverable)")
    print("=" * 60)

    for email_data in valid_emails:
        print(f"\n{email_data['email']}")
        print(f"  Company: {email_data['company_name']}")
        if email_data.get('contact_name'):
            print(f"  Contact: {email_data['contact_name']}")
        if email_data.get('contact_title'):
            print(f"  Title: {email_data['contact_title']}")
        print(f"  Result: {email_data['verification_result']} ({email_data['verification_quality']})")

    # Save results
    output_file = base_path / 'contact-finder' / f'millionverifier_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_emails': len(emails),
            'valid_emails': len(valid_emails),
            'valid_rate': f"{len(valid_emails)/len(emails)*100:.1f}%" if emails else "0%",
            'valid': valid_emails,
            'all_results': all_results
        }, f, indent=2)

    print(f"\n\nResults saved to: {output_file}")
    print(f"\nSummary:")
    print(f"  Total emails: {len(emails)}")
    print(f"  Valid emails: {len(valid_emails)}")
    print(f"  Valid rate: {len(valid_emails)/len(emails)*100:.1f}%" if emails else "N/A")


if __name__ == '__main__':
    asyncio.run(main())
