# Deploy Python Service - Step by Step

## Prerequisites Check

1. **Authenticate with Google Cloud:**
   ```powershell
   gcloud auth login
   ```

2. **Set the project:**
   ```powershell
   gcloud config set project hv-ecg
   ```

3. **Enable required APIs:**
   ```powershell
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

## Deployment Steps

### Step 1: Navigate to Python Service Directory

```powershell
cd functions_python
```

### Step 2: Build Docker Image

```powershell
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
```

This will:
- Build the Docker image from the Dockerfile
- Push it to Google Container Registry
- Take 5-10 minutes

### Step 3: Deploy to Cloud Run

**Single line (recommended for PowerShell):**
```powershell
gcloud run deploy ecg-multi-method --image gcr.io/hv-ecg/ecg-multi-method --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi --timeout 300 --max-instances 10
```

**Or multi-line with backticks:**
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

**Important:** After deployment, you'll see output like:
```
Service URL: https://ecg-multi-method-XXXXX-uc.a.run.app
```
**Copy this URL!**

### Step 4: Set Firebase Config

```powershell
cd ..
firebase functions:config:set python.multi_method_url="YOUR_SERVICE_URL_HERE"
```

Replace `YOUR_SERVICE_URL_HERE` with the URL from Step 3.

### Step 5: Deploy Cloud Function

```powershell
firebase deploy --only functions:processMultiMethodTransform
```

## Verify It Works

1. Test health endpoint:
   ```powershell
   curl https://ecg-multi-method-XXXXX-uc.a.run.app/health
   ```

2. Open gallery and try "Process All Methods"

## Troubleshooting

### "Reauthentication failed"
```powershell
gcloud auth login
```

### "Project not found"
```powershell
gcloud config set project hv-ecg
```

### "API not enabled"
```powershell
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

### PowerShell line continuation errors
- Use single-line commands, OR
- Use backticks (`` ` ``) not backslashes (`\`)
- No spaces after backtick
