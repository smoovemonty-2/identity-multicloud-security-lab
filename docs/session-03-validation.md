# Session 3 — Microsoft Graph Identity Security Automation

## Objective

Develop and validate a reusable, read-only PowerShell audit tool that evaluates Microsoft Entra ID security group memberships against an approved access baseline.

## Technologies

- PowerShell 7
- Microsoft Graph PowerShell SDK
- Microsoft Entra ID
- JSON configuration
- CSV audit and exception reporting

## Implementation

Built `Invoke-EntraGroupAccessAudit.ps1` with capabilities to:

1. Verify the Microsoft Graph connection, tenant, and delegated permissions.
2. Load an approved access baseline from a private JSON configuration.
3. Retrieve direct security group memberships using Microsoft Graph.
4. Compare actual access against approved Microsoft Entra object IDs.
5. Detect unexpected and missing group members.
6. Export timestamped audit and exception reports.
7. Stop execution when configuration validation or required API calls fail.

## Test Results

| Test | Outcome | Status |
|---|---|---|
| Microsoft Graph authentication | Successfully connected using delegated permissions | Passed |
| Identity retrieval | Retrieved two Entra test identities | Passed |
| Group membership retrieval | Verified Alex in App Users and Taylor in Security Auditors | Passed |
| Approved baseline | Two approved memberships, zero exceptions | Passed |
| Exception simulation | Detected unexpected and missing memberships | Passed |
| Packaged audit execution | Two approved memberships, zero exceptions | Passed |
| Missing-baseline negative test | Script stopped with an error | Passed |

## Troubleshooting and Resolution

### Authentication failure — AADSTS900023

Identified an incorrectly supplied tenant identifier. Corrected the Directory (tenant) ID and successfully authenticated to Microsoft Graph.

### Identity query failure — 404 ResourceNotFound

Investigated an incorrectly constructed User Principal Name (UPN). Retrieved the actual UPNs from Entra ID and corrected the identity queries.

### Access baseline validation failure — Invalid GUID

The packaged audit script detected invalid group IDs in the private JSON baseline and stopped execution.

Corrected the baseline with valid Microsoft Entra group object IDs, confirmed that the IDs passed GUID validation, and reran the audit successfully.

### PowerShell diagnostic syntax error

Corrected an invalid pipeline in a troubleshooting command and successfully reran the configuration diagnostic.

## Security Controls and Design Decisions

- Read-only Microsoft Graph access
- Approved identities identified by stable object IDs
- Tenant and permission verification
- Error handling to prevent misleading audit results
- Private configuration separated from public source code
- Timestamped reporting for repeatable review
- Validation of both successful and failure scenarios

## Scope and Limitations

The tool audits direct user membership in configured Entra security groups. It does not evaluate nested groups, non-user principals, privileged directory roles, Conditional Access policies, or effective enterprise application permissions.

The implementation is a validated portfolio lab, not a fully hardened production monitoring service. Production enhancements would include structured logs, retry handling, alerting, and automated tests.

## Outcome

Successfully developed and validated a reusable Microsoft Entra ID security auditing tool demonstrating identity governance, Microsoft Graph integration, PowerShell automation, access exception detection, troubleshooting, and security reporting.
