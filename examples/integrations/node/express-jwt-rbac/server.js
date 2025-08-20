import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { createAuthMiddleware } from '../../../../enhanced-ai-agent-os/middleware/node/src/index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.json());

// Configure JWT verification
const { verifyToken, requirePermission } = createAuthMiddleware({
  issuer: process.env.JWT_ISSUER || 'https://your-issuer/',
  audience: process.env.JWT_AUDIENCE || 'your-audience',
  // Prefer JWKS in production
  jwksUri: process.env.JWKS_URI || undefined,
  // Or fallback to PEM path for local dev
  publicKeyPath: process.env.JWT_PUBLIC_KEY || path.resolve(__dirname, '../../../../infrastructure/security/jwt/keys/jwt_public.pem'),
});

// Health
app.get('/healthz', (_req, res) => res.json({ ok: true }));

// Protected routes examples
app.get('/api/workflows', verifyToken, requirePermission('workflows', 'read'), (req, res) => {
  res.json({ ok: true, user: req.user.sub, roles: req.user.roles, resource: 'workflows', action: 'read' });
});

app.post('/api/workflows', verifyToken, requirePermission('workflows', 'create'), (req, res) => {
  res.json({ ok: true, created: true });
});

app.post('/api/agents/:id/invoke', verifyToken, requirePermission('agents', 'invoke'), (req, res) => {
  res.json({ ok: true, agent: req.params.id, invoked: true });
});

const port = process.env.PORT || 8080;
app.listen(port, () => console.log(`Example JWT/RBAC service running on :${port}`));
