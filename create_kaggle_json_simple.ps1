# Create kaggle.json file for Kaggle API authentication

$kaggleDir = "$env:USERPROFILE\.kaggle"
$kaggleJson = Join-Path $kaggleDir "kaggle.json"

# Create directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $kaggleDir | Out-Null

# Create kaggle.json with token format
$kaggleConfig = @{
    username = "raconcilio"
    key = "KGAT_c70783487531b81b83b96755edfcace6"
}

# Convert to JSON and write to file (without BOM)
$jsonContent = $kaggleConfig | ConvertTo-Json -Compress
[System.IO.File]::WriteAllText($kaggleJson, $jsonContent, [System.Text.UTF8Encoding]::new($false))

Write-Host "Kaggle credentials file created!" -ForegroundColor Green
Write-Host "Location: $kaggleJson" -ForegroundColor Gray
