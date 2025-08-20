# Windows wrapper for security-scan.sh
. "$PSScriptRoot\..\scripts-pwsh-helpers.ps1"
Invoke-BashScript -ScriptPath "scripts/security/security-scan.sh" -Arguments $args
