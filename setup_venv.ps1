# PowerShell script to set up virtual environment and install dependencies

Write-Host "Setting up virtual environment..." -ForegroundColor Green

# Create virtual environment
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Green
pip install -r functions_python\requirements.txt

Write-Host "`nSetup complete! To activate the virtual environment in the future, run:" -ForegroundColor Green
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
