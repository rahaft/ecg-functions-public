# Quick Deploy Guide - Get "Process All Methods" Working

## Prerequisites

- Google Cloud SDK installed (`gcloud`)
- Firebase CLI installed (`firebase`)
- Project: `hv-ecg`
- Region: `us-central1`

## Step-by-Step Deployment

### 1. Create Dockerfile (Already Created ✅)

The `functions_python/Dockerfile` has been created.

### 2. Build and Deploy Python Service

```bash
# Navigate to Python service directory
cd functions_python

# Build the container image
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method

# Deploy to Cloud Run
gcloud run deploy ecg-multi-method \
  --image gcr.io/hv-ecg/ecg-multi-method \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300 \
  --max-instances 10
```

**Important:** After deployment, copy the service URL (looks like `https://ecg-multi-method-XXXXX.run.app`)

### 3. Update Cloud Function with Service URL

Edit `functions/index.js` and replace `XXXXX` with your actual service URL, or set it as an environment variable:

**Option A: Set environment variable**
```bash
firebase functions:config:set python.multi_method_url="https://ecg-multi-method-XXXXX.run.app"
```

**Option B: Edit directly in code**
The code now checks `process.env.PYTHON_MULTI_METHOD_URL` first, then falls back to Firebase config.

### 4. Deploy Cloud Function

```bash
cd ..  # Back to project root
firebase deploy --only functions:processMultiMethodTransform
```

### 5. Test

1. Open gallery: `https://hv-ecg.web.app/gallery.html`
2. Click on an image
3. Click "🔄 Transform Image" button
4. Click "🔄 Process All Methods"
5. You should see results from all methods!

## Verify Deployment

### Check Python Service
```bash
# Check service is running
gcloud run services list --region us-central1

# Test health endpoint
curl https://ecg-multi-method-XXXXX.run.app/health
```

### Check Cloud Function
```bash
# View function logs
firebase functions:log --only processMultiMethodTransform
```

## Troubleshooting

### Service Not Responding
```bash
# Check Cloud Run logs
gcloud run services logs read ecg-multi-method --region us-central1 --limit 50
```

### Import Errors
- Make sure all dependencies are in `requirements.txt`
- Check that `transformers/` directory is copied correctly

### Timeout Errors
- Increase timeout: `--timeout 600` in Cloud Run deploy
- Check Cloud Function timeout in `index.js` (currently 300s)

### CORS Issues
- Cloud Run service should allow unauthenticated access (`--allow-unauthenticated`)
- Cloud Function handles CORS automatically

## Current Implementation Status

✅ **Ready to Deploy:**
- Flask endpoint `/transform-multi`
- Barrel transformer (fully working)
- Multi-method processor structure
- Dockerfile created

🚧 **Partial:**
- Polynomial transformer (structure ready, needs warp implementation)

⏳ **Future:**
- TPS transformer
- Perspective transformer

## What Works Now

After deployment, "Process All Methods" will:
1. ✅ Process with Barrel distortion (fully working)
2. 🚧 Process with Polynomial (will run but may have limited results)
3. ⏳ TPS and Perspective will show as "not implemented"

The system will automatically select the best available method based on quality scores.
