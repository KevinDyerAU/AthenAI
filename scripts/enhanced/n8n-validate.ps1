param(
  [string]$BaseUrl = $Env:N8N_BASE_URL,
  [string]$ApiKey = $Env:N8N_API_KEY
)

if (-not $BaseUrl) { Write-Error "N8N_BASE_URL is not set. Set env var or pass -BaseUrl."; exit 1 }

function Invoke-N8nGet($Path) {
  $headers = @{}
  if ($ApiKey) { $headers['X-N8N-API-KEY'] = $ApiKey }
  try {
    return Invoke-RestMethod -Method GET -Uri ("{0}{1}" -f $BaseUrl.TrimEnd('/'), $Path) -Headers $headers -ErrorAction Stop
  } catch {
    Write-Error "Request GET $Path failed: $($_.Exception.Message)"; throw
  }
}

Write-Host "[1/4] Checking n8n health..." -ForegroundColor Cyan
try {
  $null = Invoke-N8nGet '/rest/healthz'
  Write-Host " n8n health: OK" -ForegroundColor Green
} catch {
  Write-Warning " Could not query /rest/healthz. Continuing, but API key or URL may be wrong."
}

Write-Host "[2/4] Listing n8n credentials..." -ForegroundColor Cyan
$credentials = @()
try {
  $credentials = Invoke-N8nGet '/rest/credentials'
} catch {
  Write-Warning " Could not fetch credentials. If API key is missing, set N8N_API_KEY."
}

$credIndexByType = @{}
$credNames = @{}
foreach ($c in $credentials) {
  $t = $c.type
  if (-not $credIndexByType.ContainsKey($t)) { $credIndexByType[$t] = @() }
  $credIndexByType[$t] += $c.name
  $credNames[$c.name] = $true
}

Write-Host (" Found {0} credentials across {1} types" -f $credentials.Count, $credIndexByType.Keys.Count)

Write-Host "[3/4] Scanning local enhanced workflows for required credentials..." -ForegroundColor Cyan
$workflowFiles = Get-ChildItem -Path (Join-Path $PSScriptRoot '..' '..' 'workflows' 'enhanced') -Filter '*.json' -Recurse -ErrorAction SilentlyContinue
if (-not $workflowFiles) { Write-Error "No workflow files found under workflows/enhanced/."; exit 1 }

$result = @()
foreach ($wf in $workflowFiles) {
  try {
    $json = Get-Content -Raw -Path $wf.FullName | ConvertFrom-Json -ErrorAction Stop
  } catch {
    Write-Warning (" Skipping {0}: invalid JSON ({1})" -f $wf.Name, $_.Exception.Message)
    continue
  }

  $neededTypes = New-Object System.Collections.Generic.HashSet[string]
  $neededNamedCreds = New-Object System.Collections.Generic.HashSet[string]

  if ($json.nodes) {
    foreach ($n in $json.nodes) {
      if ($n.credentials) {
        $credProps = $n.credentials.PSObject.Properties
        foreach ($p in $credProps) {
          # $p.Name is credential type (e.g., 'openAiApi') in typical n8n exports
          $neededTypes.Add($p.Name) | Out-Null
          $val = $p.Value
          if ($val -and $val.name) { $null = $neededNamedCreds.Add([string]$val.name) }
        }
      }
    }
  }

  # Compare against available creds in n8n
  $missingTypes = @()
  foreach ($t in $neededTypes) {
    if (-not $credIndexByType.ContainsKey($t)) { $missingTypes += $t }
  }
  $missingNamed = @()
  foreach ($nm in $neededNamedCreds) {
    if (-not $credNames.ContainsKey($nm)) { $missingNamed += $nm }
  }

  $result += [pscustomobject]@{
    WorkflowFile = $wf.Name
    RequiredTypes = ($neededTypes | Sort-Object) -join ', '
    MissingTypes  = ($missingTypes | Sort-Object) -join ', '
    RequiredNamed = ($neededNamedCreds | Sort-Object) -join ', '
    MissingNamed  = ($missingNamed | Sort-Object) -join ', '
  }
}

Write-Host "[4/4] Report" -ForegroundColor Cyan
$result | Format-Table -AutoSize

$anyMissing = $false
foreach ($row in $result) { if ($row.MissingTypes -or $row.MissingNamed) { $anyMissing = $true; break } }
if ($anyMissing) {
  Write-Warning "Some workflows have unresolved credential requirements. Create the missing credentials in n8n and re-run this script."
  exit 2
} else {
  Write-Host "All enhanced workflows appear to have matching credentials in n8n (by type/name)." -ForegroundColor Green
}
