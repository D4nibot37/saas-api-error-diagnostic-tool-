# Runbook: 404 Not Found - Record or Resource Missing

**Catalog ID:** `ERR-404-NOTFOUND` · **Severity:** Low · **Automated action:** none (needs verification)

## Summary
The API could not find the resource referenced by the request - most often a
record ID that doesn't exist (any more) in the target environment, or a
mistyped endpoint URL.

## Common Causes
1. The referenced record ID no longer exists (deleted or merged into another record)
2. A typo or incorrect ID/URL in the request (wrong object API name or endpoint version)
3. The record exists in a different environment than the one being queried (sandbox vs production)
4. The record is not visible to the API user due to sharing rules (some APIs return 404 instead of 403 to avoid leaking that a hidden record exists)

## Diagnostic Checklist
- [ ] Double-check the record ID being sent - copy/paste it directly rather than retyping it
- [ ] Confirm the endpoint URL and API version match current provider documentation
- [ ] Search for the record by an alternate identifier (email, external ID) to see if it still exists under a different record ID
- [ ] Confirm which environment (production vs. sandbox) the request is actually hitting
- [ ] If the requesting user has limited sharing/visibility, ask an admin to check if the record exists but is simply hidden from that user

## Resolution Steps
1. If the record was deleted, decide whether it should be recreated or whether downstream processes should simply skip it
2. If the record was merged into another one, update any stored references to point at the surviving record's ID
3. Fix the endpoint URL/API version if that was the actual cause
4. Confirm the environment and re-point the integration if it was pointed at the wrong one
5. If it's a sharing/visibility issue, treat it as a permissions problem instead (see the 403 runbook) and escalate to an admin

## Prevention
- Avoid hardcoding record IDs where possible; look records up by a stable external ID/email instead
- Subscribe to (or poll) deletion/merge events where the provider supports them, so your integration can react instead of failing silently later
- Log the full request URL (not just the response) so 404s are easy to root-cause after the fact

## System-Specific Notes

### Salesforce
Salesforce record IDs come in 15 or 18-character variants (case-sensitive vs. case-insensitive).
A 404 can also happen if you query the 15-character ID against an endpoint expecting the
18-character version, or vice versa - always store and pass the 18-character ID from the API.

### HubSpot
HubSpot object IDs are numeric and object-type specific (a contact ID and a deal ID can be the
same number). A 404 often means the ID was sent to the wrong object endpoint (e.g. a deal ID
sent to `/crm/v3/objects/contacts/{id}`).
