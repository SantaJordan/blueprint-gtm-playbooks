#!/usr/bin/env python3
"""
Saha Health Email Finder
Find and verify emails for all 8,127 contacts using MillionVerifier
"""

import asyncio
import csv
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re
import unicodedata

import aiohttp

# ============================================================================
# Email Permutation Generator (inline to avoid import issues)
# ============================================================================

NAME_PREFIXES = {'mr', 'mrs', 'ms', 'dr', 'prof', 'rev'}
NAME_SUFFIXES = {'jr', 'sr', 'ii', 'iii', 'iv', 'phd', 'md', 'esq', 'cpa', 'do', 'dds', 'dvm', 'np', 'pa', 'rn'}


def normalize_text(text: str) -> str:
    """Remove accents and normalize unicode to ASCII"""
    if not text:
        return ""
    normalized = unicodedata.normalize('NFD', text)
    ascii_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return ascii_text.lower().strip()


def clean_name_part(name: str) -> str:
    """Clean a name part for use in email"""
    if not name:
        return ""
    name = normalize_text(name)
    name = re.sub(r'[^a-z0-9]', '', name)
    return name


def split_name(full_name: str) -> tuple[str, Optional[str]]:
    """Split full name into first and last name"""
    if not full_name:
        return "", None

    parts = full_name.strip().split()
    if not parts:
        return "", None

    # Remove prefixes
    while parts and parts[0].lower().rstrip('.') in NAME_PREFIXES:
        parts.pop(0)

    # Remove suffixes
    while parts and parts[-1].lower().rstrip('.,') in NAME_SUFFIXES:
        parts.pop()

    if len(parts) == 0:
        return "", None
    elif len(parts) == 1:
        return parts[0], None
    else:
        return parts[0], parts[-1]


def generate_email_permutations(full_name: str, domain: str) -> list[str]:
    """Generate email permutations from name and domain"""
    if not full_name or not domain:
        return []

    first_name, last_name = split_name(full_name)
    first_clean = clean_name_part(first_name)
    last_clean = clean_name_part(last_name) if last_name else None

    if len(first_clean) < 2:
        return []

    # Clean domain
    domain = domain.lower().strip()
    if domain.startswith(('http://', 'https://')):
        domain = domain.split('://', 1)[1]
    if domain.startswith('www.'):
        domain = domain[4:]
    domain = domain.rstrip('/')

    emails = []
    emails.append(f"{first_clean}@{domain}")

    if last_clean:
        first_initial = first_clean[0]
        patterns = [
            f"{last_clean}@{domain}",
            f"{first_clean}{last_clean}@{domain}",
            f"{first_clean}.{last_clean}@{domain}",
            f"{first_initial}{last_clean}@{domain}",
            f"{first_clean}{last_clean[0]}@{domain}",
            f"{first_initial}.{last_clean}@{domain}",
            f"{first_clean}_{last_clean}@{domain}",
        ]
        emails.extend(patterns)

    # Deduplicate
    seen = set()
    unique = []
    for email in emails:
        if email not in seen:
            seen.add(email)
            unique.append(email)

    return unique


# ============================================================================
# MillionVerifier Client (inline)
# ============================================================================

class EmailResult(Enum):
    OK = "ok"
    CATCH_ALL = "catch_all"
    UNKNOWN = "unknown"
    INVALID = "invalid"
    DISPOSABLE = "disposable"


class EmailQuality(Enum):
    GOOD = "good"
    RISKY = "risky"
    BAD = "bad"


@dataclass
class VerificationResult:
    email: str
    result: EmailResult
    quality: EmailQuality
    is_free: bool
    is_role: bool
    credits_remaining: int
    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return self.result == EmailResult.OK

    @property
    def is_deliverable(self) -> bool:
        return self.result in (EmailResult.OK, EmailResult.CATCH_ALL)


class MillionVerifierClient:
    BASE_URL = "https://api.millionverifier.com/api/v3/"

    def __init__(self, api_key: str, timeout_seconds: int = 30, max_concurrent: int = 10):
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
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
                            is_free=False, is_role=False, credits_remaining=data.get("credits", 0),
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
                        is_free=data.get("free", False),
                        is_role=data.get("role", False),
                        credits_remaining=data.get("credits", 0)
                    )

            except asyncio.TimeoutError:
                return VerificationResult(
                    email=email, result=EmailResult.UNKNOWN, quality=EmailQuality.BAD,
                    is_free=False, is_role=False, credits_remaining=0, error="timeout"
                )
            except Exception as e:
                return VerificationResult(
                    email=email, result=EmailResult.UNKNOWN, quality=EmailQuality.BAD,
                    is_free=False, is_role=False, credits_remaining=0, error=str(e)
                )

    async def verify_emails(self, emails: list[str]) -> list[VerificationResult]:
        tasks = [self.verify_email(email) for email in emails]
        return await asyncio.gather(*tasks)


# ============================================================================
# Main Email Finder
# ============================================================================

async def find_best_email(
    client: MillionVerifierClient,
    contact_name: str,
    domain: str
) -> tuple[Optional[str], Optional[str], list[dict]]:
    """
    Find and verify best email for a contact.
    Returns: (best_email, email_status, all_results)
    """
    permutations = generate_email_permutations(contact_name, domain)

    if not permutations:
        return None, "no_permutations", []

    results = await client.verify_emails(permutations)

    all_results = []
    best_email = None
    best_status = "not_found"
    best_score = -1

    for email, result in zip(permutations, results):
        result_dict = {
            "email": email,
            "result": result.result.value,
            "quality": result.quality.value,
            "is_role": result.is_role,
            "is_free": result.is_free
        }
        all_results.append(result_dict)

        # Score the result
        score = 0
        if result.result == EmailResult.OK:
            if result.quality == EmailQuality.GOOD:
                score = 100
            elif result.quality == EmailQuality.RISKY:
                score = 70
            else:
                score = 50
        elif result.result == EmailResult.CATCH_ALL:
            score = 40

        # Penalty for role accounts
        if result.is_role:
            score -= 20

        if score > best_score:
            best_score = score
            best_email = email
            best_status = result.result.value

    if best_score <= 0:
        return None, "not_found", all_results

    return best_email, best_status, all_results


async def process_contacts(input_file: str, output_file: str, api_key: str):
    """Process all contacts and find emails"""

    # Read contacts
    print(f"Reading contacts from {input_file}...")
    contacts = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            contacts.append(row)

    print(f"Found {len(contacts)} contacts")

    # Initialize client
    client = MillionVerifierClient(api_key=api_key, max_concurrent=10)

    # Process contacts
    results = []
    checkpoint_file = output_file.replace('.csv', '_checkpoint.json')

    # Load checkpoint if exists
    start_idx = 0
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
            results = checkpoint.get('results', [])
            start_idx = checkpoint.get('last_idx', 0) + 1
            print(f"Resuming from checkpoint at index {start_idx}")

    try:
        for i, contact in enumerate(contacts[start_idx:], start=start_idx):
            contact_name = contact.get('contact_name', '')
            domain = contact.get('website', '')
            practice = contact.get('practice_name', '')

            print(f"[{i+1}/{len(contacts)}] {contact_name} @ {domain}", end=" ", flush=True)

            if not contact_name or not domain:
                print("-> SKIP (missing data)")
                contact['email'] = ''
                contact['email_status'] = 'missing_data'
                results.append(contact)
                continue

            # Find best email
            best_email, status, all_results = await find_best_email(client, contact_name, domain)

            if best_email:
                print(f"-> {best_email} ({status})")
                contact['email'] = best_email
                contact['email_status'] = status
            else:
                print(f"-> NOT FOUND")
                contact['email'] = ''
                contact['email_status'] = status

            results.append(contact)

            # Checkpoint every 100 contacts
            if (i + 1) % 100 == 0:
                print(f"\n  Saving checkpoint at {i+1}...")
                with open(checkpoint_file, 'w') as f:
                    json.dump({'last_idx': i, 'results': results}, f)

                # Also write interim CSV
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)
                print(f"  Checkpoint saved. Credits remaining: checking...")

            # Small delay
            await asyncio.sleep(0.05)

    finally:
        await client.close()

    # Write final results
    print(f"\nWriting {len(results)} contacts to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Remove checkpoint file
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)

    # Summary
    found_ok = sum(1 for r in results if r.get('email_status') == 'ok')
    found_catch_all = sum(1 for r in results if r.get('email_status') == 'catch_all')
    not_found = sum(1 for r in results if r.get('email_status') in ('not_found', 'no_permutations', 'missing_data'))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total contacts: {len(results)}")
    print(f"Emails found (verified OK): {found_ok} ({found_ok/len(results)*100:.1f}%)")
    print(f"Catch-all emails: {found_catch_all} ({found_catch_all/len(results)*100:.1f}%)")
    print(f"Not found: {not_found} ({not_found/len(results)*100:.1f}%)")
    print(f"\nResults saved to: {output_file}")


async def main():
    api_key = os.environ.get('MILLIONVERIFIER_API_KEY')
    if not api_key:
        print("ERROR: MILLIONVERIFIER_API_KEY not set")
        sys.exit(1)

    # File paths
    input_file = "/Users/jordan/Desktop/Claude Code/Saha Health (sahahealth.ai)/contacts.csv"
    output_file = "/Users/jordan/Desktop/Claude Code/Saha Health (sahahealth.ai)/contacts_with_emails.csv"

    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    print("=" * 60)
    print("Saha Health Email Finder")
    print("=" * 60)
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print()

    await process_contacts(input_file, output_file, api_key)


if __name__ == '__main__':
    asyncio.run(main())
