param(
  [string]$OutDir = "infrastructure/security/jwt/keys"
)

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# Requires OpenSSL installed on Windows
& openssl genrsa -out "$OutDir/jwt_private.pem" 2048
& openssl rsa -in "$OutDir/jwt_private.pem" -pubout -out "$OutDir/jwt_public.pem"

icacls "$OutDir/jwt_private.pem" /inheritance:r /grant:r "$($env:USERNAME):(R)" | Out-Null
Write-Host "Generated RSA keypair in $OutDir"
