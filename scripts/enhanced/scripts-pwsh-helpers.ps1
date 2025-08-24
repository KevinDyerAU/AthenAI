# PowerShell helper to invoke Bash-based scripts on Windows.
# It prefers Git Bash (bash.exe in PATH). Falls back to WSL if available.
# Usage: . "$PSScriptRoot\scripts-pwsh-helpers.ps1"; Invoke-BashScript -ScriptPath "path/to/script.sh" -Arguments "--flag value"

function Get-BashInvoker {
  # Returns a script block that will invoke bash with provided command string
  $bash = (Get-Command bash -ErrorAction SilentlyContinue)
  if ($bash) {
    return {
      param($cmd)
      & $bash.Source -lc $cmd
    }
  }
  $wsl = (Get-Command wsl -ErrorAction SilentlyContinue)
  if ($wsl) {
    return {
      param($cmd)
      & $wsl bash -lc $cmd
    }
  }
  throw "Neither Git Bash (bash.exe) nor WSL (wsl.exe) found. Please install Git for Windows or enable WSL."
}

function Join-Args {
  param([string[]]$ArgsArray)
  if (-not $ArgsArray) { return "" }
  # Properly quote arguments for bash -lc
  $quoted = $ArgsArray | ForEach-Object {
    if ($_ -match '^[A-Za-z0-9._\-/:=]+$') { $_ } else { '"' + ($_ -replace '"','\\"') + '"' }
  }
  return ($quoted -join ' ')
}

function Resolve-RepoRoot {
  # Resolve repo root as directory containing this helpers file two levels up
  return (Resolve-Path -Path (Join-Path $PSScriptRoot '..')).Path
}

function Invoke-BashScript {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory=$true)][string]$ScriptPath,
    [string[]]$Arguments
  )
  $invoker = Get-BashInvoker
  $repoRoot = Resolve-RepoRoot
  $fullPath = Join-Path $repoRoot $ScriptPath
  if (-not (Test-Path -Path $fullPath)) {
    throw "Script not found: $fullPath"
  }
  # Build command string: cd to repo root to ensure relative paths match, then run script
  $argStr = Join-Args -ArgsArray $Arguments
  $cmd = "cd '$repoRoot' && bash '$ScriptPath' $argStr"
  Write-Host "[INFO] $(Get-Date -Format o) Running: $cmd"
  & $invoker.Invoke($cmd)
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed with exit code $LASTEXITCODE"
  }
}
