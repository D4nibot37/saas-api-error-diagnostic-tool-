Runbook: 401 Unauthorized - Expired or Invalid Token
Catalog ID: `ERR-401-TOKEN` · Severity: High · Automated action: `refresh_token`
Summary
The API rejected the request because the credentials presented (usually an
OAuth2 access token) are missing, expired, or invalid. This is an
authentication problem - the API doesn't yet know who is asking, as
opposed to a 403 where it knows who you are but says you can't do that.
Common Causes
The access token has expired (OAuth2 access tokens typically last 1-2 hours)
The token was revoked manually, or invalidated by a user password change / admin action
The refresh token has also expired or was revoked (this forces a full re-auth)
The integration's credentials (Client ID / Client Secret) are incorrect or were rotated
A sandbox token is being used against production, or vice versa
Diagnostic Checklist
[ ] Check the token's expiration timestamp if your integration stores it
[ ] Confirm this is genuinely the first failure and not a symptom of a wider outage (check provider status page)
[ ] Verify the Client ID/Secret used to obtain the token still match what's configured on the provider side
[ ] Confirm the environment: is this token from sandbox but being sent to the production endpoint (or vice versa)?
Resolution Steps
Attempt an OAuth2 refresh-token exchange to get a new access token
If the refresh token also fails, re-run the full OAuth authorization flow to get a brand-new token pair
Confirm the integration's Connected App / Private App credentials have not been revoked or rotated in the admin panel
Update the stored token immediately once refreshed, so the next scheduled job doesn't fail on the same stale token
Re-send the original request with the new token
Prevention
Proactively refresh tokens shortly before expiry instead of waiting for a 401 (e.g. refresh at 90% of the token's lifetime)
Store token expiry timestamps alongside the token so your integration can self-check before calling the API
Alert (don't just log) when a refresh token itself fails - that usually means manual re-authorization is required
System-Specific Notes
Salesforce
A `INVALID_SESSION_ID` error means the session token expired or was revoked (e.g. by an admin
forcing logout, or a password reset). Salesforce access tokens from the OAuth flow do not
auto-refresh unless your Connected App is configured for and using the refresh token grant.
HubSpot
HubSpot private app access tokens do not expire on their own, so a 401 there more often
points to a revoked/regenerated token or a scope mismatch rather than natural expiry - check
whether the token was regenerated in Settings → Integrations → Private Apps
