# Runbook: Sync Error - Field Mapping Mismatch

**Catalog ID:** `ERR-SYNC-FIELDMAP` · **Severity:** Medium-High · **Automated action:** none (needs config fix)

## Summary
A field-level mapping between two connected systems (e.g. HubSpot property →
Salesforce field) is broken - the source field, destination field, or the
values allowed by one side no longer line up with the other, so the sync
fails validation instead of writing bad data.

## Common Causes
1. A field was renamed or removed in one system (e.g. a custom Salesforce field), breaking the mapping in the sync tool
2. Data type mismatch between mapped fields (e.g. a HubSpot picklist value with no matching Salesforce picklist option)
3. A required field on the destination system has no source field mapped, so the sync fails validation on write
4. Field-level permissions block the integration user from writing to a mapped field

## Diagnostic Checklist
- [ ] Open the sync tool's field mapping configuration and look for mappings explicitly flagged as broken/invalid
- [ ] Confirm the source and destination fields both still exist, under the names the mapping expects
- [ ] Compare the field types (text, number, picklist, date) on both sides for compatibility
- [ ] If it's a picklist/dropdown, list the values allowed on both sides and diff them
- [ ] Confirm the integration user has field-level write access to every mapped field involved

## Resolution Steps
1. Fix or recreate the broken mapping once the correct source/destination fields are confirmed
2. Add any missing picklist values on the destination side, or configure a default/fallback value in the mapping for unmapped values
3. If a required destination field has no mapped source, either map one or make the field optional if appropriate
4. Grant field-level write access to the integration user if that was the blocker
5. Re-sync the records that failed due to this mapping once it's fixed

## Prevention
- Treat field mapping configuration as part of your change management process - any custom field rename/deletion should trigger a check of dependent sync mappings
- Keep picklist/dropdown values aligned between systems as a deliberate governance rule, not an afterthought
- Add monitoring/alerting on sync failure counts so a broken mapping is caught within hours, not discovered weeks later when someone notices missing data

## System-Specific Notes

### HubSpot-Salesforce sync
Native and third-party HubSpot-Salesforce connectors typically show mapping health status in
their own settings UI - check there first before assuming the issue is on the API side. Picklist
mismatches are one of the most common causes of silent sync failures in this specific pairing,
since HubSpot dropdown properties and Salesforce picklists are managed completely independently.
