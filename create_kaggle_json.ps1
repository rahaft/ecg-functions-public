# Create kaggle.json file for Kaggle API authentication
# This uses the new API token format

$kaggleDir = "$env:USERPROFILE\.kaggle"
$kaggleJson = Join-Path $kaggleDir "kaggle.json"

# Create directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $kaggleDir | Out-Null

# Create kaggle.json with token format
$kaggleConfig = @{
    username = "raconcilio"
    key = "KGAT_c70783487531b81b83b96755edfcace6"
} | ConvertTo-Json

# Write to file
$kaggleConfig | Out-File -FilePath $kaggleJson -Encoding utf8 -NoNewline

Write-Host "✓ Kaggle credentials file created!" -ForegroundColor Green
Write-Host "  Location: $kaggleJson" -ForegroundColor Gray
Write-Host ""
Write-Host "To verify, run:" -ForegroundColor Yellow
Write-Host "  python test_kaggle_list.py" -ForegroundColor Gray
