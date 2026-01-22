# Authenticate and Deploy Script
# This script authenticates first, then deploys

Write-Host "🔐 Step 0: Authenticating with Google Cloud..." -ForegroundColor Yellow
Write-Host "This will open a browser window for you to sign in." -ForegroundColor Cyan
Write-Host ""

# Authenticate (opens browser)
gcloud auth login

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Authentication failed!" -ForegroundColor Red
    Write-Host "Please run: gcloud auth login" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Authentication successful!" -ForegroundColor Green
Write-Host ""

# Set project
Write-Host "Setting project to hv-ecg..." -ForegroundColor Yellow
gcloud config set project hv-ecg

Write-Host ""
Write-Host "🚀 Starting deployment..." -ForegroundColor Green
Write-Host ""

# Now run the deployment
& "$PSScriptRoot\deploy_now.ps1"
