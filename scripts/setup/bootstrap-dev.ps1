python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r api/requirements.txt
Copy-Item .env.development.example -Destination .env -ErrorAction SilentlyContinue
Write-Host "[setup] Development environment bootstrapped."
