# Runbook: 403 Forbidden - Insufficient Permissions

**Catalog ID:** `ERR-403-PERMISSIONS` · **Severity:** Medium-High · **Automated action:** none (requires admin review)

## Summary
The API recognized who is making the request but refused to let them do it.
Unlike a 401, this is not fixed by getting a new token - it requires a
permission change, and that usually means involving a Salesforce/HubSpot
administrator.

## Common Causes
1. The API user/integration lacks permission for this object or action (e.g. a read-only user attempting a write)
2. The connected app's OAuth scopes do not include the required permission
3. IP restrictions on the org are blocking requests from this server's IP address
4. The integration user's profile or permission set was recently changed or revoked
5. Attempting to access a record outside the user's sharing rules (record-level security)

## Diagnostic Checklist
- [ ] Confirm exactly which object and action failed (read vs. create vs. update vs. delete)
- [ ] Check whether the same request works for a different, higher-privileged user - isolates a permissions vs. a data problem
- [ ] Review recent changes to the integration user's profile/permission set/role
- [ ] Check if IP allow-listing is enabled on the org and whether the calling server's IP changed recently
- [ ] Review the OAuth scopes actually granted to the connected app/private app

## Resolution Steps
1. Identify the precise permission required (object-level CRUD, field-level security, or a specific API scope)
2. Escalate to a Salesforce/HubSpot administrator with the exact object, action, and error message
3. Have the admin grant the missing permission via profile/permission set (Salesforce) or app scopes (HubSpot)
4. If IP restrictions are the cause, add the integration server's IP to the allow-list
5. If OAuth scopes changed, re-run the authorization flow so the token reflects the new scopes
6. Retry the original request once permissions are confirmed updated

## Prevention
- Use a dedicated integration user with only the permissions the integration actually needs (least privilege), documented clearly so future permission changes don't silently break it
- Keep a checklist of required scopes/permissions per integration so a re-authorization always requests the full correct set
- Add a scheduled "canary" request that exercises key permissions daily, to catch permission drift before it affects real syncs

## System-Specific Notes

### Salesforce
Look for `INSUFFICIENT_ACCESS_OR_READONLY` in the error body - this can be an object permission,
a field-level security restriction, or a sharing rule blocking access to a *specific* record even
though the object-level permission is fine. Check all three before assuming it's a broad access issue.

### HubSpot
A 403 here often means `MISSING_SCOPES` - the private app or OAuth app was never granted the
scope needed for that endpoint. Compare the endpoint's documented required scopes against what's
actually enabled under Settings → Integrations → Private Apps → [App] → Scopes.
