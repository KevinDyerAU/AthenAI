param(
  [string]$EnvFile = ".env.production.example"
)
python scripts/config/validate_env.py --env-file $EnvFile --environment production
