param(
  [string]$Rabbit = $env:RABBITMQ_URL,
  [string]$Queue = ${env:UNSTRUCTURED_QUEUE},
  [string]$DocId = "doc-n8n-guide"
)

if (-not $Rabbit) { $Rabbit = "amqp://guest:guest@localhost:5672/" }
if (-not $Queue) { $Queue = "documents.process" }

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$publisher = Join-Path $repoRoot "e2e/unstructured_publish.py"

# Prefer venv python if present
$venvPython = Join-Path (Join-Path $repoRoot "..") ".venv/Scripts/python.exe"
if (Test-Path $venvPython) {
  & $venvPython $publisher --rabbitmq $Rabbit --queue $Queue --doc-id $DocId
} else {
  python $publisher --rabbitmq $Rabbit --queue $Queue --doc-id $DocId
}
