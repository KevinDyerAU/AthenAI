# NeoV3 - Unified Cloud Deployment (PowerShell wrapper)
# Usage:
#   .\deploy-cloud.ps1 [-Help]
# Notes:
#   - Runs from repo root and invokes the Bash wrapper `deploy-cloud.sh`.
#   - Requires .env.cloud at repo root with Render credentials and secrets.
param(
  [switch]$Help
)

$ErrorActionPreference = "Stop"
$Root = Join-Path (Get-Location) "."
$BashWrapper = Join-Path $Root "deploy-cloud.sh"
$EnvFile = Join-Path $Root ".env.cloud"

function Show-Usage {
  @"
NeoV3 Cloud Deployment (PowerShell)

Usage: .\deploy-cloud.ps1 [-Help]

Description:
  PowerShell wrapper that calls Bash script .\deploy-cloud.sh which
  wraps the upstream Render.com deployment flow.

Options:
  -Help  Show this help and exit

Requirements:
  - bash available (Git Bash/WSL)
  - .env.cloud at repo root
"@ | Write-Output
}

if ($Help) { Show-Usage; exit 0 }

if (-not (Test-Path $BashWrapper)) { throw "Bash wrapper not found: $BashWrapper" }
if (-not (Test-Path $EnvFile)) { Write-Warning ".env.cloud not found at $EnvFile. You must create it before deploying." }

# Prefer native Git Bash if available; otherwise rely on WSL default 'bash'
$bashCmd = Get-Command bash -ErrorAction SilentlyContinue
if (-not $bashCmd) { throw "bash not found. Install Git for Windows or use WSL." }

& bash "$BashWrapper"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
