# TLS Guidance

- Use TLS everywhere (ingress, service-to-service where feasible).
- For local dev, use `mkcert` or self-signed.
- For production, use a managed CA (ACME/Let’s Encrypt) or corporate PKI.

## Example (mkcert)
```
mkcert -install
mkcert -key-file key.pem -cert-file cert.pem localhost 127.0.0.1 ::1
```

Place certs under a secure path and mount read-only into reverse proxy.
