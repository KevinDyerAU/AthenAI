Param(
  [string]$NEO4J_URI=$env:NEO4J_URI,
  [string]$NEO4J_USER=$env:NEO4J_USER,
  [string]$NEO4J_PASSWORD=$env:NEO4J_PASSWORD,
  [int]$INTERVAL_SECONDS=([int]($env:INTERVAL_SECONDS | ForEach-Object { if ($_){$_} else {60} })),
  [string]$ALERT_MIN_SEVERITY=($env:ALERT_MIN_SEVERITY | ForEach-Object { if ($_){$_} else {'warning'} }),
  [int]$THRESH_ORPHANS=([int]($env:THRESH_ORPHANS | ForEach-Object { if ($_){$_} else {0} })),
  [int]$THRESH_CONTRADICTIONS=([int]($env:THRESH_CONTRADICTIONS | ForEach-Object { if ($_){$_} else {0} })),
  [int]$THRESH_MISSING=([int]($env:THRESH_MISSING | ForEach-Object { if ($_){$_} else {0} }))
)

$env:NEO4J_URI = $NEO4J_URI
$env:NEO4J_USER = $NEO4J_USER
$env:NEO4J_PASSWORD = $NEO4J_PASSWORD
$env:INTERVAL_SECONDS = $INTERVAL_SECONDS
$env:ALERT_MIN_SEVERITY = $ALERT_MIN_SEVERITY
$env:THRESH_ORPHANS = $THRESH_ORPHANS
$env:THRESH_CONTRADICTIONS = $THRESH_CONTRADICTIONS
$env:THRESH_MISSING = $THRESH_MISSING

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path "$scriptDir\..\.."
Push-Location $repoRoot
python scripts/monitoring/kg_integrity_watch.py
$exitCode = $LASTEXITCODE
Pop-Location
exit $exitCode
