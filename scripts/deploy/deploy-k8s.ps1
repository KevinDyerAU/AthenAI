Param(
  [string]$Environment = "dev",
  [string]$Namespace = ""
)

$ErrorActionPreference = "Stop"
$overlay = "infrastructure/k8s/overlays/$Environment"
if (-not (Test-Path $overlay)) {
  Write-Error "Unknown environment: $Environment. Available: $(Get-ChildItem infrastructure/k8s/overlays | ForEach-Object Name | Sort-Object -Unique)"
}

kubectl apply -k $overlay

Write-Host "Waiting for api-service rollout..."
if (-not $Namespace -or $Namespace -eq "") {
  $nsLine = Select-String -Path "$overlay/kustomization.yaml" -Pattern '^namespace:' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($nsLine) {
    $Namespace = ($nsLine.Line -split ':')[1].Trim()
  } else {
    $Namespace = "neov3"
  }
}

$deployName = kubectl -n $Namespace get deploy -l app=api-service -o jsonpath='{.items[0].metadata.name}'
if (-not $deployName) {
  Write-Error "api-service deployment not found in namespace $Namespace"
}

kubectl -n $Namespace rollout status deploy/$deployName --timeout=180s
Write-Host "Deployment applied for environment: $Environment"
