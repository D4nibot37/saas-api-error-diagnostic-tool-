"""
resolvers.py
-------------
Simple simulations of automated resolution actions.

IMPORTANT: these functions SIMULATE behaviour (they do not call real
Salesforce/HubSpot APIs) so the project can be run by anyone - including a
recruiter - without needing live credentials. The point is to demonstrate the
REASONING and the resolution PATTERN (retry with backoff, payload validation,
token refresh), which is exactly what is expected from a SaaS/CRM technical
support role, not to ship a production integration.
"""

import random
from typing import Dict, List


def simulate_retry_with_backoff(
    max_retries: int = 4, base_delay: int = 1, simulate_success_on: int = 3
) -> Dict:
    """
    Simulates an exponential backoff retry strategy, typically used for
    429 (rate limit) or transient 5xx errors.

    - base_delay: initial wait time in seconds (doubles on each attempt)
    - simulate_success_on: the attempt number on which the request "succeeds"

    Real sleeping is intentionally skipped (commented out) so the demo runs
    instantly; in production code you would call time.sleep(delay).
    """
    log: List[str] = []
    for attempt in range(1, max_retries + 1):
        delay = base_delay * (2 ** (attempt - 1))
        log.append(f"Attempt {attempt}/{max_retries} - waiting {delay}s before retrying...")
        # time.sleep(delay)  # disabled so the demo output is instant

        if attempt >= simulate_success_on:
            log.append(f"Attempt {attempt}: request succeeded (200 OK - simulated)")
            return {"success": True, "attempts": attempt, "log": log}

        log.append(f"Attempt {attempt}: 429 Too Many Requests (simulated)")

    log.append("Retries exhausted. Escalate for manual review or request a higher rate limit from the provider.")
    return {"success": False, "attempts": max_retries, "log": log}


def simulate_payload_validation(payload: dict, required_fields: List[str]) -> Dict:
    """
    Simulates validating a payload before (re)sending it - typical for 400
    Bad Request errors caused by incomplete or malformed data.
    """
    errors: List[str] = []

    for field_name in required_fields:
        if field_name not in payload or payload[field_name] in (None, ""):
            errors.append(f"Required field missing or empty: '{field_name}'")

    email = payload.get("email")
    if email and "@" not in email:
        errors.append(f"Invalid email format: '{email}'")

    return {"valid": not errors, "errors": errors}


def simulate_token_refresh() -> Dict:
    """Simulates an OAuth2 refresh-token flow, typical for resolving 401 errors."""
    new_token = f"tok_{random.randint(100000, 999999)}_refreshed"
    return {
        "success": True,
        "new_token": new_token,
        "expires_in_minutes": 60,
        "message": "Token refreshed successfully via the OAuth2 refresh_token flow.",
    }
