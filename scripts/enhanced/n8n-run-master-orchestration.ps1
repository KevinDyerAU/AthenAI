param(
  [string]$BaseUrl = $Env:N8N_BASE_URL,
  [string]$ApiKey = $Env:N8N_API_KEY,
  [string]$WebhookBase = $null,
  [string]$SamplePayloadPath = $null,
  [switch]$Activate
)

if (-not $BaseUrl) { Write-Error "N8N_BASE_URL is not set. Set env var or pass -BaseUrl."; exit 1 }
if (-not $WebhookBase) { $WebhookBase = $BaseUrl }

function Invoke-N8n($Method, $Path, $BodyObj=$null) {
  $headers = @{}
  if ($ApiKey) { $headers['X-N8N-API-KEY'] = $ApiKey }
  $uri = "{0}{1}" -f $BaseUrl.TrimEnd('/'), $Path
  if ($BodyObj -ne $null) {
    $json = ($BodyObj | ConvertTo-Json -Depth 10)
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -ContentType 'application/json' -Body $json
  } else {
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
  }
}

# Locate master orchestration workflow JSON
$wfPath = Join-Path $PSScriptRoot '..' '..' 'workflows' 'enhanced' 'master-orchestration-agent.json'
if (-not (Test-Path $wfPath)) { Write-Error "Workflow file not found: $wfPath"; exit 1 }

try {
  $wfJson = Get-Content -Raw -Path $wfPath | ConvertFrom-Json -ErrorAction Stop
} catch {
  Write-Error "Failed parsing workflow JSON: $($_.Exception.Message)"; exit 1
}

# Attempt to discover webhook path & method from nodes
$webhookNode = $null
if ($wfJson.nodes) {
  foreach ($n in $wfJson.nodes) {
    # Heuristic: node type or name contains webhook, and has parameters.path
    $type = ''
    if ($n.type) { $type = [string]$n.type }
    $name = ''
    if ($n.name) { $name = [string]$n.name }
    if ((($type -match 'webhook') -or ($name -match '(?i)webhook')) -and $n.parameters -and $n.parameters.path) {
      $webhookNode = $n; break
    }
  }
}

if (-not $webhookNode) {
  Write-Warning "No webhook node detected in JSON. Will try to execute by API if possible."
} else {
  $path = $webhookNode.parameters.path
  $method = 'POST'
  if ($webhookNode.parameters.method) { $method = $webhookNode.parameters.method.ToUpper() }
  elseif ($webhookNode.parameters.httpMethod) { $method = $webhookNode.parameters.httpMethod.ToUpper() }
  $webhookUrl = "{0}/webhook/{1}" -f $WebhookBase.TrimEnd('/'), ($path.TrimStart('/'))
}

# Optionally activate workflow in n8n by name (requires API key)
$wfId = $null
if ($ApiKey) {
  try {
    $all = Invoke-N8n 'GET' '/rest/workflows'
    # Try matching by name similar to file name
    $target = $all | Where-Object { $_.name -match '(?i)master.*orchestration' }
    if ($target) { $wfId = $target[0].id }
    if ($Activate -and $wfId) {
      Write-Host "Activating workflow id=$wfId..." -ForegroundColor Cyan
      $body = @{ active = $true }
      $null = Invoke-N8n 'PATCH' ("/rest/workflows/{0}" -f $wfId) $body
      Write-Host " Activated." -ForegroundColor Green
    }
  } catch {
    Write-Warning "Could not query/activate workflows via API. Ensure N8N_API_KEY is set and valid."
  }
}

# Prepare sample payload
$payload = $null
if ($SamplePayloadPath -and (Test-Path $SamplePayloadPath)) {
  try {
    $payload = Get-Content -Raw -Path $SamplePayloadPath | ConvertFrom-Json -ErrorAction Stop
  } catch {
    Write-Warning "Provided sample payload is not valid JSON. Falling back to default."; $payload = $null
  }
}
if (-not $payload) {
  $payload = @{ 
    conversation_id = "conv-local-001";
    user_id = "user-local-001";
    task = "Research and draft a concise brief on the latest trends in retrieval-augmented generation (RAG) and propose an evaluation plan.";
    priority = "normal";
  }
}

# Trigger
if ($webhookUrl) {
  Write-Host ("Triggering webhook: {0} {1}" -f $method, $webhookUrl) -ForegroundColor Cyan
  try {
    if ($method -eq 'GET') {
      $resp = Invoke-RestMethod -Method GET -Uri $webhookUrl
    } else {
      $resp = Invoke-RestMethod -Method POST -Uri $webhookUrl -ContentType 'application/json' -Body ($payload | ConvertTo-Json -Depth 10)
    }
    Write-Host "Webhook accepted. Response:" -ForegroundColor Green
    $resp | ConvertTo-Json -Depth 10
  } catch {
    Write-Warning "Webhook call failed: $($_.Exception.Message)"
  }
} elseif ($wfId) {
  # Fallback: execute via API (requires API key)
  try {
    Write-Host ("Executing workflow id={0} via API..." -f $wfId) -ForegroundColor Cyan
    $body = @{ runData = @{ input = $payload } }
    $resp = Invoke-N8n 'POST' ("/rest/workflows/{0}/run" -f $wfId) $body
    Write-Host "Execution started:" -ForegroundColor Green
    $resp | ConvertTo-Json -Depth 10
  } catch {
    Write-Error "Unable to execute workflow via API. Provide a webhook or valid API key."
    exit 2
  }
} else {
  Write-Error "No webhook discovered and no workflow id resolved. Import the workflow into n8n and/or supply N8N_API_KEY."
  exit 2
}
