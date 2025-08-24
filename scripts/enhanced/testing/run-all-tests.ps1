# Windows wrapper for run-all-tests.sh
. "$PSScriptRoot\..\scripts-pwsh-helpers.ps1"
Invoke-BashScript -ScriptPath "scripts/testing/run-all-tests.sh" -Arguments $args
