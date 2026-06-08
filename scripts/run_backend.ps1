param(
    [int]$Port = 8000
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $ProjectRoot "backend")

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $Port
