"""
error_catalog.py
------------------
Loads and queries the catalog of known SaaS/CRM API errors.

This module is responsible for:
1. Loading the error dataset from data/error_catalog.json
2. Finding the most likely known error given an HTTP status code, a free-text
   error message, and optional context (source system: Salesforce, HubSpot...)

The goal is to keep this simple enough to explain line-by-line in an
interview: no external NLP library, no black-box logic - just a transparent,
explainable scoring rule you could describe on a whiteboard.
"""

import json
import os
from dataclasses import dataclass
from typing import List, Optional


DEFAULT_CATALOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "error_catalog.json"
)


@dataclass
class ErrorMatch:
    """A single catalog entry matched against a reported error, with a confidence score."""

    id: str
    http_code: Optional[int]
    error_type: str
    name: str
    systems: List[str]
    probable_causes: List[str]
    resolution_steps: List[str]
    automated_action: Optional[str]
    severity: str
    runbook: str
    confidence: float = 0.0


class ErrorCatalog:
    """Loads data/error_catalog.json and matches incoming errors against it."""

    def __init__(self, catalog_path: str = DEFAULT_CATALOG_PATH):
        self.catalog_path = catalog_path
        self.errors = self._load_catalog()

    def _load_catalog(self) -> list:
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("errors", [])

    def find_best_match(
        self,
        http_code: Optional[int] = None,
        message: str = "",
        system: Optional[str] = None,
    ) -> Optional[ErrorMatch]:
        """
        Find the catalog entry that best matches a reported error.

        Scoring rule (simple and transparent on purpose):
          +3 points if the HTTP status code matches exactly
          +2 points for each catalog keyword found inside the message (case-insensitive)
          +1 point if the reported system (Salesforce/HubSpot/...) matches

        Returns an ErrorMatch, or None if nothing scores above zero.
        """
        message_lower = (message or "").lower()
        best_entry = None
        best_score = 0

        for entry in self.errors:
            score = 0

            if http_code is not None and entry.get("http_code") == http_code:
                score += 3

            for keyword in entry.get("keywords", []):
                if keyword.lower() in message_lower:
                    score += 2

            if system:
                entry_systems_lower = [s.lower() for s in entry.get("systems", [])]
                if system.lower() in entry_systems_lower:
                    score += 1

            if score > best_score:
                best_score = score
                best_entry = entry

        if best_entry is None or best_score == 0:
            return None

        # Rough 0-1 confidence normalization for display purposes only.
        confidence = min(best_score / 6, 1.0)

        return ErrorMatch(
            id=best_entry["id"],
            http_code=best_entry.get("http_code"),
            error_type=best_entry.get("error_type", "unknown"),
            name=best_entry["name"],
            systems=best_entry.get("systems", []),
            probable_causes=best_entry.get("probable_causes", []),
            resolution_steps=best_entry.get("resolution_steps", []),
            automated_action=best_entry.get("automated_action"),
            severity=best_entry.get("severity", "medium"),
            runbook=best_entry.get("runbook", ""),
            confidence=confidence,
        )

    def list_all(self) -> list:
        """Return every raw entry in the catalog (useful for a future dashboard/export)."""
        return self.errors
