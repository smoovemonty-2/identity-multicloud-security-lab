# IR-008 — Multi-Cloud Security Incident Triage Report

**Assessment date:** November 9, 2026  
**Environment:** AWS and Microsoft Azure security lab  
**Investigation type:** Identity and administrative activity review  
**Status:** Initial triage complete; targeted follow-up open  
**Provisional security risk:** Low  
**Confirmed unauthorized activity:** None established

## 1. Executive Summary

A multi-cloud investigation was conducted to examine administrative activity across AWS and Microsoft Azure, with particular attention to identity management, authorization changes, resource provisioning, and security governance.

The investigation analyzed 150 collected event records: 50 AWS CloudTrail events and 100 Azure Activity Log events.

A Python-based correlation workflow identified 18 security-relevant records requiring review.

The four Azure RBAC event records were associated with one correlation group spanning two resources. Review of the caller, timing, resource scopes, and associated permissions established consistency with the authorized Terraform changes implemented during Session 7.

The remaining events included AWS security configuration inspection, successful Azure resource-management activity, and eight failed Azure governance or Event Grid operations.

**Initial determination:** No evidence of unauthorized privilege modification was established in the reviewed sample. Further operational investigation is warranted for the failed Azure events.

## 2. Evidence Collection and Preservation

| Evidence source | Records | Coverage |
|---|---:|---|
| AWS CloudTrail | 50 | Regional management events |
| Azure Activity Log | 100 | Lab resource-group activity |
| Unified timeline | 150 | Normalized chronological analysis |
| Security review candidates | 18 | Rule-flagged events |
| Azure RBAC correlation groups | 1 | Related authorization activity |

Original evidence was preserved in private storage with SHA-256 checksums. Derived analysis files were generated separately.

Cloud resource identifiers, user identities, and raw evidence are excluded from this public-facing report.

## 3. AWS Findings

**Operation:** `GetAccountPublicAccessBlock`  
**Occurrences:** 1  
**Classification:** Security configuration inspection

This is a read-only API operation that retrieves account-level S3 Block Public Access configuration.

The event does not itself demonstrate modification of public-access settings, object access, or data exfiltration.

No unauthorized AWS permissions change was identified among the flagged records.

**Assessment:** Low concern from the observed operation; caller authorization and wider account activity remain outside the scope of this individual finding.

## 4. Azure RBAC Findings

**Operation:** `Microsoft.Authorization/roleAssignments/write`

| Status | Records |
|---|---:|
| Started | 2 |
| Succeeded | 2 |
| Total | 4 |

The records formed one correlation group and involved two distinct resources.

The observed changes were compared with the authorized Terraform deployment that granted the user-assigned managed identity:

- Storage Blob Data Reader on the application-data Storage account
- Key Vault Secrets User on the designated Key Vault

The reviewed caller, deployment timing, resource scopes, and permissions matched the authorized infrastructure changes.

**Assessment:** Authorized administrative activity. No unexplained privilege expansion was established in these records.

Correlation grouping was used alongside the distinct operations and resource details; the shared correlation ID was not treated as proof of only one permission change.

## 5. Azure Resource Provisioning Findings

| Operation | Started | Accepted | Succeeded |
|---|---:|---:|---:|
| Key Vault write | 1 | 1 | 1 |
| Storage account write | 1 | 0 | 1 |

These events are consistent with the expected resource-provisioning activity performed during the Terraform lab.

They do not independently indicate unauthorized changes.

**Assessment:** Expected activity based on the lab context, subject to the bounded evidence available.

## 6. Failed Azure Operations Requiring Follow-Up

| Operation | Failed records | Assessment |
|---|---:|---|
| `policies/auditIfNotExists/action` | 6 | Determine policy compliance findings and failure details |
| `policies/deny/action` | 1 | Correlate with known policy-enforced deployment rejection |
| `systemTopics/write` | 1 | Determine whether Event Grid creation failed due to policy, permissions, or another cause |

Eight failed operation records were identified.

The previous Azure subscription policy requiring `Environment=Production` provides a potential explanation for the deny event. However, the event's correlation details and policy evaluation must be checked before assigning that root cause.

Similarly, the failed Event Grid system-topic operation may represent an environmental configuration or governance issue. Its cause has not been established.

**Assessment:** Unresolved operational or governance findings. No evidence currently establishes malicious intent.

## 7. Risk and Incident Determination

**Provisional risk: Low for unauthorized identity-change activity within the reviewed sample.**

Supporting evidence:

- The two reviewed RBAC changes matched authorized Terraform activity.
- The flagged AWS API was read-only.
- The observed successful Storage and Key Vault operations were consistent with the documented lab.
- No confirmed unauthorized administrative change was identified.

Residual uncertainties include the causes of the eight failed Azure operations and the limited coverage of the collected telemetry.

The findings do not establish complete absence of compromise, unauthorized data access, or activity outside the collection scope.

## 8. Containment Decision

**Decision: No containment action indicated by the current evidence.**

Revoking roles, disabling identities, or modifying cloud resources would be disproportionate without evidence of unauthorized activity.

If additional evidence identifies an unauthorized principal, unexpected privilege grant, or malicious operation, incident escalation and authorized containment would be reconsidered.

No active containment changes were performed as part of this exercise.

## 9. Evidence Limitations

The AWS investigation used a bounded collection of regional management events rather than an exhaustive cloud-wide dataset.

The Azure investigation examined a bounded sample of resource-group Activity Log records.

The collected evidence does not provide comprehensive S3 object-level auditing, Key Vault secret-access history, or continuous monitoring across both environments.

Results therefore apply only to the available records and corroborated changes.

## 10. Follow-Up Actions

| Priority | Action | Success criterion |
|---|---|---|
| High | Review six failed Policy audit events | Determine whether they represent compliance findings or processing failures |
| High | Correlate Policy deny event | Confirm or reject association with known tagging policy |
| Medium | Investigate Event Grid failure | Identify root cause and operational impact |
| Medium | Review audit coverage | Document visibility gaps and any additional logging requirements |
| Medium | Preserve and publish sanitized findings | Maintain reproducible investigation notes without exposing raw evidence |

These priorities refer to investigative follow-up, not confirmed incident severity.

## 11. Conclusion

**Initial triage is complete. The unauthorized RBAC modification hypothesis was not supported by the reviewed evidence.**

The investigation demonstrated multi-cloud event collection, evidence preservation, timeline normalization, security-event correlation, authorization verification, and risk-based containment decisions.

The reviewed authorization activity is consistent with approved infrastructure changes. The remaining Azure failures require targeted operational review before all investigation work can be closed.

**Disposition: No confirmed security incident; operational follow-up remains open.**
