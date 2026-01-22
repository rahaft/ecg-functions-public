# Quick Start Guide

## Setup Virtual Environment (Recommended)

### Option 1: Use PowerShell Script
```powershell
.\setup_venv.ps1
```

### Option 2: Manual Setup
```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r functions_python\requirements.txt
```

## Activate Virtual Environment (for future use)

```powershell
.\activate_venv.ps1
```

Or manually:
```powershell
.\venv\Scripts\Activate.ps1
```

## Once Virtual Environment is Set Up

### 1. Start Live Test Server
```powershell
# Make sure venv is activated first
python scripts/start_live_test.py
```

Then open `http://localhost:5000` in your browser.

### 2. Test Single Image
```powershell
python scripts/run_test.py test path/to/your/ecg_image.jpg
```

### 3. View Results
```powershell
python scripts/run_test.py view
```

## Troubleshooting

### If you get "execution of scripts is disabled"
Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### If dependencies fail to install
Make sure you're using the virtual environment:
```powershell
# Check if activated (you should see (venv) in prompt)
# If not, activate it:
.\venv\Scripts\Activate.ps1
```
