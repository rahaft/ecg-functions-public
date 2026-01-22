# Install GCS authentication to PowerShell profile
# This will automatically set GOOGLE_APPLICATION_CREDENTIALS every time you open PowerShell

Write-Host "Installing Google Cloud Storage authentication to PowerShell profile..." -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$keyFile = Join-Path $scriptDir "service-account-key.json"

# Check if key file exists
if (-not (Test-Path $keyFile)) {
    Write-Host "✗ Error: service-account-key.json not found!" -ForegroundColor Red
    Write-Host "  Expected location: $keyFile" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Make sure the service account key file is in the project root directory first." -ForegroundColor Yellow
    exit 1
}

# Check if PowerShell profile exists
$profilePath = $PROFILE.CurrentUserAllHosts
$profileDir = Split-Path -Parent $profilePath

# Create profile directory if it doesn't exist
if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    Write-Host "✓ Created PowerShell profile directory: $profileDir" -ForegroundColor Green
}

# Create or update profile
$profileLine = "`$env:GOOGLE_APPLICATION_CREDENTIALS = `"$keyFile`"  # GCS Authentication - Added by install_gcs_auth_profile.ps1"

# Check if already added
$profileContent = ""
if (Test-Path $profilePath) {
    $profileContent = Get-Content $profilePath -Raw
}

if ($profileContent -match [regex]::Escape($keyFile)) {
    Write-Host "⚠ Authentication already added to PowerShell profile" -ForegroundColor Yellow
    Write-Host "  Profile location: $profilePath" -ForegroundColor Gray
} else {
    # Add to profile
    Add-Content -Path $profilePath -Value "`n$profileLine"
    Write-Host "✓ Added Google Cloud authentication to PowerShell profile!" -ForegroundColor Green
    Write-Host "  Profile location: $profilePath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "The environment variable will be set automatically every time you open PowerShell." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To apply immediately, run:" -ForegroundColor Yellow
    Write-Host "  . `$PROFILE" -ForegroundColor Gray
}

Write-Host ""
Write-Host "To verify authentication, run:" -ForegroundColor Yellow
Write-Host "  python -c `"from google.cloud import storage; client = storage.Client(project='hv-ecg'); print('✓ Authentication successful!')`"" -ForegroundColor Gray
