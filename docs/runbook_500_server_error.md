# Runbook: 500 Internal Server Error - Provider-Side Failure

**Catalog ID:** `ERR-500-SERVER` · **Severity:** Medium · **Automated action:** `retry_with_backoff`

## Summary
The provider's own infrastructure failed to process an otherwise valid
request. Unlike 4xx errors, this is not something the integration did wrong -
it needs patience and, if it persists, a support ticket with the provider.

## Common Causes
1. Temporary issue on the provider's side (outage, deployment, degraded service)
2. An edge case in the request triggered an unhandled error server-side
3. Timeout on a very large or complex request

## Diagnostic Checklist
- [ ] Check the provider's public status page for an active incident
- [ ] Confirm the request itself is well-formed (rule out that this is really a disguised 400)
- [ ] Check whether the error correlates with unusually large payloads or batch sizes
- [ ] Note the request ID/timestamp from the response for a support ticket if needed

## Resolution Steps
1. Retry with exponential backoff - most 5xx errors are transient and resolve within seconds to minutes
2. If retries consistently fail, check the provider's status page before doing anything else
3. If there's no reported incident and the error is reproducible, open a support ticket including the request ID, timestamp, and exact payload
4. If the error correlates with large/complex requests, try splitting the operation into smaller batches as a workaround

## Prevention
- Always wrap outbound calls in retry-with-backoff logic, since 5xx errors are an expected (if infrequent) part of any distributed system
- Subscribe to the provider's status page/incident notifications so the team knows immediately when it's a known outage
- Keep payload sizes reasonable and use bulk endpoints designed for large volumes, rather than one very large single request

## System-Specific Notes

### Salesforce
Check `status.salesforce.com` for your instance. Persistent 500s tied to a specific Apex-based
custom endpoint may indicate an unhandled exception in custom code on the Salesforce side -
worth flagging to whoever owns that Apex class/trigger.

### HubSpot
Check `status.hubspot.com`. If the error is isolated to one specific object/record, it can be
worth testing the same operation on a different record to rule out corrupted data on that one
record before escalating as a platform-wide issue.
