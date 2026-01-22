# Deployment Guide

This guide covers deploying both the Node.js Cloud Functions and the Python digitization pipeline.

## Node.js Cloud Functions

The main Cloud Functions are in the `functions/` directory and handle:
- Storage triggers for automatic processing
- HTTP callable functions for manual processing
- Submission file generation

### Deploy Node.js Functions

```bash
cd functions
npm install
cd ..
firebase deploy --only functions
```

## Python Digitization Pipeline

The Python pipeline can be deployed in several ways:

### Option 1: Cloud Run (Recommended)

1. Build and deploy as a Cloud Run service:

```bash
cd functions_python
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ecg-digitization
gcloud run deploy ecg-digitization \
  --image gcr.io/YOUR_PROJECT_ID/ecg-digitization \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

2. Update the Node.js function to call the Cloud Run URL:
   - Set environment variable: `PYTHON_DIGITIZATION_URL`
   - Or update `functions/index.js` to use the Cloud Run endpoint

### Option 2: Python Cloud Functions (Gen 2)

1. Deploy as a Python Cloud Function:

```bash
cd functions_python
gcloud functions deploy processECGImagePython \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=process_ecg_image \
  --trigger-http \
  --allow-unauthenticated
```

2. Update Node.js function to call the Python function URL.

### Option 3: Local Processing (Development)

For local development, you can run the Python pipeline directly:

```bash
cd functions_python
pip install -r requirements.txt
python digitization_pipeline.py
```

## Environment Variables

Set these in Firebase Functions:

```bash
firebase functions:config:set python.digitization_url="YOUR_CLOUD_RUN_URL"
```

Or use environment variables in Node.js:

```javascript
const pythonFunctionUrl = process.env.PYTHON_DIGITIZATION_URL;
```

## Testing

### Test Node.js Functions Locally

```bash
cd functions
npm run serve
```

### Test Python Pipeline Locally

```bash
cd functions_python
python -m pytest tests/  # If you have tests
python digitization_pipeline.py  # Test with sample image
```

## Monitoring

- View logs: `firebase functions:log`
- Monitor in Firebase Console: Functions tab
- Check Cloud Run logs: `gcloud run services logs read ecg-digitization`

## Troubleshooting

### Functions not triggering
- Check Storage rules allow uploads
- Verify function deployment succeeded
- Check function logs for errors

### Python processing fails
- Verify all dependencies in requirements.txt
- Check image format compatibility
- Review error logs in Cloud Run/Function logs

### Memory/Timeout issues
- Increase function memory: `--memory 2Gi`
- Increase timeout: `--timeout 540s`
- Optimize image processing pipeline
