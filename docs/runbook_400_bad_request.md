Runbook: 400 Bad Request - Data Validation Error
Catalog ID: `ERR-400-VALIDATION` · Severity: Low-Medium · Automated action: `validate_payload`
Summary
The API rejected the request because the payload sent did not meet the
endpoint's expected shape, type, or business rules. This is almost always a
client-side (integration-side) problem, not an outage.
Common Causes
Missing required field(s) in the request payload
Invalid data type (e.g. a string sent where a number or date is expected)
Malformed JSON syntax in the request body
A field value violates a picklist/dropdown constraint (e.g. an invalid status value)
Date format mismatch (e.g. `MM/DD/YYYY` sent instead of ISO 8601 `YYYY-MM-DD`)
Diagnostic Checklist
[ ] Read the full error response body, not just the status code - the provider almost always names the offending field
[ ] Confirm the payload is valid JSON (a trailing comma or unescaped quote is enough to trigger this)
[ ] Compare the payload's fields and types against the object's current schema in the provider's docs
[ ] Check if the object has recently changed (new required field, new picklist values) on the provider's side
[ ] Reproduce with a minimal payload to isolate which field is actually the problem
Resolution Steps
Identify the specific field(s) flagged in the error response
Validate the payload against the endpoint's schema before sending it (see `src/resolvers.py::simulate_payload_validation` for the pattern)
Normalize date and number formats to what the API expects (ISO 8601 for dates in almost every modern SaaS API)
Confirm any picklist/dropdown value being sent exists on the destination object
Re-send the corrected request and confirm a 2xx response
Prevention
Add client-side validation before every outbound API call, mirroring the provider's required fields
Keep a local copy of the object schema and review it whenever the provider announces API changes
Add automated tests that exercise the payload builder against edge cases (empty strings, nulls, wrong types)
System-Specific Notes
Salesforce
Validation errors often come back as an array with `errorCode: "REQUIRED_FIELD_MISSING"` or
`"FIELD_CUSTOM_VALIDATION_EXCEPTION"` - the latter means a custom validation rule on the
object rejected the data, so check Setup → Object Manager → Validation Rules, not just the field schema.
HubSpot
HubSpot's property validation errors typically return `"invalidPropertyValues"` and name the
exact property internal name - cross-check it against the property definition in
Settings → Properties, since internal names often differ from the labels shown in the UI.
