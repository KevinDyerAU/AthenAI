param(
  [Parameter(Mandatory = $true)][string]$EnvFile
)

$ErrorActionPreference = 'Stop'
$script = Join-Path $PSScriptRoot 'validate_env.py'
python $script --env-file $EnvFile --environment staging
