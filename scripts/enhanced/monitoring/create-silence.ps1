param(
  [string]$AlertmanagerUrl = "http://localhost:${env:ALERTMANAGER_PORT -as [string] -replace '^$', '9093'}",
  [string]$AlertName = "RabbitMQQueueDepthHigh",
  [string]$Instance = "",
  [string]$Severity = "",
  [string]$Duration = "2h",
  [string]$Comment = "Maintenance window",
  [string]$CreatedBy = "$env:USERNAME"
)

# Build matchers
$matchers = @()
if ($AlertName) { $matchers += @{ name = "alertname"; value = $AlertName; isRegex = $false } }
if ($Instance) { $matchers += @{ name = "instance"; value = $Instance; isRegex = $false } }
if ($Severity) { $matchers += @{ name = "severity"; value = $Severity; isRegex = $false } }

$startsAt = (Get-Date).ToUniversalTime().ToString("o")
$endsAt = (Get-Date).ToUniversalTime().Add([System.Xml.XmlConvert]::ToTimeSpan($Duration)).ToString("o")

$payload = @{ 
  matchers = $matchers
  startsAt = $startsAt
  endsAt = $endsAt
  createdBy = $CreatedBy
  comment = $Comment
}

try {
  $response = Invoke-RestMethod -Method Post -Uri "$AlertmanagerUrl/api/v2/silences" -ContentType 'application/json' -Body ($payload | ConvertTo-Json -Depth 5)
  Write-Host "Silence created with ID: $($response.silenceID)" -ForegroundColor Green
} catch {
  Write-Error "Failed to create silence: $($_.Exception.Message)"
  if ($_.Exception.Response) {
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $reader.BaseStream.Position = 0
    $reader.DiscardBufferedData()
    $body = $reader.ReadToEnd()
    Write-Host "Response body: $body" -ForegroundColor Yellow
  }
  exit 1
}
