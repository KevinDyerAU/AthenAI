# NeoV3 - Unified Local Deployment (PowerShell)
# Usage:
#   .\deploy-local.ps1 [-Fresh] [-Reuse] [-Help]
# Notes:
#   - Runs from repo root. Uses docker-compose.yml at root.
#   - Ensures .env, required directories, and agentnet network.
#   - Phases: core -> monitoring -> n8n -> api
param(
  [switch]$Fresh,
  [switch]$Reuse,
  [switch]$Status,
  [switch]$Check,
  [switch]$Unstructured,
  [switch]$NoUnstructured,
  [switch]$Help
)

$ErrorActionPreference = "Stop"
$Script:Root = Join-Path (Get-Location) "."
$ComposeFile = Join-Path $Script:Root "docker-compose.yml"
$UnstructuredComposeFile = Join-Path $Script:Root "docker-compose.unstructured.yml"
$EnvFile     = Join-Path $Script:Root ".env"
$EnvExamples = @((Join-Path $Script:Root ".env.example"), (Join-Path $Script:Root "unified.env.example"))
$LogFile     = Join-Path $Script:Root "deployment.local.log"

# Temp deployment root (per-run)
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$DeployTmpRoot = Join-Path $Script:Root (Join-Path "deploy_tmp" $Timestamp)
$OverrideFile = Join-Path $DeployTmpRoot "docker-compose.override.yml"

function Write-Log([string]$msg, [string]$level = "INFO") {
  $ts = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  $prefix = switch ($level) { 'ERROR' { '[ERROR]'} 'WARN' { '[WARN]'} 'SUCCESS' { '[SUCCESS]'} default { '[INFO]'} }
  $line = "[$ts] $prefix $msg"
  $line | Tee-Object -FilePath $LogFile -Append | Out-Null
}

# Resolve API host port from env or .env, defaulting to 5000
function Get-ApiPort {
  $p = $env:API_HOST_PORT
  if (-not $p) { $p = Get-DotEnvValue 'API_HOST_PORT' }
  if (-not $p) { $p = 5000 }
  return $p
}

# Verify API JSON health endpoint and fail fast if degraded
function Verify-ApiHealth {
  $port = Get-ApiPort
  $url = "http://localhost:$port/system/health"
  Write-Log "Verifying API health at $url"
  try {
    $resp = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 5 -UseBasicParsing
    $body = $resp.Content
  } catch {
    Write-Log "API health endpoint not reachable at $url" 'ERROR'
    throw
  }
  if ($body -match '"status"\s*:\s*"degraded"') {
    Write-Log ("API health degraded: {0}" -f $body) 'WARN'
    throw "Startup aborted due to degraded API health"
  }
}

function Test-EnvKeys {
  $required = @(
    'POSTGRES_USER','POSTGRES_PASSWORD','POSTGRES_DB',
    'NEO4J_PASSWORD',
    'RABBITMQ_DEFAULT_USER','RABBITMQ_DEFAULT_PASS',
    'API_SECRET_KEY','N8N_ENCRYPTION_KEY','N8N_BASIC_AUTH_PASSWORD','GRAFANA_SECURITY_ADMIN_PASSWORD'
  )
  if (-not (Test-Path $EnvFile)) { Write-Log ".env not found at $EnvFile" 'ERROR'; return $false }
  $text = Get-Content -Raw -LiteralPath $EnvFile
  $missing = @()
  foreach ($k in $required) { if (-not ($text -match "(?m)^\s*${k}\s*=\S+")) { $missing += $k } }
  if ($missing.Count -gt 0) {
    Write-Log ("Missing required keys in .env: {0}" -f ($missing -join ', ')) 'ERROR'
    return $false
  }
  if ($UseUnstructured) {
    if (-not ($text -match "(?m)^\s*UNSTRUCTURED_QUEUE\s*=\S+")) { Write-Log "UNSTRUCTURED_QUEUE not set; default will be used (documents.process)" 'WARN' }
  }
  Write-Log "All required .env keys present" 'SUCCESS'
  return $true
}

function Invoke-Check {
  Write-Log "Running preflight checks (no changes)"
  Test-RequiredTools
  $envOk = $false
  if (Test-Path $EnvFile) { $envOk = Test-EnvKeys } else { Write-Log ".env not found at $EnvFile" 'ERROR' }
  try {
    if ($UseUnstructured -and (Test-Path $UnstructuredComposeFile)) {
      Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $UnstructuredComposeFile config | Out-Null
    } else {
      Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile config | Out-Null
    }
    Write-Log "docker-compose config OK" 'SUCCESS'
  } catch { Write-Log "docker-compose config failed: $($_.Exception.Message)" 'ERROR' }
  Write-Host "`n=== existing containers (if any) ===";
  try {
    if ($UseUnstructured -and (Test-Path $UnstructuredComposeFile)) {
      Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $UnstructuredComposeFile ps
    } else {
      Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile ps
    }
  } catch {}
  Write-Host "`n=== health (if running) ==="; @(
    'enhanced-ai-postgres',
    'enhanced-ai-neo4j',
    'enhanced-ai-rabbitmq',
    'enhanced-ai-n8n',
    'enhanced-ai-prometheus',
    'enhanced-ai-grafana',
    'enhanced-ai-loki',
    'enhanced-ai-alertmanager',
    'enhanced-ai-agent-api'
  ) | ForEach-Object { Get-ContainerHealth $_ } | Out-Host
  if (-not $envOk) { exit 2 } else { exit 0 }
}

function Get-ContainerHealth([string]$name) {
  $state = $(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' $name 2>$null)
  if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($state)) { "$( $name ): not found" }
  else { "$( $name ): $( $state )" }
}

function Invoke-ResetFresh {
  Write-Log "Performing full reset: clearing deploy_tmp, recreating .env and secrets" 'WARN'
  try {
    $tmpRoot = Join-Path $Script:Root 'deploy_tmp'
    if (Test-Path $tmpRoot) { Remove-Item -Recurse -Force -LiteralPath $tmpRoot }
  } catch { Write-Log "Failed to clear deploy_tmp: $($_.Exception.Message)" 'WARN' }
  try {
    if (Test-Path $EnvFile) { Remove-Item -Force -LiteralPath $EnvFile }
  } catch { Write-Log "Failed to remove .env: $($_.Exception.Message)" 'WARN' }
  # Recreate fresh .env from example and regenerate all secrets
  Initialize-EnvFile
  Initialize-Secrets
}

function Test-HttpEndpoint([string]$label, [string]$url) {
  try {
    $resp = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 5 -UseBasicParsing
    if ($resp.StatusCode -in 200,204) { Write-Log "$( $label ) HTTP OK ($($resp.StatusCode)) - $( $url )" 'SUCCESS' }
    else { Write-Log "$( $label ) HTTP check failed ($($resp.StatusCode)) - $( $url )" 'WARN' }
  } catch {
    Write-Log "$( $label ) HTTP check failed (no-conn) - $( $url )" 'WARN'
  }
}

# Read a key from the .env file (simple KEY=VALUE parser, ignores comments)
function Get-DotEnvValue([string]$key) {
  if (-not (Test-Path $EnvFile)) { return $null }
  try {
    $line = Select-String -Path $EnvFile -Pattern "^(?i)\s*${key}\s*=\s*(.*)$" -SimpleMatch:$false -CaseSensitive:$false -Encoding UTF8 -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $line) { return $null }
    $val = $line.Matches[0].Groups[1].Value.Trim()
    # Strip optional surrounding quotes
    if ($val.StartsWith('"') -and $val.EndsWith('"')) { $val = $val.Substring(1, $val.Length-2) }
    if ($val.StartsWith("'") -and $val.EndsWith("'")) { $val = $val.Substring(1, $val.Length-2) }
    return $val
  } catch { return $null }
}

function Show-Usage {
  @"
NeoV3 Local Deployment (PowerShell)

Usage: .\deploy-local.ps1 [-Fresh] [-Reuse] [-Status] [-Check] [-Unstructured] [-NoUnstructured] [-Help]

Options:
  -Fresh   FULL RESET: down -v, clear deploy_tmp/, recreate .env and secrets
  -Reuse   Reuse existing containers (no recreate), skip pulls
  -Status  Print docker compose ps and per-container health and exit
  -Check   Validate tools, .env keys, and compose config (no changes)
  -Unstructured Include Unstructured worker overlay (default)
  -NoUnstructured Opt out of Unstructured worker (default is ON)
  -Help    Show this help and exit

Phases:
  1) Core: postgres, neo4j, rabbitmq (wait healthy)
  2) Monitoring: prometheus, grafana, loki, promtail, alertmanager, otel-collector
  3) Orchestration: n8n
  4) API: build and start
"@ | Write-Output
}

if ($Help) { Show-Usage; exit 0 }
if ($Fresh -and $Reuse) { Write-Log "-Fresh and -Reuse cannot be used together" "ERROR"; exit 1 }

# Args mapping
$SkipPull = $false
$DockerUpArgs = ""
if ($Reuse) { $SkipPull = $true; $DockerUpArgs = "--no-recreate" }
if ($Fresh) { $SkipPull = $false; $DockerUpArgs = "--force-recreate --build" }

# Unstructured default: ON unless explicitly opted out
$UseUnstructured = $true
if ($NoUnstructured) { $UseUnstructured = $false }
elseif ($Unstructured) { $UseUnstructured = $true }

# Helpers
function Dc {
  param([Parameter(ValueFromRemainingArguments=$true)]$Args)
  if (Get-Command docker -ErrorAction SilentlyContinue) {
    try { & docker compose @Args; return } catch {}
  }
  if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    & docker-compose @Args; return
  }
  throw "Docker Compose not found"
}

function Test-RequiredTools {
  $dockerOk = (Get-Command docker -ErrorAction SilentlyContinue)
  $dcOk = $false
  if ($dockerOk) {
    try { docker info | Out-Null } catch { throw "Docker daemon not running" }
    try { docker compose version | Out-Null; $dcOk = $true } catch {}
  }
  if (-not $dcOk) {
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) { $dcOk = $true }
  }
  if (-not $dcOk) { throw "Docker Compose (v2 or v1) not available" }
}

function Initialize-EnvFile {
  if (Test-Path $EnvFile) { Write-Log ".env found"; return }
  foreach ($cand in $EnvExamples) {
    if (Test-Path $cand) {
      Copy-Item $cand $EnvFile -Force
      Write-Log "Created .env from $(Split-Path $cand -Leaf). Review secrets before first run" "WARN"
      return
    }
  }
  throw "No .env found. Add $EnvFile first."
}

function New-SecretString([int]$length = 32) {
  $pool = @(); $pool += 48..57; $pool += 65..90; $pool += 97..122; $pool += 33,35,36,37,38,64
  -join (1..$length | ForEach-Object { [char]$pool[(Get-Random -Min 0 -Max $pool.Count)] })
}

function Set-Env-IfMissing([string]$key, [string]$value) {
  if (-not (Test-Path $EnvFile)) { throw ".env not found for Set-Env-IfMissing" }
  $pattern = "^\s*${key}\s*="
  $exists = Select-String -Path $EnvFile -Pattern $pattern -Quiet
  if (-not $exists) { Add-Content -LiteralPath $EnvFile -Value "$key=$value"; Write-Log "Initialized $key in .env" }
}

function Initialize-Secrets {
  Write-Log "Ensuring required secrets in .env"
  # Align API and Postgres credentials
  Set-Env-IfMissing -key 'POSTGRES_USER' -value 'ai_agent_user'
  Set-Env-IfMissing -key 'POSTGRES_DB' -value 'enhanced_ai_os'
  Set-Env-IfMissing -key 'POSTGRES_PASSWORD' -value (New-SecretString 32)
  # Defaults for Compose variable expansion (suppress warnings)
  Set-Env-IfMissing -key 'POSTGRES_HOST' -value 'postgres'
  Set-Env-IfMissing -key 'POSTGRES_PORT' -value '5432'

  # Neo4j
  Set-Env-IfMissing -key 'NEO4J_PASSWORD' -value (New-SecretString 32)

  # RabbitMQ
  Set-Env-IfMissing -key 'RABBITMQ_DEFAULT_USER' -value 'ai_agent_queue_user'
  Set-Env-IfMissing -key 'RABBITMQ_DEFAULT_PASS' -value (New-SecretString 32)

  # API and tooling
  Set-Env-IfMissing -key 'API_SECRET_KEY' -value (New-SecretString 48)
  Set-Env-IfMissing -key 'GRAFANA_SECURITY_ADMIN_PASSWORD' -value (New-SecretString 32)
  Set-Env-IfMissing -key 'N8N_ENCRYPTION_KEY' -value (New-SecretString 48)
  # n8n basic auth defaults (align with compose defaults)
  Set-Env-IfMissing -key 'N8N_BASIC_AUTH_ACTIVE' -value 'true'
  Set-Env-IfMissing -key 'N8N_BASIC_AUTH_USER' -value 'admin'
  Set-Env-IfMissing -key 'N8N_BASIC_AUTH_PASSWORD' -value (New-SecretString 32)
}

function Initialize-Directories {
  if (-not (Test-Path $DeployTmpRoot)) { New-Item -ItemType Directory -Path $DeployTmpRoot -Force | Out-Null }
  $paths = @(
    "enhanced-ai-agent-os/data/postgres",
    "enhanced-ai-agent-os/backups/postgres",
    "enhanced-ai-agent-os/data/neo4j/data",
    "enhanced-ai-agent-os/data/neo4j/logs",
    "enhanced-ai-agent-os/data/neo4j/import",
    "enhanced-ai-agent-os/data/neo4j/plugins",
    "enhanced-ai-agent-os/backups/neo4j",
    "enhanced-ai-agent-os/data/rabbitmq",
    "enhanced-ai-agent-os/logs/rabbitmq",
    "enhanced-ai-agent-os/backups/rabbitmq",
    "enhanced-ai-agent-os/data/n8n",
    "enhanced-ai-agent-os/logs/n8n",
    "enhanced-ai-agent-os/backups/n8n",
    "enhanced-ai-agent-os/data/prometheus",
    "enhanced-ai-agent-os/data/grafana",
    "enhanced-ai-agent-os/logs/grafana",
    "enhanced-ai-agent-os/data/alertmanager",
    "enhanced-ai-agent-os/data/loki",
    "logs/api",
    "data/api",
    # Unstructured worker (created regardless; used when -Unstructured)
    "data/unstructured",
    "logs/unstructured"
  )
  foreach ($p in $paths) { $full = Join-Path $DeployTmpRoot $p; if (-not (Test-Path $full)) { New-Item -ItemType Directory -Path $full -Force | Out-Null } }
}

function New-NetworkIfMissing { if (-not (docker network ls --format '{{.Name}}' | Select-String -SimpleMatch 'agentnet' -Quiet)) { docker network create agentnet | Out-Null } }

function Invoke-ComposeDownFresh { if (Test-Path $ComposeFile) { Dc --project-directory $Script:Root -f $ComposeFile --env-file $EnvFile down -v | Out-Null } }
function Invoke-BuildAll {
  Write-Log "Building images (docker compose build)"
  try { Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $OverrideFile build | Out-Null; Write-Log "Build completed" 'SUCCESS' } catch { Write-Log ("Build failed: {0}" -f $_.Exception.Message) 'ERROR'; throw }
}
function New-OverrideFile {
  $content = @"
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/data/postgres
  postgres_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/backups/postgres

  neo4j_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/data/neo4j/data
  neo4j_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/data/neo4j/logs
  neo4j_import:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/data/neo4j/import
  neo4j_plugins:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/data/neo4j/plugins
  neo4j_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/backups/neo4j

  rabbitmq_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/data/rabbitmq
  rabbitmq_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/logs/rabbitmq
  rabbitmq_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/backups/rabbitmq

  n8n_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/data/n8n
  n8n_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/logs/n8n
  n8n_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/backups/n8n

  prometheus_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/data/prometheus

  grafana_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/data/grafana
  grafana_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/logs/grafana

  alertmanager_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/data/alertmanager

  loki_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/enhanced-ai-agent-os/data/loki

  api-logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/logs/api
  api-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DeployTmpRoot}/data/api
"@
  if (-not (Test-Path (Split-Path $OverrideFile -Parent))) { New-Item -ItemType Directory -Path (Split-Path $OverrideFile -Parent) -Force | Out-Null }
  Set-Content -LiteralPath $OverrideFile -Value $content -NoNewline
}

function Update-GitIgnore {
  $gi = Join-Path $Script:Root ".gitignore"
  if (-not (Test-Path $gi)) {
    Set-Content -LiteralPath $gi -Value "deploy_tmp/`n.env`ndeployment.local.log`n"
  }
  else {
    $needs = @('deploy_tmp/','.env','deployment.local.log')
    $cur = Get-Content -LiteralPath $gi -ErrorAction SilentlyContinue
    foreach ($n in $needs) { if (-not ($cur -contains $n)) { Add-Content -LiteralPath $gi -Value ($n + "`n") } }
  }
}

function Wait-Healthy([string]$name, [int]$seconds = 360) {
  $deadline = (Get-Date).AddSeconds($seconds)
  while ((Get-Date) -lt $deadline) {
    $state = $(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' $name 2>$null)
    if ($LASTEXITCODE -eq 0 -and $state -eq 'healthy') { Write-Log "$name healthy" 'SUCCESS'; return }

    # Fallback for n8n: if container is running or starting but not yet marked healthy, try HTTP healthz with Basic Auth if set
    if ($name -eq 'enhanced-ai-n8n' -and $LASTEXITCODE -eq 0 -and ($state -in @('running','starting'))) {
      $port = if ($env:N8N_PORT) { $env:N8N_PORT } else { (Get-DotEnvValue 'N8N_PORT') }
      if (-not $port) { $port = 5678 }
      $user = if ($env:N8N_BASIC_AUTH_USER) { $env:N8N_BASIC_AUTH_USER } else { (Get-DotEnvValue 'N8N_BASIC_AUTH_USER') }
      $pass = if ($env:N8N_BASIC_AUTH_PASSWORD) { $env:N8N_BASIC_AUTH_PASSWORD } else { (Get-DotEnvValue 'N8N_BASIC_AUTH_PASSWORD') }
      $headers = @{}
      $usingAuth = $false
      if ($user -and $pass) {
        $pair = "{0}:{1}" -f $user, $pass
        $basic = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
        $headers['Authorization'] = "Basic $basic"
        $usingAuth = $true
      }
      try {
        $resp = Invoke-WebRequest -Uri "http://localhost:$port/healthz" -Method GET -TimeoutSec 5 -UseBasicParsing -Headers $headers
        $code = $resp.StatusCode
        if ($usingAuth) { Write-Log ("n8n HTTP /healthz probe (auth) -> {0}" -f $code) 'INFO' } else { Write-Log ("n8n HTTP /healthz probe (no-auth) -> {0}" -f $code) 'INFO' }
        if ($code -in 200,204) { Write-Log "$name HTTP healthz OK; proceeding despite docker health='$state'" 'WARN'; return }
      } catch {
        if ($usingAuth) { Write-Log "n8n HTTP /healthz probe (auth) -> no-conn" 'INFO' } else { Write-Log "n8n HTTP /healthz probe (no-auth) -> no-conn" 'INFO' }
      }
    }

    Start-Sleep -Seconds 5
  }
  throw "Timeout waiting for $name to be healthy"
}

function Invoke-PhaseCore {
  Write-Log "Starting core: postgres, neo4j, rabbitmq"
  if ($UseUnstructured -and (Test-Path $UnstructuredComposeFile)) {
    Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $UnstructuredComposeFile -f $OverrideFile up -d $DockerUpArgs postgres neo4j rabbitmq
  } else {
    Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $OverrideFile up -d $DockerUpArgs postgres neo4j rabbitmq
  }
  Wait-Healthy 'enhanced-ai-postgres' 300
  Wait-Healthy 'enhanced-ai-neo4j' 480
  Wait-Healthy 'enhanced-ai-rabbitmq' 300
}

# Optional phase: Unstructured worker
function Invoke-PhaseUnstructured {
  if (-not $UseUnstructured) { return }
  if (-not (Test-Path $UnstructuredComposeFile)) { Write-Log "-Unstructured specified but overlay not found at $UnstructuredComposeFile; skipping" 'WARN'; return }
  Write-Log "Starting Unstructured worker"
  try { Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $UnstructuredComposeFile -f $OverrideFile build unstructured-worker | Out-Null } catch {}
  Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $UnstructuredComposeFile -f $OverrideFile up -d $DockerUpArgs unstructured-worker
  try { Wait-Healthy 'neov3-unstructured-worker' 240 } catch { Write-Log "Unstructured worker not healthy yet" 'WARN' }
}

function Invoke-DatabaseMigrations {
  Write-Log "Applying database migrations (Postgres, Neo4j)"
  $pgScript = Join-Path $Script:Root "scripts\migrations\apply-postgres.ps1"
  $neoScript = Join-Path $Script:Root "scripts\migrations\apply-neo4j.ps1"
  if (Test-Path $pgScript) {
    try { & $pgScript; Write-Log "Postgres migration completed" 'SUCCESS' } catch { Write-Log ("Postgres migration failed: {0}" -f $_.Exception.Message) 'ERROR'; throw }
  } else { Write-Log "Postgres migration script not found at $pgScript" 'WARN' }
  if (Test-Path $neoScript) {
    try { & $neoScript; Write-Log "Neo4j migration completed" 'SUCCESS' } catch { Write-Log ("Neo4j migration failed: {0}" -f $_.Exception.Message) 'ERROR'; throw }
  } else { Write-Log "Neo4j migration script not found at $neoScript" 'WARN' }
}

function Invoke-PhaseMonitoring {
  Write-Log "Starting monitoring stack"
  try {
    if ($UseUnstructured -and (Test-Path $UnstructuredComposeFile)) {
      Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $UnstructuredComposeFile -f $OverrideFile up -d $DockerUpArgs prometheus grafana loki promtail alertmanager otel-collector
    } else {
      Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $OverrideFile up -d $DockerUpArgs prometheus grafana loki promtail alertmanager otel-collector
    }
  } catch { Write-Log $_.Exception.Message 'WARN' }
  $gp = ${env:GRAFANA_PORT}; if (-not $gp) { $gp = 3000 }
  $pp = ${env:PROMETHEUS_PORT}; if (-not $pp) { $pp = 9090 }
  $lp = ${env:LOKI_PORT}; if (-not $lp) { $lp = 3100 }
  $ap = ${env:ALERTMANAGER_PORT}; if (-not $ap) { $ap = 9093 }
  Test-HttpEndpoint -label 'Grafana' -url "http://localhost:$gp/api/health"
  Test-HttpEndpoint -label 'Prometheus' -url "http://localhost:$pp/-/ready"
  Test-HttpEndpoint -label 'Alertmanager' -url "http://localhost:$ap/-/ready"
  Test-HttpEndpoint -label 'Loki' -url "http://localhost:$lp/ready"
}

function Invoke-PhaseOrchestration {
  Write-Log "Starting orchestration: n8n"
  Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $OverrideFile up -d $DockerUpArgs n8n
  try { Wait-Healthy 'enhanced-ai-n8n' 420 } catch { Write-Log "n8n not healthy yet" 'WARN' }
}

function Invoke-PhaseAPI {
  Write-Log "Building and starting API"
  if ($UseUnstructured -and (Test-Path $UnstructuredComposeFile)) {
    Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $UnstructuredComposeFile -f $OverrideFile build api-service
    Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $UnstructuredComposeFile -f $OverrideFile up -d $DockerUpArgs api-service
  } else {
    Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $OverrideFile build api-service
    Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $OverrideFile up -d $DockerUpArgs api-service
  }
  Wait-Healthy 'enhanced-ai-agent-api' 300
  # Extra verification from host perspective
  try { Verify-ApiHealth } catch { throw }
}

function Write-Summary {
  Write-Host "`n=== docker compose ps ==="
  if ($UseUnstructured -and (Test-Path $UnstructuredComposeFile)) {
    Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $UnstructuredComposeFile -f $OverrideFile ps
  } else {
    Dc --project-directory $Script:Root --env-file $EnvFile -f $ComposeFile -f $OverrideFile ps
  }
  Write-Host "`n=== health summary ==="
  @(
    'enhanced-ai-postgres',
    'enhanced-ai-neo4j',
    'enhanced-ai-rabbitmq',
    'neov3-unstructured-worker',
    'enhanced-ai-n8n',
    'enhanced-ai-prometheus',
    'enhanced-ai-grafana',
    'enhanced-ai-loki',
    'enhanced-ai-alertmanager',
    'enhanced-ai-agent-api'
  ) | ForEach-Object { Get-ContainerHealth $_ } | Tee-Object -FilePath $LogFile -Append | Out-Host
}

# Main
: > $LogFile
Write-Log "Starting deploy-local.ps1 Fresh=$Fresh Reuse=$Reuse Status=$Status Check=$Check"
if ($Check) { Invoke-Check }
Test-RequiredTools
if ($Fresh) { Invoke-ComposeDownFresh; Invoke-ResetFresh }
Initialize-EnvFile
Initialize-Secrets
Initialize-Directories
New-OverrideFile
Update-GitIgnore
New-NetworkIfMissing
if (-not $SkipPull) {
  Write-Log "docker compose pull"
  try {
    if ($UseUnstructured -and (Test-Path $UnstructuredComposeFile)) {
      Dc --project-directory $Script:Root -f $ComposeFile -f $UnstructuredComposeFile -f $OverrideFile --env-file $EnvFile pull | Out-Null
    } else {
      Dc --project-directory $Script:Root -f $ComposeFile -f $OverrideFile --env-file $EnvFile pull | Out-Null
    }
  } catch { Write-Log $_.Exception.Message 'WARN' }
}
if ($Fresh) { Invoke-BuildAll }
if ($Status) { Write-Summary; exit 0 }
Invoke-PhaseCore
Invoke-PhaseUnstructured
Invoke-DatabaseMigrations
Invoke-PhaseMonitoring
Invoke-PhaseOrchestration
Invoke-PhaseAPI
Write-Summary
Write-Log ("Local deployment completed. API http://localhost:{0} Grafana http://localhost:3000 Prometheus http://localhost:9090 n8n http://localhost:5678" -f (Get-ApiPort)) 'SUCCESS'
