# Windows wrapper for install-system.sh
. "$PSScriptRoot\..\scripts-pwsh-helpers.ps1"
Invoke-BashScript -ScriptPath "scripts/setup/install-system.sh" -Arguments $args
