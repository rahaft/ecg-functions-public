# Deploy Python Service for "Process All Methods"

This guide will help you deploy the Python multi-method transformation service to Cloud Run so that "Process All Methods" works fully.

## Quick Start (5 Steps)

### Step 1: Create Dockerfile

Create `functions_python/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run Flask app
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]
```

### Step 2: Update main.py to Run Flask

Add this to the end of `functions_python/main.py`:

```python
if __name__ == '__main__':
    if FLASK_AVAILABLE:
        app.run(host='0.0.0.0', port=8080, debug=False)
```

### Step 3: Build and Deploy to Cloud Run

```bash
cd functions_python

# Build the container
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

After deployment, note the service URL (e.g., `https://ecg-multi-method-XXXXX.run.app`)

### Step 4: Update Cloud Function

Edit `functions/index.js` and uncomment/update the Python service call:

```javascript
const pythonServiceUrl = process.env.PYTHON_MULTI_METHOD_URL || 
                         'https://ecg-multi-method-XXXXX.run.app'; // Replace with your URL

if (!pythonServiceUrl || pythonServiceUrl.includes('XXXXX')) {
  throw new functions.https.HttpsError('failed-precondition', 
    'Python multi-method service URL not configured.');
}

const response = await axios.post(pythonServiceUrl + '/transform-multi', {
  image: imageBuffer.toString('base64'),
  width: imageWidth,
  height: imageHeight
}, {
  headers: { 'Content-Type': 'application/json' },
  timeout: 240000 // 4 minutes
});

return response.data;
```

### Step 5: Deploy Cloud Function

```bash
firebase deploy --only functions:processMultiMethodTransform
```

## Testing

1. Open the gallery and select an image
2. Click "🔄 Transform Image" button
3. Click "🔄 Process All Methods"
4. You should see results from all methods!

## Troubleshooting

### "Service not responding"
- Check Cloud Run service is running: `gcloud run services list`
- Check logs: `gcloud run services logs read ecg-multi-method`

### "Import errors"
- Make sure all dependencies are in `requirements.txt`
- Check that transformers module is properly structured

### "Timeout errors"
- Increase Cloud Run timeout: `--timeout 600`
- Increase Cloud Function timeout in `index.js`

## Current Status

✅ **Working:**
- Flask endpoint `/transform-multi` exists
- Barrel transformer implemented
- Multi-method processor structure ready

🚧 **Partial:**
- Polynomial transformer (needs warp implementation)

⏳ **Not Implemented:**
- TPS transformer
- Perspective transformer

## Next Steps

1. Complete polynomial transformer warp implementation
2. Implement TPS transformer
3. Implement perspective transformer
4. Enhance quality scoring metrics
