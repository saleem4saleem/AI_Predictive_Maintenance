param(
    [string]$BaseUrl = "http://localhost:8000"
)

$Endpoints = @(
    "/api/v1/health",
    "/api/v1/overview",
    "/api/v1/assets",
    "/api/v1/models/active"
)

foreach ($Endpoint in $Endpoints) {
    $Url = "$BaseUrl$Endpoint"
    Write-Host "Checking $Url"
    Invoke-RestMethod -Uri $Url -Method Get | ConvertTo-Json -Depth 8
}
