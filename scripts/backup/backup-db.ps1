param(
  [string]$OutDir = "./backups"
)
if (-not $env:DATABASE_URL) { throw "DATABASE_URL not set" }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$file = Join-Path $OutDir "db-backup-$ts.sql"
Write-Host "[backup] Writing $file"
& pg_dump $env:DATABASE_URL | Out-File -FilePath $file -Encoding utf8
Write-Host "[backup] Done"
