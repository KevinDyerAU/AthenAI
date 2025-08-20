# Enhanced AI Security Middleware (Node/Express)

JWT authentication and RBAC enforcement middleware for Node/Express services in Enhanced AI Agent OS.

## Quick start

1) Install
```
cd enhanced-ai-agent-os/middleware/node
npm install
```

2) Provide RBAC policies and keys
- RBAC: `infrastructure/security/rbac/policies.yaml` (already seeded)
- JWT verification: either
  - JWKS: set `jwksUri` to your IdP JWKS endpoint, or
  - PEM: generate and mount `infrastructure/security/jwt/keys/jwt_public.pem`

3) Use in an Express app
```js
import express from 'express';
import { createAuthMiddleware } from './src/index.js';

const app = express();
const { verifyToken, requirePermission } = createAuthMiddleware({
  issuer: 'https://your-issuer/',
  audience: 'your-audience',
  jwksUri: 'https://your-issuer/.well-known/jwks.json'
  // or publicKeyPath: 'infrastructure/security/jwt/keys/jwt_public.pem'
});

app.get('/api/workflows', verifyToken, requirePermission('workflows', 'read'), (req, res) => {
  res.json({ ok: true, user: req.user.sub, roles: req.user.roles });
});

app.listen(8080, () => console.log('Server on :8080'));
```

## Token requirements
- Algorithms: RS256 by default (configurable)
- Claims: `iss`, `aud`, `exp`, `iat`, `nbf` recommended; roles in `roles` or `https://roles`

## RBAC model
- `policies.yaml` defines roles and allowed `resource`/`actions`.
- `requirePermission(resource, action)` checks if any role grants access (supports `*`).

## Troubleshooting
- "missing_bearer_token": Ensure `Authorization: Bearer <token>` header.
- "invalid_token": Check issuer/audience, expiration, algorithm, and JWKS/PEM.
- "forbidden": Role lacks permission for the requested `resource`/`action`.
