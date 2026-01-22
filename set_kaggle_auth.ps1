# Set Kaggle API Authentication
# Run this script to set the KAGGLE_USERNAME and KAGGLE_API_TOKEN environment variables

$env:KAGGLE_USERNAME = "raconcilio"
$env:KAGGLE_API_TOKEN = "KGAT_c70783487531b81b83b96755edfcace6"

Write-Host "✓ Kaggle authentication set!" -ForegroundColor Green
Write-Host "  Username: $env:KAGGLE_USERNAME" -ForegroundColor Gray
Write-Host "  API Token: $($env:KAGGLE_API_TOKEN.Substring(0,15))..." -ForegroundColor Gray
Write-Host ""
Write-Host "To verify, run:" -ForegroundColor Yellow
Write-Host "  python test_kaggle_list.py" -ForegroundColor Gray
