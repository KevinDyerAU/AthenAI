param(
  [string]$BaseUrl = $Env:N8N_BASE_URL,
  [string]$ApiKey = $Env:N8N_API_KEY,
  [switch]$UpdateIfExists
)

if (-not $BaseUrl) { Write-Error "N8N_BASE_URL is not set. Set env var or pass -BaseUrl."; exit 1 }
if (-not $ApiKey) { Write-Error "N8N_API_KEY is required to import workflows via API."; exit 1 }

function Invoke-N8n($Method, $Path, $BodyObj=$null) {
  $headers = @{ 'X-N8N-API-KEY' = $ApiKey }
  $uri = "{0}{1}" -f $BaseUrl.TrimEnd('/'), $Path
  if ($null -ne $BodyObj) {
    $json = ($BodyObj | ConvertTo-Json -Depth 20)
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -ContentType 'application/json' -Body $json
  } else {
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
  }
}

$dir = Join-Path $PSScriptRoot '..' '..' 'workflows' 'enhanced'
$files = Get-ChildItem -Path $dir -Filter '*.json' -ErrorAction Stop
if (-not $files) { Write-Error "No workflow files found in $dir"; exit 1 }

# Get existing workflows for update detection
$existing = @{}
try {
  $all = Invoke-N8n 'GET' '/rest/workflows'
  foreach ($w in $all) { $existing[$w.name] = $w }
} catch {
  Write-Error "Failed to list existing workflows: $($_.Exception.Message)"; exit 1
}

foreach ($f in $files) {
  Write-Host ("Processing {0}" -f $f.Name) -ForegroundColor Cyan
  try {
    $wf = Get-Content -Raw -Path $f.FullName | ConvertFrom-Json -ErrorAction Stop
  } catch {
    Write-Warning (" Skipping invalid JSON: {0}" -f $f.Name)
    continue
  }

  # n8n expects workflow payload with nodes, connections, name, settings, staticData, etc.
  # Use file contents as-is if they match export schema; otherwise, map minimal fields.
  $payload = @{}
  if (($wf.PSObject.Properties.Name -contains 'nodes') -and ($wf.PSObject.Properties.Name -contains 'connections')) {
    $payload = $wf
  } else {
    # Minimal wrapper
    $nameVal = $f.BaseName
    if ($wf.name) { $nameVal = [string]$wf.name }
    $settingsVal = @{}
    if ($wf.settings) { $settingsVal = $wf.settings }
    $staticVal = @{}
    if ($wf.staticData) { $staticVal = $wf.staticData }
    $payload = @{ nodes = $wf.nodes; connections = $wf.connections; name = $nameVal; settings = $settingsVal; staticData = $staticVal }
  }

  $name = $f.BaseName
  if ($payload.name) { $name = [string]$payload.name }
  if ($existing.ContainsKey($name)) {
    if ($UpdateIfExists) {
      $id = $existing[$name].id
      Write-Host (" Updating existing workflow '{0}' (id={1})" -f $name, $id)
      try {
        $null = Invoke-N8n 'PATCH' ("/rest/workflows/{0}" -f $id) $payload
        Write-Host "  Updated." -ForegroundColor Green
      } catch {
        Write-Warning ("  Update failed: {0}" -f $_.Exception.Message)
      }
    } else {
      Write-Host (" Skipping import; workflow '{0}' already exists. Use -UpdateIfExists to update." -f $name) -ForegroundColor Yellow
    }
  } else {
    Write-Host (" Creating new workflow '{0}'" -f $name)
    try {
      $null = Invoke-N8n 'POST' '/rest/workflows' $payload
      Write-Host "  Created." -ForegroundColor Green
    } catch {
      Write-Warning ("  Create failed: {0}" -f $_.Exception.Message)
    }
  }
}
