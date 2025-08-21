param(
  [string]$EnvFile = ".env.development.example"
)
python scripts/config/validate_env.py --env-file $EnvFile --environment development
