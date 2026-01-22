# Deploy to Cloud Run via Cloud Shell

You're now in Cloud Shell. Follow these steps:

## Step 1: Upload Your Code

You have two options:

### Option A: Upload via Cloud Shell Editor (Easiest)

1. In the Cloud Shell Editor (left side), click the **folder icon** (Explorer)
2. Right-click in the file explorer → **"Upload..."**
3. Navigate to your local `functions_python` folder and select all files, OR
4. Zip the folder locally first, then upload the zip file

If you uploaded a zip:
```bash
unzip functions_python.zip
```

### Option B: Use gcloud from Local Machine

From your **local PowerShell** (keep Cloud Shell open):

```powershell
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"
gcloud cloud-shell scp --recurse functions_python cloudshell:~/ecg-service/
```

## Step 2: Verify Files Are Uploaded

In Cloud Shell terminal, run:

```bash
cd ~/ecg-service
ls -la
# You should see functions_python folder
cd functions_python
ls -la
# You should see: main.py, Dockerfile, requirements.txt, transformers/, etc.
```

## Step 3: Set Your Project

```bash
gcloud config set project hv-ecg
```

## Step 4: Build the Docker Image

```bash
cd ~/ecg-service/functions_python
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
```

This will take 5-10 minutes. Wait for it to complete.

## Step 5: Deploy to Cloud Run

After the build succeeds, deploy:

```bash
gcloud run deploy ecg-multi-method \
  --image gcr.io/hv-ecg/ecg-multi-method \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300 \
  --max-instances 10
```

## Step 6: Copy the Service URL

After deployment completes, you'll see output like:

```
Service URL: https://ecg-multi-method-XXXXX-uc.a.run.app
```

**COPY THIS URL!** You'll need it for the next step.

## Step 7: Update Firebase Config (On Your Local Machine)

Switch back to your **local PowerShell** and run:

```powershell
firebase functions:config:set python.multi_method_url="PASTE_THE_URL_FROM_STEP_6"
```

## Step 8: Deploy the Cloud Function

```powershell
firebase deploy --only functions:processMultiMethodTransform
```

## Done! 🎉

Now go back to your gallery and click "Process All Methods" - it should work!
