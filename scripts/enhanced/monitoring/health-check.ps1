# Windows wrapper for health-check.sh
. "$PSScriptRoot\..\scripts-pwsh-helpers.ps1"
Invoke-BashScript -ScriptPath "scripts/monitoring/health-check.sh" -Arguments $args
