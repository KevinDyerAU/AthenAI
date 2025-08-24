# Windows wrapper for backup-all-data.sh
. "$PSScriptRoot\..\scripts-pwsh-helpers.ps1"
Invoke-BashScript -ScriptPath "scripts/backup/backup-all-data.sh" -Arguments $args
