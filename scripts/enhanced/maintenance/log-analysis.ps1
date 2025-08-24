# Windows wrapper for log-analysis.sh
. "$PSScriptRoot\..\scripts-pwsh-helpers.ps1"
Invoke-BashScript -ScriptPath "scripts/maintenance/log-analysis.sh" -Arguments $args
