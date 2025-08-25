Param(
  [string]$EnvFile = (Join-Path $PSScriptRoot '..' '..' '.env' | Resolve-Path),
  [string]$SchemaFile = (Join-Path $PSScriptRoot '..' '..' 'db' 'neo4j' 'schema.cypher' | Resolve-Path)
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $EnvFile)) { Write-Error ".env not found at $EnvFile" }
if (-not (Test-Path $SchemaFile)) { Write-Error "schema.cypher not found at $SchemaFile" }

# Load required envs
Get-Content $EnvFile | ForEach-Object {
  if ($_ -match '^(NEO4J_PASSWORD)=(.*)$') {
    $parts = $_.Split('=',2)
    [System.Environment]::SetEnvironmentVariable($parts[0], $parts[1])
  }
}

if (-not $env:NEO4J_PASSWORD) { Write-Error "NEO4J_PASSWORD not set in .env" }

$container = 'enhanced-ai-neo4j'
Write-Host "Applying Neo4j schema to $container"

# Pipe file via stdin
Get-Content -Raw -LiteralPath $SchemaFile | docker exec -i $container cypher-shell -a neo4j:7687 -u neo4j -p $env:NEO4J_PASSWORD

Write-Host "Neo4j schema applied successfully."
