param([string]$Target = "./tmp")
Write-Host "[maintenance] Cleaning $Target"
if (Test-Path $Target) { Remove-Item -Recurse -Force $Target }
New-Item -ItemType Directory -Force -Path $Target | Out-Null
Write-Host "[maintenance] Done"
