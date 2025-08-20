import fs from 'fs';
import path from 'path';
import jwt from 'jsonwebtoken';
import jwksClient from 'jwks-rsa';
import yaml from 'js-yaml';

const POLICIES_PATH = path.resolve(process.cwd(), '../../infrastructure/security/rbac/policies.yaml');

function loadPolicies() {
  const p = POLICIES_PATH;
  if (!fs.existsSync(p)) throw new Error(`RBAC policies not found at ${p}`);
  return yaml.load(fs.readFileSync(p, 'utf8'));
}

function roleAllows(policies, roles, resource, action) {
  if (!policies || !Array.isArray(policies.roles)) return false;
  const roleSet = new Set(roles || []);
  for (const role of policies.roles) {
    if (!roleSet.has(role.name)) continue;
    for (const rule of role.allow || []) {
      const resMatch = rule.resource === '*' || rule.resource === resource;
      const actMatch = Array.isArray(rule.actions) && (rule.actions.includes('*') || rule.actions.includes(action));
      if (resMatch && actMatch) return true;
    }
  }
  return false;
}

export function createAuthMiddleware({
  issuer,
  audience,
  algorithms = ['RS256'],
  jwksUri,
  publicKeyPath,
}) {
  const policies = loadPolicies();

  let getKey;
  if (jwksUri) {
    const client = jwksClient({ jwksUri });
    getKey = (header, cb) => {
      client.getSigningKey(header.kid, (err, key) => {
        if (err) return cb(err);
        const signingKey = key.getPublicKey();
        cb(null, signingKey);
      });
    };
  } else if (publicKeyPath) {
    const pub = fs.readFileSync(publicKeyPath, 'utf8');
    getKey = (_header, cb) => cb(null, pub);
  } else {
    throw new Error('Either jwksUri or publicKeyPath must be provided');
  }

  function verifyToken(req, res, next) {
    const auth = req.headers['authorization'] || '';
    const token = auth.startsWith('Bearer ') ? auth.substring(7) : null;
    if (!token) return res.status(401).json({ error: 'missing_bearer_token' });

    const opts = { algorithms, audience, issuer, clockTolerance: 5 };
    getKey({ kid: jwt.decode(token, { complete: true })?.header?.kid }, (err, key) => {
      if (err) return res.status(401).json({ error: 'key_resolution_failed' });
      jwt.verify(token, key, opts, (e, payload) => {
        if (e) return res.status(401).json({ error: 'invalid_token', detail: e.message });
        req.user = {
          sub: payload.sub,
          roles: payload.roles || payload['https://roles'] || [],
          scope: payload.scope || '',
          claims: payload,
        };
        next();
      });
    });
  }

  function requirePermission(resource, action) {
    return (req, res, next) => {
      const roles = (req.user && req.user.roles) || [];
      if (!roleAllows(policies, roles, resource, action)) {
        return res.status(403).json({ error: 'forbidden', resource, action });
      }
      next();
    };
  }

  return { verifyToken, requirePermission };
}
