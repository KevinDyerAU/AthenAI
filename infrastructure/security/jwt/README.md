# JWT Authentication Keys and Validation

This directory contains guidance for generating and managing JWT signing keys and validating tokens at the edge and in services.

## Key Algorithms
- RS256 (RSA) recommended for compatibility
- ES256 (ECDSA) recommended for performance and smaller keys

## Generate Keys
Use the helper scripts in `scripts/security/`:
- `generate-jwt-keys.sh` (OpenSSL, Linux/macOS)
- `generate-jwt-keys.ps1` (PowerShell, Windows)

Outputs by default to `infrastructure/security/jwt/keys/`:
- `jwt_private.pem` (private key, protect and restrict permissions)
- `jwt_public.pem` (public key for verification)

## Rotation
- Maintain `kid` (Key ID) in JWT header.
- Keep previous public keys available for verification during rotation window.

## Validation
- Services should validate `iss`, `aud`, `exp`, `nbf`, `iat`, and `kid`.
- Enforce short-lived access tokens and rotate refresh tokens.

## MFA and SSO
- Integrate with your IdP (OIDC/SAML). Use IdP-issued JWTs or exchange for internal tokens.
