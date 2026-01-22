# PowerShell Script to Deploy Parallel Processing System
# Run this script to deploy all new features to the internet

Write-Host "🚀 Deploying Parallel Processing System to Internet..." -ForegroundColor Green
Write-Host ""

# Step 1: Build and Deploy Python Service
Write-Host "Step 1: Building Docker image..." -ForegroundColor Yellow
gcloud config set project hv-ecg
cd functions_python
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build successful!" -ForegroundColor Green
Write-Host ""

# Step 2: Deploy to Cloud Run
Write-Host "Step 2: Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy ecg-multi-method --image gcr.io/hv-ecg/ecg-multi-method --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi --timeout 300 --max-instances 10

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Deployment successful!" -ForegroundColor Green
Write-Host ""

# Step 3: Get service URL
Write-Host "Step 3: Getting service URL..." -ForegroundColor Yellow
$serviceUrl = gcloud run services describe ecg-multi-method --region us-central1 --format="value(status.url)"
Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
Write-Host ""

# Step 4: Test health endpoint
Write-Host "Step 4: Testing health endpoint..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "$serviceUrl/health" -Method Get
    Write-Host "✅ Health check passed!" -ForegroundColor Green
    Write-Host "Endpoints available:" -ForegroundColor Cyan
    $healthResponse.endpoints | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
} catch {
    Write-Host "⚠️  Health check failed: $_" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Deploy Hosting
Write-Host "Step 5: Deploying hosting..." -ForegroundColor Yellow
cd ..
firebase deploy --only hosting

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Hosting deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Hosting deployment successful!" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
Write-Host "Gallery URL: https://hv-ecg.web.app/gallery.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "New endpoints available:" -ForegroundColor Yellow
Write-Host "  - POST $serviceUrl/detect-edges" -ForegroundColor Gray
Write-Host "  - POST $serviceUrl/process-batch" -ForegroundColor Gray
Write-Host ""
Write-Host "Test from browser console:" -ForegroundColor Yellow
Write-Host "  detectEdges(img, 'canny', true)" -ForegroundColor Gray
Write-Host "  processBatch([img1, img2, ...], options)" -ForegroundColor Gray
