# Set Google Cloud Storage Authentication
# Run this script to set the GOOGLE_APPLICATION_CREDENTIALS environment variable

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$keyFile = Join-Path $scriptDir "service-account-key.json"

if (Test-Path $keyFile) {
    $env:GOOGLE_APPLICATION_CREDENTIALS = $keyFile
    Write-Host "✓ Google Cloud authentication set!" -ForegroundColor Green
    Write-Host "  Credentials file: $keyFile" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To verify, run:" -ForegroundColor Yellow
    Write-Host "  python -c `"from google.cloud import storage; client = storage.Client(project='hv-ecg'); print('✓ Authentication successful!')`"" -ForegroundColor Gray
} else {
    Write-Host "✗ Error: service-account-key.json not found!" -ForegroundColor Red
    Write-Host "  Expected location: $keyFile" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Make sure the service account key file is in the project root directory." -ForegroundColor Yellow
    exit 1
}
