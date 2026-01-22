# Deploy Parallel Processing to Internet

## Quick Deployment Steps

### 1. Update Code (Already Done ✅)
- ✅ Edge detection endpoints added to `main.py`
- ✅ Batch processing endpoint added
- ✅ WebSocket client added to `gallery.html`
- ✅ Requirements updated

### 2. Deploy Python Service to Cloud Run

**In Cloud Shell or local terminal:**

```bash
# Set project
gcloud config set project hv-ecg

# Navigate to functions_python
cd functions_python

# Build Docker image
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

**After deployment, note the service URL:**
```
Service URL: https://ecg-multi-method-XXXXX.run.app
```

### 3. Deploy Updated Hosting

```bash
# Deploy gallery.html with new features
firebase deploy --only hosting
```

### 4. Verify Deployment

**Check health endpoint:**
```bash
curl https://ecg-multi-method-101881880910.us-central1.run.app/health
```

Should return:
```json
{
  "status": "healthy",
  "endpoints": [
    "/transform-multi",
    "/analyze-fit",
    "/detect-edges",
    "/process-batch",
    "/health"
  ]
}
```

**Test edge detection:**
```bash
# Use a test image
curl -X POST https://ecg-multi-method-101881880910.us-central1.run.app/detect-edges \
  -H "Content-Type: application/json" \
  -d '{
    "image": "base64_encoded_image_here",
    "method": "canny"
  }'
```

---

## New Endpoints Available

### 1. `/detect-edges` (POST)
Detect edges in ECG image.

**Request:**
```json
{
  "image": "base64_encoded_image",
  "method": "canny",  // optional: "canny", "sobel", "laplacian", "contour"
  "crop_to_content": false  // optional: crop to content boundaries
}
```

**Response:**
```json
{
  "success": true,
  "bounding_box": {
    "x": 10,
    "y": 20,
    "width": 800,
    "height": 600
  },
  "edge_pixels": 12345,
  "contour_count": 5,
  "method": "canny",
  "cropped_image": "base64_encoded_cropped_image"  // if crop_to_content=true
}
```

### 2. `/process-batch` (POST)
Process up to 10 images in parallel.

**Request:**
```json
{
  "images": ["base64_image1", "base64_image2", ...],
  "options": {
    "edge_detection": true,
    "color_separation": true,
    "grid_detection": true,
    "quality_check": true,
    "crop_to_content": false,
    "color_method": "lab"  // or "hsv"
  }
}
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "results": [
    {
      "index": 0,
      "success": true,
      "steps": {
        "edge_detection": { ... },
        "color_separation": { ... },
        "grid_detection": { ... },
        "quality_check": { ... }
      }
    },
    {
      "index": 1,
      "success": true,
      "steps": { ... }
    }
  ]
}
```

---

## Testing from Browser

### 1. Open Gallery
Go to: `https://hv-ecg.web.app/gallery.html`

### 2. Test Edge Detection
Open browser console and run:
```javascript
// Get first image
const img = document.querySelector('.gallery-item img');
if (img) {
    detectEdges(img, 'canny', true).then(result => {
        console.log('Edge detection result:', result);
    });
}
```

### 3. Test Batch Processing
```javascript
// Get multiple images
const images = Array.from(document.querySelectorAll('.gallery-item img')).slice(0, 5);

processBatch(images, {
    edge_detection: true,
    color_separation: true,
    grid_detection: true
}).then(result => {
    console.log('Batch processing result:', result);
});
```

### 4. Test GCS Batch Processing
```javascript
// Process images from GCS
const imagePaths = [
    'ecg_images/user1/record1/image1.png',
    'ecg_images/user1/record1/image2.png'
];

processGCSBatch(imagePaths, 'your-bucket-name', {
    edge_detection: true,
    color_separation: true
}).then(result => {
    console.log('GCS batch result:', result);
});
```

---

## Deployment Checklist

- [ ] Code updated (✅ Done)
- [ ] Build Docker image
- [ ] Deploy to Cloud Run
- [ ] Verify health endpoint
- [ ] Deploy hosting
- [ ] Test edge detection from browser
- [ ] Test batch processing from browser
- [ ] Test with GCS images

---

## Troubleshooting

### Service not responding
- Check Cloud Run logs: `gcloud run services logs read ecg-multi-method --region us-central1`
- Verify service is running: `gcloud run services list`

### CORS errors
- Cloud Run should handle CORS automatically
- If issues, check service allows unauthenticated access

### Timeout errors
- Increase timeout: `--timeout 600` in deploy command
- Process fewer images per batch (reduce from 10 to 5)

### Memory errors
- Increase memory: `--memory 4Gi` in deploy command
- Process images in smaller batches

---

## Next Steps After Deployment

1. **Test with real ECG images** from GCS
2. **Monitor performance** - check execution times
3. **Optimize** - adjust batch size, memory, timeout as needed
4. **Add UI buttons** in gallery.html for easy access to new features

---

*Deployment Guide - January 21, 2026*
