# Deploy to Live - Firebase Deployment Script
# This script deploys the Firebase hosting, Firestore rules, and indexes

Write-Host "Starting Firebase deployment..." -ForegroundColor Cyan

# Check if firebase CLI is installed
try {
    $firebaseVersion = firebase --version
    Write-Host "Firebase CLI found: $firebaseVersion" -ForegroundColor Green
} catch {
    Write-Host "Firebase CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   npm install -g firebase-tools" -ForegroundColor Yellow
    exit 1
}

# Check if user is logged in
Write-Host ""
Write-Host "Checking Firebase login status..." -ForegroundColor Cyan
$loginCheck = firebase projects:list 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in to Firebase. Please run: firebase login" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Deploying Firestore indexes..." -ForegroundColor Cyan
firebase deploy --only firestore:indexes
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to deploy Firestore indexes" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Deploying Firestore rules..." -ForegroundColor Cyan
firebase deploy --only firestore:rules
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to deploy Firestore rules" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Deploying hosting..." -ForegroundColor Cyan
firebase deploy --only hosting
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to deploy hosting" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Site URL: https://hv-ecg.web.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Firestore indexes may take 1-2 minutes to build." -ForegroundColor Yellow
