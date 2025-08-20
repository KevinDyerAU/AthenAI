# Windows wrapper for configure-environment.sh
. "$PSScriptRoot\..\scripts-pwsh-helpers.ps1"
Invoke-BashScript -ScriptPath "scripts/setup/configure-environment.sh" -Arguments $args
