Param(
  [string]$EnvFile = (Join-Path $PSScriptRoot '..' '..' '.env' | Resolve-Path),
  [string]$SchemaFile = (Join-Path $PSScriptRoot '..' '..' 'db' 'postgres' 'schema.sql' | Resolve-Path)
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $EnvFile)) { Write-Warning ".env not found at $EnvFile — will use compose defaults if possible" }
if (-not (Test-Path $SchemaFile)) { Write-Error "schema.sql not found at $SchemaFile" }

# Load required envs
if (Test-Path $EnvFile) {
  Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^(POSTGRES_USER|POSTGRES_PASSWORD|POSTGRES_DB)=(.*)$') {
      $parts = $_.Split('=',2)
      [System.Environment]::SetEnvironmentVariable($parts[0], $parts[1])
    }
  }
}

# Fallback to compose defaults if not set
if (-not $env:POSTGRES_USER) { $env:POSTGRES_USER = 'ai_agent_user' }
if (-not $env:POSTGRES_DB) { $env:POSTGRES_DB = 'enhanced_ai_os' }

# Try to read password from running container if not present
if (-not $env:POSTGRES_PASSWORD) {
  try {
    $env:POSTGRES_PASSWORD = (docker exec enhanced-ai-postgres printenv POSTGRES_PASSWORD 2>$null)
  } catch {}
}

if (-not $env:POSTGRES_DB -or -not $env:POSTGRES_USER) { Write-Error "POSTGRES_DB/POSTGRES_USER not available" }
if (-not $env:POSTGRES_PASSWORD) { Write-Error "POSTGRES_PASSWORD not available (set in .env or container env)" }

$container = 'enhanced-ai-postgres'
Write-Host "Applying PostgreSQL schema to $container database=$($env:POSTGRES_DB) user=$($env:POSTGRES_USER)"

# Pipe file via stdin with password passed as PGPASSWORD
Get-Content -Raw -LiteralPath $SchemaFile |
  docker exec -e PGPASSWORD=$env:POSTGRES_PASSWORD -i $container psql -U $env:POSTGRES_USER -d $env:POSTGRES_DB

Write-Host "Done. Validating indexes..."
$Query = "SELECT relname FROM pg_class WHERE relkind='i' ORDER BY relname LIMIT 5;"
docker exec -e PGPASSWORD=$env:POSTGRES_PASSWORD -i $container psql -U $env:POSTGRES_USER -d $env:POSTGRES_DB -c $Query

Write-Host "PostgreSQL schema applied successfully."
