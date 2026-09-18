#!/usr/bin/env python3
"""
diagnostic_tool.py
---------------------
Command-line diagnostic tool for common API errors in SaaS/CRM environments
(Salesforce, HubSpot, and generic REST APIs).

Given an HTTP status code, an error message and (optionally) the source
system, it:
  1. Diagnoses the most probable cause using a small, explainable catalog
  2. Prints clear, actionable resolution steps (a runbook, not just a label)
  3. Optionally simulates a resolution action (retry with backoff, payload
     validation, token refresh) so the tool demonstrates troubleshooting AND
     resolution, not just classification

Quick usage:
    python src/diagnostic_tool.py --demo
    python src/diagnostic_tool.py --code 429 --message "Rate limit exceeded" --system HubSpot --resolve
    python src/diagnostic_tool.py --code 400 --message "Missing required field: email" --resolve
    python src/diagnostic_tool.py --message "Duplicate contact detected during sync"
    python src/diagnostic_tool.py --live-check https://httpstat.us/429 --resolve
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from error_catalog import ErrorCatalog, ErrorMatch
from resolvers import (
    simulate_payload_validation,
    simulate_retry_with_backoff,
    simulate_token_refresh,
)

SEPARATOR = "=" * 60


def print_diagnosis(match: "ErrorMatch | None", http_code, message, system) -> None:
    """Pretty-prints the diagnosis for a single reported error."""
    print(SEPARATOR)
    print("DIAGNOSIS")
    print(SEPARATOR)
    print(f"Reported HTTP code : {http_code}")
    print(f"Reported message   : {message or '(none)'}")
    print(f"Source system      : {system or 'Not specified'}")
    print("-" * 60)

    if match is None:
        print("No clear match found in the catalog.")
        print("Next step: check the provider's official API documentation,")
        print("or add this case to data/error_catalog.json for next time.")
        print(SEPARATOR)
        return

    print(f"Identified error   : {match.name} ({match.id})")
    print(f"Severity           : {match.severity.upper()}")
    print(f"Match confidence   : {match.confidence * 100:.0f}%")
    print()
    print("PROBABLE CAUSES:")
    for i, cause in enumerate(match.probable_causes, 1):
        print(f"  {i}. {cause}")
    print()
    print("RESOLUTION STEPS (runbook):")
    for i, step in enumerate(match.resolution_steps, 1):
        print(f"  {i}. {step}")
    print()
    print(f"Full runbook       : {match.runbook}")
    print(SEPARATOR)


def attempt_resolution(match: "ErrorMatch | None", payload: dict | None = None) -> None:
    """Runs a simulated automated resolution action, if one is defined for this error."""
    if match is None or match.automated_action is None:
        print("\nNo automated action is defined for this error - it requires manual/admin review.")
        return

    print("\nSIMULATING AUTOMATED RESOLUTION")
    print("-" * 60)

    if match.automated_action == "refresh_token":
        result = simulate_token_refresh()
        print(result["message"])
        print(f"New token (simulated): {result['new_token']}")

    elif match.automated_action == "retry_with_backoff":
        result = simulate_retry_with_backoff()
        for line in result["log"]:
            print(line)
        print(f"\nFinal result: {'SUCCESS' if result['success'] else 'FAILED after retries'}")

    elif match.automated_action == "validate_payload":
        example_payload = payload or {"email": "invalid-email.com", "name": ""}
        result = simulate_payload_validation(example_payload, required_fields=["name", "email"])
        if result["valid"]:
            print("Payload is valid - safe to resend the request.")
        else:
            print("Payload is invalid. Issues found:")
            for err in result["errors"]:
                print(f"  - {err}")
            print("  -> Fix these fields before retrying the request.")

    else:
        print(f"Action '{match.automated_action}' is registered but not implemented in this demo.")

    print("-" * 60)


def run_demo(catalog: ErrorCatalog) -> None:
    """Runs a handful of realistic scenarios end-to-end - useful for a quick live demo."""
    scenarios = [
        {"code": 401, "message": "Invalid token: session expired", "system": "Salesforce"},
        {"code": 429, "message": "Rate limit exceeded, too many requests", "system": "HubSpot"},
        {"code": 400, "message": "Missing required field: email", "system": "HubSpot"},
        {"code": None, "message": "Duplicate contact record detected during sync", "system": None},
    ]

    for scenario in scenarios:
        match = catalog.find_best_match(
            http_code=scenario["code"], message=scenario["message"], system=scenario["system"]
        )
        print_diagnosis(match, scenario["code"], scenario["message"], scenario["system"])
        attempt_resolution(match)
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diagnose common API errors in SaaS/CRM environments (Salesforce, HubSpot, etc.)"
    )
    parser.add_argument("--code", type=int, default=None, help="HTTP status code (e.g. 401, 403, 429, 400, 404)")
    parser.add_argument("--message", type=str, default="", help="Reported error message")
    parser.add_argument("--system", type=str, default=None, help="Source system (Salesforce, HubSpot, etc.)")
    parser.add_argument("--resolve", action="store_true", help="Simulate an automated resolution attempt")
    parser.add_argument("--demo", action="store_true", help="Run a handful of example scenarios")
    parser.add_argument(
        "--live-check",
        dest="live_url",
        type=str,
        default=None,
        help="Perform a real GET request to this URL and diagnose the actual response (requires internet + requests)",
    )

    args = parser.parse_args()
    catalog = ErrorCatalog()

    if args.demo:
        run_demo(catalog)
        return

    if args.live_url:
        from live_check import check_live_endpoint

        live_result = check_live_endpoint(args.live_url)
        print(f"\nLive check: GET {args.live_url}")
        print(f"  -> HTTP {live_result['http_code']} ({live_result['message']})\n")

        match = catalog.find_best_match(
            http_code=live_result["http_code"], message=live_result["message"], system=args.system
        )
        print_diagnosis(match, live_result["http_code"], live_result["message"], args.system)
        if args.resolve:
            attempt_resolution(match)
        return

    if args.code is None and not args.message:
        parser.print_help()
        return

    match = catalog.find_best_match(http_code=args.code, message=args.message, system=args.system)
    print_diagnosis(match, args.code, args.message, args.system)

    if args.resolve:
        attempt_resolution(match)


if __name__ == "__main__":
    main()
