# Deploy Python Service to Cloud Run
# This script builds and deploys the Python Flask service with CORS fixes

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploy Python Service to Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if gcloud is installed
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "gcloud CLI: $gcloudVersion" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: gcloud CLI not found!" -ForegroundColor Red
    Write-Host "Install from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Set project
$projectId = "hv-ecg"
Write-Host "Project: $projectId" -ForegroundColor Cyan
gcloud config set project $projectId

# Service configuration
$serviceName = "ecg-multi-method"
$region = "us-central1"
$imageTag = "gcr.io/$projectId/$serviceName"

Write-Host ""
Write-Host "Service: $serviceName" -ForegroundColor Yellow
Write-Host "Region: $region" -ForegroundColor Yellow
Write-Host "Image: $imageTag" -ForegroundColor Yellow
Write-Host ""

# Change to functions_python directory
$originalDir = Get-Location
Set-Location "functions_python"

try {
    # Step 1: Build the container
    Write-Host "Step 1: Building container image..." -ForegroundColor Yellow
    gcloud builds submit --tag $imageTag
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host ""
    
    # Step 2: Deploy to Cloud Run
    Write-Host "Step 2: Deploying to Cloud Run..." -ForegroundColor Yellow
    gcloud run deploy $serviceName `
        --image $imageTag `
        --platform managed `
        --region $region `
        --allow-unauthenticated `
        --memory 2Gi `
        --timeout 300 `
        --max-instances 10 `
        --port 8080
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Deployment failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Deployment Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # Get the service URL
    Write-Host "Getting service URL..." -ForegroundColor Cyan
    $serviceUrl = gcloud run services describe $serviceName --region $region --format="value(status.url)"
    
    Write-Host ""
    Write-Host "Service URL: $serviceUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "Update gallery.html with this URL if needed:" -ForegroundColor Yellow
    Write-Host "  const PYTHON_SERVICE_URL = '$serviceUrl';" -ForegroundColor Cyan
    Write-Host ""
    
} finally {
    Set-Location $originalDir
}
