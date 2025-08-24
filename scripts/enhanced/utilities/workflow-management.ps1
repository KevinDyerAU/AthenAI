# Windows wrapper for workflow-management.sh
. "$PSScriptRoot\..\scripts-pwsh-helpers.ps1"
Invoke-BashScript -ScriptPath "scripts/utilities/workflow-management.sh" -Arguments $args
