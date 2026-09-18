# Runbook: Sync Error - Duplicate Record Conflict

**Catalog ID:** `ERR-SYNC-DUPLICATE` · **Severity:** Medium · **Automated action:** none (needs manual merge)

## Summary
A two-way (or one-way) CRM sync - the classic example being a
HubSpot-Salesforce integration - detects that the same real-world contact or
lead exists as two separate records, one in each system (or twice in the
same system), and refuses to sync blindly to avoid overwriting good data
with the wrong record.

## Common Causes
1. The same contact/lead was created independently in both systems before the sync connection existed
2. The matching/dedupe field (usually email) has inconsistent formatting between systems - case, extra whitespace, personal vs. work email aliases
3. Deduplication rules are misconfigured or disabled in the sync tool
4. A record was merged in one system but the merge has not yet propagated to the other system

## Diagnostic Checklist
- [ ] Identify the matching/dedupe key the sync tool actually uses (almost always email, sometimes a custom external ID)
- [ ] Pull up both candidate records side by side and compare the matching field exactly, including case and whitespace
- [ ] Check the sync tool's logs for the specific duplicate/conflict entry and note which two record IDs are involved
- [ ] Check if either record was recently merged, and if the merge already reached the other system

## Resolution Steps
1. Confirm which of the two records has more complete/authoritative/recent data
2. Merge the duplicates in the system where merging is supported (usually the CRM of record), keeping the better record
3. Update the matching field on both surviving records to be identical and normalized (trim whitespace, consistent casing)
4. Re-run the sync for the affected record so it reconciles cleanly against the merged record
5. If this is a recurring pattern, review and tighten the sync tool's dedupe rules rather than just fixing this one instance

## Prevention
- Normalize the matching field (lowercase, trimmed) at the point of data entry, not just at sync time
- Turn on stricter automatic deduplication in the sync tool where safe to do so
- Establish a clear "system of record" policy so new records are always created in one place first, then synced outward

## System-Specific Notes

### HubSpot-Salesforce sync
HubSpot's native Salesforce integration and most third-party sync tools (e.g. Zapier, native
connectors) match primarily on email by default. If your org routinely uses secondary/personal
emails for the same contact, consider syncing on a custom external ID field instead of relying
solely on email matching.
