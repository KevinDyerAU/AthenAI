#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-infrastructure/security/jwt/keys}"
mkdir -p "$OUT_DIR"

# RSA 2048 (RS256)
openssl genrsa -out "$OUT_DIR/jwt_private.pem" 2048
openssl rsa -in "$OUT_DIR/jwt_private.pem" -pubout -out "$OUT_DIR/jwt_public.pem"
chmod 600 "$OUT_DIR/jwt_private.pem"
chmod 644 "$OUT_DIR/jwt_public.pem"

echo "Generated RSA keypair in $OUT_DIR"
