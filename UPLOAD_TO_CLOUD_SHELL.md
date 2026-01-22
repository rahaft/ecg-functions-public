# How to Upload Files to Cloud Shell

Since you don't see the folder icon, here are alternative methods:

## Method 1: Use the File Menu (Easiest)

1. In Cloud Shell Editor, click **"File"** in the top menu bar
2. Select **"Upload..."** or **"Upload Files..."**
3. Select your `functions_python` folder (or zip it first)

## Method 2: Use gcloud from Your Local Machine (Recommended - Most Reliable)

**IMPORTANT:** This command must be run from your **local PowerShell**, NOT from Cloud Shell!

1. **Close or minimize Cloud Shell** (keep it running in background)
2. Open **PowerShell on your local machine**
3. Run these commands:

```powershell
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"
gcloud cloud-shell scp --recurse functions_python cloudshell:~/ecg-service/
```

This will copy your entire `functions_python` folder to Cloud Shell.

## Method 3: Create a Zip and Upload via File Menu

1. On your local machine, zip the `functions_python` folder:
   - Right-click `functions_python` → "Send to" → "Compressed (zipped) folder"
   - Name it `functions_python.zip`

2. In Cloud Shell Editor:
   - Click **"File"** → **"Upload..."**
   - Select `functions_python.zip`

3. In Cloud Shell terminal, extract it:
```bash
cd ~/ecg-service
unzip functions_python.zip
```

## After Uploading

Verify files are there:
```bash
cd ~/ecg-service
ls -la
cd functions_python
ls -la
```

You should see: `main.py`, `Dockerfile`, `requirements.txt`, `transformers/`, etc.
