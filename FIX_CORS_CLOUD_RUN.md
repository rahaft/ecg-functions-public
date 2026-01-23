# Fix CORS for Cloud Run Service

## Issue
The Cloud Run service `ecg-multi-method` is blocking requests from `https://hv-ecg.web.app` due to CORS policy.

## Solution

The CORS configuration has been updated in `functions_python/main.py`. You need to **redeploy the Cloud Run service** for the changes to take effect.

## Deploy Steps

1. **Build and deploy the updated service:**

```powershell
cd functions_python
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
gcloud run deploy ecg-multi-method --image gcr.io/hv-ecg/ecg-multi-method --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi --timeout 300 --max-instances 10
```

2. **Verify CORS is working:**

After deployment, test the endpoint:
```powershell
curl -X OPTIONS https://ecg-multi-method-101881880910.us-central1.run.app/process-gcs-batch -H "Origin: https://hv-ecg.web.app" -v
```

You should see `Access-Control-Allow-Origin: *` in the response headers.

## Changes Made

1. ✅ Updated CORS configuration to use wildcard origins
2. ✅ Improved OPTIONS preflight handler
3. ✅ Added CORS headers to all error responses
4. ✅ Updated Dockerfile to run app directly

## Testing

After redeployment, try processing a group in the gallery. The CORS error should be resolved.
