# Session 1 — Enterprise Identity Security Validation

**Project:** Enterprise Identity & Multi-Cloud Security Engineering Lab

**Platform:** Microsoft Entra ID

**Application:** `lab-enterprise-portal`

**Validation date:** 10/24/2026

## 1. Objective

Implement and validate least-privilege access controls for an internal enterprise application using Microsoft Entra ID.

## 2. Identity configuration

Two test identities were provisioned:

- Alex Morgan — Authorized application user
- Taylor Brooks — Unassigned security auditor

Both identities were configured as standard users without administrative privileges.

Security groups:

- `SG-LAB-App-Users`
- `SG-LAB-Security-Auditors`

## 3. Application security controls

| Control                | Expected configuration | Observed result |
| ---------------------- | ---------------------- | --------------- |
| Application enabled    | Yes                    | Yes             |
| Assignment required    | Yes                    | Yes             |
| Alex assigned          | Yes                    | Yes             |
| Alex's role            | Default Access         | Default Access  |
| Taylor assigned        | No                     | No              |
| Auditor group assigned | No                     | No              |

## 4. Audit log investigation

- Activity examined: Add app role assignment grant to user
- Initiated by: Global Administrator
- Target resource: ServicePrincipal
- Result: Success
- Relevant observation: Successful assignment of Alex to application

## 5. Security assessment

The enterprise application is configured to require explicit assignment. Alex has a direct assignment, while Taylor remains unassigned.

This configuration supports least-privilege application access by restricting which identities are eligible to authenticate to the application.

## 6. Validation status

- Configuration checks: Passed
- Audit evidence reviewed: Yes
- Actual SSO authentication testing: Pending Session 2
- Unauthorized sign-in testing: Pending Session 2

## 7. Next steps

Implement the Python Flask application with Microsoft Entra authentication using OpenID Connect.

Validate successful authentication for Alex and expected access denial for Taylor.

Investigate the resulting Entra sign-in logs and document the troubleshooting process.
