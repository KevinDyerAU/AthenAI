<#
.SYNOPSIS
  One-shot developer setup script for NeoV3 autonomous agent environment (Windows/PowerShell).
.DESCRIPTION
  - Creates Python venv (if api/requirements.txt exists) and installs deps
  - Ensures required local directories exist
  - Starts docker compose with dev overrides
  - Prints next steps
#>

param(
  [switch]$Recreate
)

$ErrorActionPreference = 'Stop'

function Ensure-Dir($path) {
  if (-not (Test-Path -LiteralPath $path)) {
    New-Item -ItemType Directory -Path $path | Out-Null
  }
}

Write-Host "[1/5] Ensuring local directories..." -ForegroundColor Cyan
Ensure-Dir "$PSScriptRoot\..\..\data\api"
Ensure-Dir "$PSScriptRoot\..\..\logs\api"
Ensure-Dir "$PSScriptRoot\..\..\enhanced-ai-agent-os\agents\config"
Ensure-Dir "$PSScriptRoot\..\..\enhanced-ai-agent-os\agents\implementations"
Ensure-Dir "$PSScriptRoot\..\..\enhanced-ai-agent-os\agents\metrics"
Ensure-Dir "$PSScriptRoot\..\..\enhanced-ai-agent-os\logs\agents"

Write-Host "[2/5] Python virtual environment (optional)..." -ForegroundColor Cyan
$apiPath = Join-Path $PSScriptRoot "..\..\api"
$reqFile = Join-Path $apiPath "requirements.txt"
if (Test-Path -LiteralPath $reqFile) {
  $venvPath = Join-Path $apiPath ".venv"
  if ($Recreate -and (Test-Path -LiteralPath $venvPath)) { Remove-Item -Recurse -Force $venvPath }
  if (-not (Test-Path -LiteralPath $venvPath)) {
    Write-Host "Creating venv at $venvPath" -ForegroundColor Yellow
    python -m venv "$venvPath"
  }
  $venvPython = Join-Path $venvPath "Scripts\python.exe"
  if (Test-Path -LiteralPath $venvPython) {
    & $venvPython -m pip install --upgrade pip wheel setuptools
    & $venvPython -m pip install -r $reqFile
  }
}
else {
  Write-Host "No api/requirements.txt found; skipping venv" -ForegroundColor DarkYellow
}

Write-Host "[3/5] Validating env file..." -ForegroundColor Cyan
$envFile = Join-Path $PSScriptRoot "..\..\.env"
if (-not (Test-Path -LiteralPath $envFile)) {
  Write-Host ".env not found, copying from .env.example" -ForegroundColor Yellow
  Copy-Item (Join-Path $PSScriptRoot "..\..\.env.example") $envFile
}

Write-Host "[4/5] Starting Docker services..." -ForegroundColor Cyan
# Compose V2 syntax: `docker compose`
$composeRoot = (Join-Path $PSScriptRoot "..\..")
Push-Location $composeRoot
try {
  docker compose -f docker-compose.yml -f docker-compose.override.dev.yml up -d --remove-orphans
}
finally {
  Pop-Location
}

Write-Host "[5/5] Done. Useful URLs:" -ForegroundColor Cyan
Write-Host "  API:           http://localhost:8000" -ForegroundColor Green
Write-Host "  RabbitMQ:      http://localhost:15672" -ForegroundColor Green
Write-Host "  Neo4j Browser: http://localhost:7474" -ForegroundColor Green
Write-Host "  Grafana:       http://localhost:3000" -ForegroundColor Green

Write-Host "Next: Run scripts/dev/verify-connectivity.ps1 to validate connectivity." -ForegroundColor Cyan
