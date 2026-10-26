# Session 2 — Microsoft Entra ID SSO Implementation and Validation

**Project:** Enterprise Identity & Multi-Cloud Security Engineering Lab  
**Application:** `lab-enterprise-portal`  
**Technologies:** Microsoft Entra ID, Python Flask, MSAL, OpenID Connect, OAuth 2.0, Microsoft Graph  
**Status:** Technical validation passed

## 1. Objective

Integrate a Python Flask web application with Microsoft Entra ID for centralized authentication, implement application access restrictions, test Microsoft Graph connectivity, and troubleshoot authentication failures.

## 2. Implementation

- Configured a single-tenant Entra application registration.
- Registered the Web redirect URI: `http://localhost:3000/auth/redirect`.
- Configured a short-lived local development client credential.
- Configured Microsoft Graph delegated `User.Read` permission with administrator consent.
- Integrated Flask with MSAL using the authorization-code flow.
- Configured the application to display an account selector.
- Enforced enterprise application assignment requirements.

## 3. Authentication and Authorization Testing

| Test | Expected Result | Actual Result |
|---|---|---|
| Alex SSO authentication | Successful login | Passed |
| Microsoft Graph `/me` | Return authenticated user's profile | Passed |
| Taylor SSO authentication | Access denied | Passed — AADSTS50105 |
| Entra sign-in log review | Success and failure events | Both located |
| Redirect URI mismatch | Authentication error | Passed — AADSTS50011 |
| Restore correct redirect URI | Authentication restored | Passed |

## 4. Troubleshooting Exercise A — Existing Administrator SSO Session

**Issue:** The application automatically authenticated using an existing administrator browser session.

**Investigation:** Identified that an existing Microsoft Entra browser SSO session was being reused.

**Resolution:** Updated the MSAL authentication request to include `prompt="select_account"`.

**Result:** The account selector appeared, allowing authentication testing with the intended test identities.

## 5. Troubleshooting Exercise B — Application Assignment Failure

**Test identity:** Taylor Brooks

**Error:** AADSTS50105

**Root cause:** The enterprise application required explicit assignment, and Taylor was not assigned.

**Security result:** Unauthorized application sign-in was correctly denied.

**Verification:** Located the corresponding failed sign-in event in Microsoft Entra logs.

## 6. Troubleshooting Exercise C — Redirect URI Mismatch

**Error:** AADSTS50011

**Root cause:** The redirect URI supplied by the local application did not match the URI configured in Microsoft Entra.

**Test modification:** Changed the local redirect URI path from `/auth/redirect` to `/auth/redirect-test`.

**Resolution:** Restored the original redirect URI.

**Verification:** Successfully authenticated after correcting the configuration.

## 7. Security Controls Validated

- Centralized authentication through Microsoft Entra ID.
- Explicit enterprise application assignment.
- Least-privilege delegated Microsoft Graph access.
- Application credential stored outside application source code.
- Authentication and authorization failure investigation.
- Restoration of correct authentication behavior after a configuration failure.

## 8. Evidence

- Successful Alex sign-in: [Evidence file or private reference]
- Failed Taylor sign-in: [Evidence file or private reference]
- AADSTS50011 failure: [Evidence file or private reference]
- Successful authentication recovery: [Evidence file or private reference]
- Microsoft Graph response: [Sanitized evidence reference]

## 9. Remaining Considerations

This implementation is a local development lab rather than a production-hardened authentication service.

Production improvements would include HTTPS deployment, stronger credential management, secure production session storage, structured monitoring, and additional application-level authorization.

## 10. Conclusion

Successfully implemented and validated a Microsoft Entra ID OIDC integration with Python Flask.

Demonstrated delegated Microsoft Graph access, enforcement of application assignments, investigation of unauthorized sign-in attempts, diagnosis of redirect URI mismatches, and successful recovery after configuration correction.
