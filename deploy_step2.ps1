# Step 2: Deploy to Cloud Run
# Run this after the Docker build completes

Write-Host "🚀 Step 2: Deploying to Cloud Run..." -ForegroundColor Green
Write-Host ""

gcloud run deploy ecg-multi-method --image gcr.io/hv-ecg/ecg-multi-method --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi --timeout 300 --max-instances 10

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Getting service URL..." -ForegroundColor Yellow
    $serviceUrl = gcloud run services describe ecg-multi-method --region us-central1 --format="value(status.url)"
    Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next step: Deploy hosting with: firebase deploy --only hosting" -ForegroundColor Yellow
} else {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
}
