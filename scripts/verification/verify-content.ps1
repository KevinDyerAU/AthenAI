param(
  [ValidateSet('basic','strict')][string]$Level = 'basic'
)
python scripts/verification/verify_content.py --level $Level
