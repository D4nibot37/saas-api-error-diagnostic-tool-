# Runbook: 429 Too Many Requests - Rate Limit Exceeded

**Catalog ID:** `ERR-429-RATELIMIT` · **Severity:** Medium · **Automated action:** `retry_with_backoff`

## Summary
The integration sent more requests than the API allows in a given window.
This is rarely a "break glass" emergency - it's a traffic-shaping problem,
and it's usually self-resolving if the client backs off correctly.

## Common Causes
1. The integration exceeded the API's request-per-second or request-per-day limit
2. A bulk sync/import job is firing requests without batching or throttling
3. Multiple integrations/processes sharing the same API credentials are competing for the same quota
4. No backoff strategy is implemented, so repeated immediate retries make the limit worse instead of recovering from it

## Diagnostic Checklist
- [ ] Check the `Retry-After` header (or the provider's equivalent) on the 429 response
- [ ] Review recent request volume - was there a bulk job, a backfill, or a burst of traffic right before this started?
- [ ] Confirm whether other integrations share the same API credentials/app and could be consuming the same quota
- [ ] Check the provider's dashboard for current API usage against your plan's limit

## Resolution Steps
1. Wait the amount of time indicated by `Retry-After` (or a sensible default like a few seconds) before retrying
2. Implement exponential backoff with jitter for the retry loop - never retry immediately in a tight loop
3. Switch bulk operations to the provider's bulk/batch endpoints where available (e.g. Salesforce Bulk API, HubSpot batch endpoints), which count against limits very differently than single-record calls
4. If usage is consistently near the limit even with sane batching, request a rate limit increase from the provider
5. Add request throttling/queueing so the integration proactively stays under the limit instead of reacting to 429s

## Prevention
- Track request counts client-side against the known limit so you throttle before hitting 429, not after
- Prefer bulk/batch endpoints for any operation touching more than a handful of records
- Stagger scheduled jobs (syncs, backfills) so they don't all fire in the same time window

## System-Specific Notes

### Salesforce
Salesforce enforces both a rolling per-24-hour API call limit (based on your org's edition/licenses)
and, in some cases, concurrent request limits. For large data volumes, the Bulk API is designed
specifically to avoid burning through the standard REST API limit.

### HubSpot
HubSpot enforces both a per-second and a daily limit per app/account tier. The response includes
`X-HubSpot-RateLimit-Remaining` and similar headers - checking these proactively lets you throttle
before you actually get a 429.
