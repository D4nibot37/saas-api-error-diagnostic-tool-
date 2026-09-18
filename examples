# Usage Examples

All commands below are run from the project root. Output shown is real,
captured by actually running the tool (nothing hand-written).

## 1. Run the built-in demo (fastest way to see everything)

```bash
python src/diagnostic_tool.py --demo
```

Runs four realistic scenarios end-to-end (401, 429, 400, and a sync error),
each with diagnosis + simulated resolution.

## 2. Diagnose a single reported error

```bash
python src/diagnostic_tool.py --code 403 --message "User does not have permission to access this object" --system Salesforce
```

```
============================================================
DIAGNOSIS
============================================================
Reported HTTP code : 403
Reported message   : User does not have permission to access this object
Source system      : Salesforce
------------------------------------------------------------
Identified error   : Forbidden - Insufficient Permissions (ERR-403-PERMISSIONS)
Severity           : MEDIUM-HIGH
Match confidence   : 67%

PROBABLE CAUSES:
  1. The API user/integration lacks permission for this object or action (e.g. a read-only user attempting a write)
  2. The connected app's OAuth scopes do not include the required permission
  3. IP restrictions on the org are blocking requests from this server's IP address
  4. The integration user's profile or permission set was recently changed or revoked
  5. Attempting to access a record outside the user's sharing rules (record-level security)

RESOLUTION STEPS (runbook):
  1. Identify the exact permission required for the failing action (object CRUD + field-level security)
  2. Review the integration user's profile / permission set (Salesforce) or the app's granted scopes (HubSpot)
  3. Confirm the request's origin IP is allow-listed if IP restrictions are enabled
  4. Escalate to a Salesforce/HubSpot administrator if a permission change is required
  5. Re-authenticate if OAuth scopes were recently updated, since the existing token may need to be reissued

Full runbook       : docs/runbook_403_forbidden.md
============================================================
```

## 3. Diagnose AND simulate a resolution attempt

```bash
python src/diagnostic_tool.py --code 429 --message "Rate limit exceeded" --system HubSpot --resolve
```

The `--resolve` flag additionally runs the matching simulated action - in
this case, an exponential backoff retry loop:

```
SIMULATING AUTOMATED RESOLUTION
------------------------------------------------------------
Attempt 1/4 - waiting 1s before retrying...
Attempt 1: 429 Too Many Requests (simulated)
Attempt 2/4 - waiting 2s before retrying...
Attempt 2: 429 Too Many Requests (simulated)
Attempt 3/4 - waiting 4s before retrying...
Attempt 3: request succeeded (200 OK - simulated)

Final result: SUCCESS
------------------------------------------------------------
```

## 4. Diagnose from a free-text message, no HTTP code needed

Useful for sync-tool style errors that don't come with a standard HTTP code:

```bash
python src/diagnostic_tool.py --message "Duplicate contact record detected during sync"
```

## 5. What happens with an unrecognized error

```bash
python src/diagnostic_tool.py --code 999 --message "some totally unknown weird error xyz"
```

```
============================================================
DIAGNOSIS
============================================================
Reported HTTP code : 999
Reported message   : some totally unknown weird error xyz
Source system      : Not specified
------------------------------------------------------------
No clear match found in the catalog.
Next step: check the provider's official API documentation,
or add this case to data/error_catalog.json for next time.
============================================================
```

This is a deliberate design choice: the tool never guesses when it has no
real signal - it says so clearly instead of returning a misleading answer.

## 6. Optional bonus: diagnose a real, live HTTP response

Requires `pip install -r requirements.txt` and internet access:

```bash
python src/diagnostic_tool.py --live-check https://httpstat.us/429 --resolve
```

This sends a real GET request with `requests`, reads the actual status code
returned, and feeds it into the exact same diagnostic engine used for the
static examples above.

---

**Tip for your own portfolio walkthrough:** record a short terminal GIF of
`--demo` (e.g. with [asciinema](https://asciinema.org/) or
[Terminalizer](https://terminalizer.com/)) and embed it in the main
`README.md` - it's the fastest way for a recruiter to see the tool working in
under 15 seconds.
