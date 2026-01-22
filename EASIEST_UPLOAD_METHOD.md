# Easiest Method: Zip and Upload via File Menu

## Step 1: Create Zip File (Local PowerShell)

In your **local PowerShell**, run:

```powershell
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"
Compress-Archive -Path functions_python -DestinationPath functions_python.zip -Force
```

This creates `functions_python.zip` in your project folder.

## Step 2: Upload via Cloud Shell Editor

1. **In Cloud Shell Editor** (your browser):
   - Click **"File"** in the top menu bar
   - Select **"Upload..."** or **"Upload Files..."**
   - Navigate to: `C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg`
   - Select `functions_python.zip`
   - Click "Open"

2. Wait for upload to complete (you'll see progress)

## Step 3: Extract in Cloud Shell Terminal

**In the Cloud Shell terminal** (bottom panel of Cloud Shell Editor), run:

```bash
cd ~/ecg-service
ls -la
```

You should see `functions_python.zip`. Then extract it:

```bash
unzip functions_python.zip
```

## Step 4: Verify

```bash
cd functions_python
ls -la
```

You should see: `main.py`, `Dockerfile`, `requirements.txt`, `transformers/`, etc.

## Step 5: Build and Deploy

```bash
gcloud config set project hv-ecg
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
```

This will take 5-10 minutes.
