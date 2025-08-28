param(
  [int]$Port = 8088
)

$ErrorActionPreference = 'Stop'

# Resolve Python
$pythonCandidates = @(
  Join-Path $PSScriptRoot ".venv\Scripts\python.exe",
  "py -3",
  "python",
  "python3"
)

$pythonCmd = $null
foreach ($cand in $pythonCandidates) {
  try {
    if ($cand -match "\\.exe$") {
      if (Test-Path $cand) { $pythonCmd = "`"$cand`""; break }
    } else {
      $ver = & $ExecutionContext.InvokeCommand.ExpandString($cand) --version 2>$null
      if ($LASTEXITCODE -eq 0 -or $ver) { $pythonCmd = $cand; break }
    }
  } catch {}
}

if (-not $pythonCmd) {
  Write-Error "Python not found. Install Python 3.x or create a venv in .venv first."
  exit 1
}

$env:SERVE_PORT = "$Port"

# Note: Environment variables from the parent shell are already available to this process.
# No additional pass-through is required. If you need to set custom ports, set them
# before invoking this script, e.g.:
#   $Env:API_HOST_PORT=9000; $Env:GRAFANA_PORT=3300; ./start-index.ps1 -Port 8090

Push-Location $PSScriptRoot
try {
  Write-Host "Starting NeoV3 local portal on http://localhost:$Port"
  if ($pythonCmd -match "\\.exe$" -or $pythonCmd -match "py ") {
    & $pythonCmd serve.py
  } else {
    & $pythonCmd "serve.py"
  }
} finally {
  Pop-Location
}
