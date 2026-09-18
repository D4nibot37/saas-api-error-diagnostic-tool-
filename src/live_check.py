"""
live_check.py
---------------
OPTIONAL bonus module: performs a real HTTP request against a target
endpoint using the `requests` library, and feeds the actual response into
the same diagnostic engine used for the static dataset.

This demonstrates combining a documented "runbook" knowledge base with live
API interaction - a core part of real SaaS/CRM technical support work.

Usage (from the project root):
    python src/diagnostic_tool.py --live-check https://httpstat.us/429 --system HubSpot

Note: requires internet access and the `requests` library
(pip install -r requirements.txt). This module is not exercised by the
default demo so the core tool works fully offline.
"""

import requests


def check_live_endpoint(url: str, timeout: int = 10) -> dict:
    """
    Sends a GET request to `url` and returns a dict shaped so it can be
    passed straight into ErrorCatalog.find_best_match(http_code=..., message=...).
    """
    try:
        response = requests.get(url, timeout=timeout)
        return {
            "http_code": response.status_code,
            "message": response.reason or "",
            "headers": dict(response.headers),
            "ok": response.ok,
        }
    except requests.exceptions.RequestException as exc:
        return {
            "http_code": None,
            "message": f"Request failed: {exc}",
            "headers": {},
            "ok": False,
        }
