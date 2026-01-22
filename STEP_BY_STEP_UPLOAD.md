# Step-by-Step: Upload functions_python to Cloud Shell

## Important: Two Different Terminals

- **Local PowerShell** = Your Windows computer
- **Cloud Shell Terminal** = The browser-based terminal (at bottom of Cloud Shell Editor)

## Step 1: Upload from Local PowerShell

**In your LOCAL PowerShell** (not Cloud Shell), run:

```powershell
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"
gcloud cloud-shell scp --recurse functions_python cloudshell:~/ecg-service/
```

This will copy your entire `functions_python` folder to Cloud Shell. It may take a few minutes.

## Step 2: Verify in Cloud Shell

**Switch to Cloud Shell** (in your browser), and in the **Cloud Shell terminal** (bottom panel), run:

```bash
cd ~/ecg-service
ls -la
```

You should see the `functions_python` folder listed.

## Step 3: Check Contents

```bash
cd functions_python
ls -la
```

You should see: `main.py`, `Dockerfile`, `requirements.txt`, `transformers/`, etc.

## If the Upload Didn't Work

If `gcloud cloud-shell scp` doesn't work, try creating a zip file first:

### On Local Machine (PowerShell):

```powershell
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"
Compress-Archive -Path functions_python -DestinationPath functions_python.zip -Force
gcloud cloud-shell scp functions_python.zip cloudshell:~/ecg-service/
```

### Then in Cloud Shell Terminal:

```bash
cd ~/ecg-service
unzip functions_python.zip
```

## Next Steps After Upload

Once files are uploaded, continue with build and deploy:

```bash
cd ~/ecg-service/functions_python
gcloud config set project hv-ecg
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
```
