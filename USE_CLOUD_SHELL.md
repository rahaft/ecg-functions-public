# Use Google Cloud Shell (Easiest Solution)

Windows file locking is causing issues. Use Google Cloud Shell instead - it runs in your browser and avoids all Windows issues.

## Step 1: Open Cloud Shell

1. Go to: https://console.cloud.google.com/cloudshell
2. Click "Open Cloud Shell" (top right)
3. Wait for it to initialize

## Step 2: Upload Your Code

In Cloud Shell, run:

```bash
# Create a directory
mkdir -p ~/ecg-service
cd ~/ecg-service
```

Then upload your `functions_python` folder:
- Click the **three dots menu** (top right of Cloud Shell)
- Select **"Upload file"**
- Upload your entire `functions_python` folder (or zip it first and upload the zip)

OR use gcloud to copy from your local machine:

```bash
# From your local PowerShell, run:
gcloud cloud-shell scp local-functions_python/* cloudshell:~/ecg-service/
```

## Step 3: Build and Deploy (in Cloud Shell)

```bash
cd ~/ecg-service/functions_python

# Build
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method

# Deploy
gcloud run deploy ecg-multi-method \
  --image gcr.io/hv-ecg/ecg-multi-method \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300 \
  --max-instances 10
```

## Step 4: Copy the Service URL

After deployment, you'll see:
```
Service URL: https://ecg-multi-method-XXXXX-uc.a.run.app
```

**Copy this URL!**

## Step 5: Set Firebase Config (Back on Your Local Machine)

In your local PowerShell:

```powershell
firebase functions:config:set python.multi_method_url="YOUR_SERVICE_URL_FROM_STEP_4"
```

## Step 6: Deploy Function

```powershell
firebase deploy --only functions:processMultiMethodTransform
```

## Done!

Now "Process All Methods" should work!
