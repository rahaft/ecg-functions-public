# Bulk Testing Guide - Frontend

## How to Use Bulk Testing

### Quick Start

**In browser console (F12) on gallery.html:**

```javascript
// Quick bulk test with all options enabled
quickBulkTest();
```

This will:
- Find all loaded images in the gallery
- Process up to 10 images in parallel
- Test edge detection, color separation, grid detection, and quality checks
- Show summary in console

### Custom Bulk Test

```javascript
// Test specific options
bulkTestGallery({
    edge_detection: true,
    color_separation: true,
    grid_detection: false,
    quality_check: true,
    crop_to_content: true,
    color_method: 'hsv'  // or 'lab'
});
```

### Wait for Images to Load

If you see "No valid images found", wait a few seconds for images to load, then try:

```javascript
// Wait for images, then test
setTimeout(() => {
    quickBulkTest();
}, 3000);  // Wait 3 seconds
```

---

## What Gets Tested

When you run bulk testing, it processes each image through:

1. **Edge Detection** - Finds image boundaries
2. **Color Separation** - Separates ECG traces from grid
3. **Grid Detection** - Detects grid lines
4. **Quality Checks** - Validates image quality

---

## Console Output

After running `quickBulkTest()`, you'll see:

```
🧪 Starting bulk test on gallery images...
📸 Found 20 images
🔄 Processing 10 images...
✅ Bulk test completed in 12.34s
Results: {success: true, count: 10, results: [...]}
📊 Summary: 10 successful, 0 failed out of 10 total
✅ Image 0: {edge_detection: '✓', color_separation: '✓', grid_detection: '✓', quality_check: '✓'}
✅ Image 1: {edge_detection: '✓', color_separation: '✓', grid_detection: '✓', quality_check: '✓'}
...
```

---

## Troubleshooting

### "No valid images found"
- Images might still be loading
- Wait a few seconds and try again
- Check that images are visible in the gallery

### CORS errors
- Run: `firebase deploy --only hosting` after CORS fix is deployed
- Check service is accessible

### Images not loading
- Check browser console for errors
- Verify Firebase Storage permissions
- Refresh the page

---

## After CORS Fix is Deployed

Once you redeploy the Python service with CORS support:

1. **Rebuild and redeploy:**
   ```powershell
   cd functions_python
   gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
   gcloud run deploy ecg-multi-method --image gcr.io/hv-ecg/ecg-multi-method --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi --timeout 300 --max-instances 10
   ```

2. **Then test:**
   ```javascript
   quickBulkTest();
   ```

---

*Bulk Testing Guide - January 21, 2026*
