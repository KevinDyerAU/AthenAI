param([string]$WorkflowsDir = "workflows")
$fail = 0
Get-ChildItem -Recurse -Path $WorkflowsDir -Filter *.json | ForEach-Object {
  Write-Host "[workflow] Validating $($_.FullName)"
  try { Get-Content $_.FullName | ConvertFrom-Json | Out-Null }
  catch { $fail = 1 }
}
exit $fail
