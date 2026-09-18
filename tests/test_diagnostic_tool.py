"""
test_diagnostic_tool.py
--------------------------
Basic unit tests for the matching engine and the resolution simulators.

Run with:
    python -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from error_catalog import ErrorCatalog
from resolvers import simulate_payload_validation, simulate_retry_with_backoff, simulate_token_refresh


class TestErrorCatalog(unittest.TestCase):
    def setUp(self):
        self.catalog = ErrorCatalog()

    def test_catalog_loads_entries(self):
        self.assertGreaterEqual(len(self.catalog.list_all()), 8)

    def test_matches_401_by_http_code(self):
        match = self.catalog.find_best_match(http_code=401, message="")
        self.assertIsNotNone(match)
        self.assertEqual(match.http_code, 401)
        self.assertEqual(match.id, "ERR-401-TOKEN")

    def test_matches_429_by_keyword_without_code(self):
        match = self.catalog.find_best_match(http_code=None, message="Too many requests, rate limit hit")
        self.assertIsNotNone(match)
        self.assertEqual(match.http_code, 429)

    def test_system_context_breaks_ties_in_favor_of_expected_entry(self):
        match = self.catalog.find_best_match(http_code=403, message="", system="Salesforce")
        self.assertIsNotNone(match)
        self.assertEqual(match.id, "ERR-403-PERMISSIONS")

    def test_sync_error_matches_by_keyword_with_no_http_code(self):
        match = self.catalog.find_best_match(http_code=None, message="Duplicate contact detected during sync")
        self.assertIsNotNone(match)
        self.assertEqual(match.error_type, "synchronization")
        self.assertEqual(match.id, "ERR-SYNC-DUPLICATE")

    def test_no_match_returns_none(self):
        match = self.catalog.find_best_match(http_code=999, message="totally unrelated unknown text")
        self.assertIsNone(match)


class TestResolvers(unittest.TestCase):
    def test_payload_validation_flags_missing_fields(self):
        result = simulate_payload_validation({"email": "", "name": ""}, required_fields=["name", "email"])
        self.assertFalse(result["valid"])
        self.assertEqual(len(result["errors"]), 2)

    def test_payload_validation_flags_bad_email_format(self):
        result = simulate_payload_validation({"name": "Ana", "email": "ana-at-example.com"}, required_fields=["name", "email"])
        self.assertFalse(result["valid"])
        self.assertTrue(any("email" in e.lower() for e in result["errors"]))

    def test_payload_validation_passes_valid_payload(self):
        result = simulate_payload_validation({"name": "Ana", "email": "ana@example.com"}, required_fields=["name", "email"])
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_retry_with_backoff_eventually_succeeds(self):
        result = simulate_retry_with_backoff(max_retries=4, simulate_success_on=2)
        self.assertTrue(result["success"])
        self.assertEqual(result["attempts"], 2)

    def test_retry_with_backoff_can_exhaust_retries(self):
        result = simulate_retry_with_backoff(max_retries=2, simulate_success_on=5)
        self.assertFalse(result["success"])
        self.assertEqual(result["attempts"], 2)

    def test_token_refresh_returns_new_token(self):
        result = simulate_token_refresh()
        self.assertTrue(result["success"])
        self.assertTrue(result["new_token"].startswith("tok_"))


if __name__ == "__main__":
    unittest.main()
