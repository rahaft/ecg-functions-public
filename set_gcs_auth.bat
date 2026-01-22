@echo off
REM Set Google Cloud Storage Authentication
REM Run this script to set the GOOGLE_APPLICATION_CREDENTIALS environment variable

set SCRIPT_DIR=%~dp0
set KEY_FILE=%SCRIPT_DIR%service-account-key.json

if exist "%KEY_FILE%" (
    set GOOGLE_APPLICATION_CREDENTIALS=%KEY_FILE%
    echo ✓ Google Cloud authentication set!
    echo   Credentials file: %KEY_FILE%
    echo.
    echo To verify, run:
    echo   python -c "from google.cloud import storage; client = storage.Client(project='hv-ecg'); print('✓ Authentication successful!')"
) else (
    echo ✗ Error: service-account-key.json not found!
    echo   Expected location: %KEY_FILE%
    echo.
    echo Make sure the service account key file is in the project root directory.
    exit /b 1
)
