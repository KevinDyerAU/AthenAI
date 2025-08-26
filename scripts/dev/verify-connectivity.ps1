<#
.SYNOPSIS
  Verifies connectivity to core services used by autonomous agents: Neo4j and RabbitMQ.
#>

$ErrorActionPreference = 'Stop'

function Test-Tcp($host, $port, $timeoutSec = 5) {
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $iar = $client.BeginConnect($host, $port, $null, $null)
    $success = $iar.AsyncWaitHandle.WaitOne([TimeSpan]::FromSeconds($timeoutSec))
    if (-not $success) { return $false }
    $client.EndConnect($iar)
    $client.Close()
    return $true
  } catch { return $false }
}

# Load .env if present to read passwords
$envPath = Join-Path $PSScriptRoot "..\..\.env"
if (Test-Path -LiteralPath $envPath) {
  Get-Content $envPath | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object {
    $name,$value = $_.Split('=',2)
    if (-not [string]::IsNullOrWhiteSpace($name)) { $env:$name = $value }
  }
}

Write-Host "Testing Neo4j bolt connectivity..." -ForegroundColor Cyan
$neoHost = $env:NEO4J_HOST; if (-not $neoHost) { $neoHost = 'localhost' }
$neoPort = if ($env:NEO4J_BOLT_PORT) { [int]$env:NEO4J_BOLT_PORT } else { 7687 }
if (Test-Tcp $neoHost $neoPort) {
  Write-Host "  TCP $neoHost:$neoPort OK" -ForegroundColor Green
} else {
  Write-Host "  TCP $neoHost:$neoPort FAILED" -ForegroundColor Red
}

# Try a cypher-shell query via docker (best-effort)
try {
  $password = $env:NEO4J_PASSWORD
  if ($password) {
    $result = docker exec neo4j cypher-shell -u neo4j -p $password "RETURN 1 AS ok" 2>$null
    if ($LASTEXITCODE -eq 0 -and $result -match 'ok') {
      Write-Host "  Cypher-shell query OK" -ForegroundColor Green
    } else {
      Write-Host "  Cypher-shell query FAILED" -ForegroundColor Yellow
    }
  } else {
    Write-Host "  Skipping cypher-shell (NEO4J_PASSWORD not set)" -ForegroundColor DarkYellow
  }
} catch {
  Write-Host "  Cypher-shell check errored: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "Testing RabbitMQ connectivity..." -ForegroundColor Cyan
$rHost = if ($env:RABBITMQ_HOST) { $env:RABBITMQ_HOST } else { 'localhost' }
$rPort = if ($env:RABBITMQ_PORT) { [int]$env:RABBITMQ_PORT } else { 5672 }
if (Test-Tcp $rHost $rPort) {
  Write-Host "  TCP $rHost:$rPort OK" -ForegroundColor Green
} else {
  Write-Host "  TCP $rHost:$rPort FAILED" -ForegroundColor Red
}

# Try management API if creds available
$rmqUser = if ($env:RABBITMQ_DEFAULT_USER) { $env:RABBITMQ_DEFAULT_USER } else { $env:RABBITMQ_USER }
$rmqPass = if ($env:RABBITMQ_DEFAULT_PASS) { $env:RABBITMQ_DEFAULT_PASS } else { $env:RABBITMQ_PASSWORD }
$mgmtPort = if ($env:RABBITMQ_MANAGEMENT_PORT) { [int]$env:RABBITMQ_MANAGEMENT_PORT } else { 15672 }
$mgmtUrl  = "http://$rHost:$mgmtPort/rabbitmq/api/overview"
if ($rmqUser -and $rmqPass) {
  try {
    $pair = "$rmqUser:$rmqPass"
    $basic = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
    $headers = @{ Authorization = "Basic $basic" }
    $resp = Invoke-WebRequest -Uri $mgmtUrl -Headers $headers -UseBasicParsing -TimeoutSec 5
    if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300) {
      Write-Host "  RabbitMQ Management API OK" -ForegroundColor Green
    } else {
      Write-Host "  RabbitMQ Management API returned $($resp.StatusCode)" -ForegroundColor Yellow
    }
  } catch {
    Write-Host "  RabbitMQ Management API check failed: $($_.Exception.Message)" -ForegroundColor Yellow
  }
} else {
  Write-Host "  Skipping management API (no credentials provided)" -ForegroundColor DarkYellow
}

Write-Host "Connectivity verification complete." -ForegroundColor Cyan
