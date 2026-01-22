# Fix Firebase Storage CORS Configuration
# This script configures CORS for Firebase Storage to allow requests from hv-ecg.web.app

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Firebase Storage CORS Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$bucketName = "hv-ecg.appspot.com"
$corsFile = "firebase-storage-cors.json"

# Check if CORS file exists
if (-not (Test-Path $corsFile)) {
    Write-Host "ERROR: CORS configuration file not found: $corsFile" -ForegroundColor Red
    Write-Host "Please create the file first." -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Checking gsutil installation..." -ForegroundColor Yellow
$gsutilCheck = Get-Command gsutil -ErrorAction SilentlyContinue

if (-not $gsutilCheck) {
    Write-Host "ERROR: gsutil not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Google Cloud SDK:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Cyan
    Write-Host "2. Or install via: winget install Google.CloudSDK" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After installation, run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "OK: gsutil found" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Checking authentication..." -ForegroundColor Yellow
$authCheck = gsutil ls 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Not authenticated with gcloud/gsutil" -ForegroundColor Yellow
    Write-Host "Running: gcloud auth login" -ForegroundColor Cyan
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Authentication failed!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "OK: Authenticated" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Setting CORS configuration..." -ForegroundColor Yellow
Write-Host "Bucket: gs://$bucketName" -ForegroundColor Cyan
Write-Host "CORS File: $corsFile" -ForegroundColor Cyan
Write-Host ""

gsutil cors set $corsFile "gs://$bucketName"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "OK: CORS configuration applied successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Step 4: Verifying CORS configuration..." -ForegroundColor Yellow
    gsutil cors get "gs://$bucketName"
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS: CORS configured!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Refresh the gallery page: https://hv-ecg.web.app/gallery.html" -ForegroundColor Cyan
    Write-Host "2. Images should now load without CORS errors" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to set CORS configuration" -ForegroundColor Red
    Write-Host "Check the error message above." -ForegroundColor Yellow
    exit 1
}
