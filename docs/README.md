Runbooks - SaaS/CRM API Error Catalog
Each file in this folder is a runbook: a short, structured document that a
support engineer can follow under pressure, without having to reverse-engineer
the fix from scratch every time the same error shows up.
Every runbook follows the same template on purpose - consistency is what
makes a runbook fast to scan during an incident:
Summary - what the error means in plain language
Common Causes - ranked roughly by likelihood
Diagnostic Checklist - what to check, in order, before touching anything
Resolution Steps - the actual fix, step by step
Prevention - how to stop it from recurring
System-Specific Notes - Salesforce / HubSpot specifics where they differ
Index
Error	Type	Runbook
400 Bad Request	Validation	runbook_400_bad_request.md
401 Unauthorized	Authentication	runbook_401_unauthorized.md
403 Forbidden	Authorization	runbook_403_forbidden.md
404 Not Found	Resource	runbook_404_not_found.md
429 Too Many Requests	Rate limit	runbook_429_rate_limit.md
500 Internal Server Error	Provider-side	runbook_500_server_error.md
Sync - Duplicate records	Synchronization	runbook_sync_duplicate_records.md
Sync - Field mapping mismatch	Synchronization	runbook_sync_field_mapping.md
These runbooks are the source of truth behind `data/error_catalog.json` - the
JSON is the machine-readable version of exactly this content, which is what
`src/diagnostic_tool.py` actually reads at runtime.
