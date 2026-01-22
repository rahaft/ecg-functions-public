# Deploy Python Service - PowerShell Commands

## PowerShell-Compatible Deployment Commands

PowerShell uses backticks (`` ` ``) for line continuation, not backslashes (`\`).

### Step 1: Build Docker Image

```powershell
cd functions_python
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
```

### Step 2: Deploy to Cloud Run (Single Line)

```powershell
gcloud run deploy ecg-multi-method --image gcr.io/hv-ecg/ecg-multi-method --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi --timeout 300 --max-instances 10
```

### Step 2 Alternative: Multi-Line with Backticks

```powershell
gcloud run deploy ecg-multi-method `
  --image gcr.io/hv-ecg/ecg-multi-method `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 2Gi `
  --timeout 300 `
  --max-instances 10
```

**Important:** Use backticks (`` ` ``), not backslashes (`\`), and make sure there are no spaces after the backtick.

### Step 3: Get Service URL

After deployment, you'll see output like:
```
Service URL: https://ecg-multi-method-XXXXX-uc.a.run.app
```

Copy this URL.

### Step 4: Set Firebase Config

```powershell
firebase functions:config:set python.multi_method_url="YOUR_SERVICE_URL_HERE"
```

Replace `YOUR_SERVICE_URL_HERE` with the URL from Step 3.

### Step 5: Deploy Cloud Function

```powershell
cd ..
firebase deploy --only functions:processMultiMethodTransform
```

## Quick Copy-Paste (All Steps)

```powershell
# Step 1: Build
cd functions_python
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method

# Step 2: Deploy (single line)
gcloud run deploy ecg-multi-method --image gcr.io/hv-ecg/ecg-multi-method --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi --timeout 300 --max-instances 10

# Step 3: Copy the Service URL from the output, then:
cd ..
firebase functions:config:set python.multi_method_url="https://ecg-multi-method-XXXXX-uc.a.run.app"

# Step 4: Deploy function
firebase deploy --only functions:processMultiMethodTransform
```

## Verify Deployment

```powershell
# Check service is running
gcloud run services list --region us-central1

# Test health endpoint (replace with your URL)
curl https://ecg-multi-method-XXXXX-uc.a.run.app/health
```

## Troubleshooting

### "Missing expression after unary operator '--'"
- You're using backslashes (`\`) instead of backticks (`` ` ``)
- Use single-line command or backticks for continuation

### "Command not found: gcloud"
- Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install

### "Permission denied"
- Run: `gcloud auth login`
- Run: `gcloud config set project hv-ecg`
