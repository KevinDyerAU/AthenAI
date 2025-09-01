# Security Architecture & Procedures

This document outlines the security framework for Enhanced AI Agent OS, covering authentication, authorization, API security, data protection, monitoring, and compliance.

## Authentication & Authorization
- JWT-based authentication with refresh tokens.
- RBAC with roles and granular permissions (service and user principals).
- MFA and SSO via IdP (OIDC/SAML) recommended. Support service-to-service tokens.

### Tokens
- Access tokens: short-lived (5–15m). Include `aud`, `iss`, `sub`, `roles`, `scope`, `kid`.
- Refresh tokens: long-lived, revocable, rotated per use, hashed at rest.
- Public key discovery: JWKS or published PEMs (`infrastructure/security/jwt/keys`).

## API Security
- NGINX security policies (`infrastructure/security/nginx/security.conf`): CORS, rate limiting, headers.
- Input validation at service layer. Enforce size/time limits.
- Enable WAF where appropriate.
- Security endpoints (JWT + RBAC protected):
  - `GET /api/security/compliance/assess` — runs compliance checks and persists a report when enabled.
  - `GET /api/security/incidents?kind=&severity=&limit=` — list recorded security incidents.
  - `POST /api/security/incidents` — record a new incident `{kind, severity, message, context}`.
  - `GET /api/security/sandbox/policy` — view current sandbox policy (env-driven).
  - `POST /api/security/sandbox/evaluate` — evaluate sandbox policy for a `risk_score` (0..1).

### Auth headers and flows

Required headers for protected endpoints:

- `Authorization: Bearer <access_token>`
- `Content-Type: application/json` (for JSON bodies)

Token lifecycle (local `AUTH_PROVIDER=local`):

1. Client obtains token via login endpoint (if exposed) or via IdP when `AUTH_PROVIDER=oidc`.
2. Sends token in `Authorization` header.
3. Refreshes token before expiry using refresh endpoint/flow.

Example request:

```bash
curl -fsS http://localhost:8000/api/system/status \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Data Protection
- Encryption in transit: TLS for all endpoints and internal comms where possible.
- Encryption at rest: database-native (Postgres/Neo4j) + encrypted volumes.
- Data classification & retention policies documented per dataset.

## Security Monitoring & Detection
- Prometheus alerting rules for auth failures, rate limiting spikes, and anomalous behavior (`infrastructure/monitoring/alerts/security.yml`).
- Centralized logs (Loki/Promtail) with audit fields: user/service id, action, resource, result, IP, trace id.
- Tracing with OTel/Jaeger including auth context (without sensitive data).
 - Incidents API provides a lightweight SOC feed; persist can be disabled via `INCIDENT_PERSIST_DISABLED=true`.

## Audit Logging & Compliance
- Immutable audit logs retained per policy (e.g., 1–7 years).
- Regular compliance reports (access reviews, key rotation, vulnerability status) in `workflows/security/`.
 - Application-level compliance assessment is exposed via `GET /api/security/compliance/assess` and can be disabled with `COMPLIANCE_PERSIST_DISABLED=true`.

## Vulnerability Management
- Container image scanning (Trivy) and dependency scanning in CI.
- ZAP baseline scans for API endpoints.

## Implementation Pointers
- Generate JWT keys via scripts in `scripts/security/`.
- Include `security.conf` in NGINX server blocks.
- Add service middleware to validate JWT, roles, and scopes.
- Store secrets in environment or a secrets manager; avoid committing.
