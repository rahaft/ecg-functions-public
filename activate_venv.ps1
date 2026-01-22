# Quick activation script for virtual environment

if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated! You can now run the pipeline." -ForegroundColor Green
} else {
    Write-Host "Virtual environment not found. Run setup_venv.ps1 first." -ForegroundColor Red
}
