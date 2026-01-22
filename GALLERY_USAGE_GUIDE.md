# Gallery Page Usage Guide

## How to Use the Gallery Page

**URL:** `https://hv-ecg.web.app/gallery.html`

---

## Quick Start

### 1. View Images
- Images are automatically loaded when you sign in
- Images are grouped by prefix (e.g., `1006427285-0001.png`, `1006427285-0002.png` are in the same group)
- Click on any image to view it larger

### 2. Copy Version Info
- Scroll to the bottom footer
- **Click anywhere on the version line** OR click the **"📋 Copy"** button
- Version info is copied to clipboard as: `Version: 2.3.3 | Build: 2026.01.21.2235 | Deployed: 1/21/2026, 10:35:00 PM | Firebase SDK: 10.7.1`

---

## Bulk Testing Functions

### Quick Bulk Test

**In browser console (F12):**

```javascript
// Test all images with default options
quickBulkTest();
```

This will:
- Find all loaded images in gallery
- Process up to 10 images in parallel
- Test: edge detection, color separation, grid detection, quality checks
- Show results in console

### Custom Bulk Test

```javascript
// Test with specific options
bulkTestGallery({
    edge_detection: true,
    color_separation: true,
    grid_detection: false,
    quality_check: true,
    crop_to_content: true,
    color_method: 'hsv'  // or 'lab'
});
```

### Wait for Images to Load First

If you see "No valid images found", wait a few seconds:

```javascript
// Wait 3 seconds for images to load, then test
setTimeout(() => {
    quickBulkTest();
}, 3000);
```

---

## Individual Image Processing

### Edge Detection

```javascript
// Get an image element
const img = document.querySelector('.gallery-item img');

// Detect edges
detectEdges(img, 'canny', true).then(result => {
    console.log('Edge detection:', result);
    // Returns: bounding_box, edge_pixels, contour_count
});
```

### Process Single Image

```javascript
const img = document.querySelector('.gallery-item img');

// Process with all options
processBatch([img], {
    edge_detection: true,
    color_separation: true,
    grid_detection: true,
    quality_check: true
}).then(result => {
    console.log('Processing result:', result);
});
```

---

## Batch Processing

### Process Multiple Images

```javascript
// Get up to 10 images
const images = Array.from(document.querySelectorAll('.gallery-item img')).slice(0, 10);

// Process in parallel
processBatch(images, {
    edge_detection: true,
    color_separation: true,
    grid_detection: true,
    quality_check: true
}).then(result => {
    console.log(`Processed ${result.count} images`);
    console.log('Results:', result.results);
});
```

### Process GCS Images

```javascript
// Process images directly from Google Cloud Storage
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

## Understanding Results

### Edge Detection Result
```javascript
{
    success: true,
    bounding_box: {x: 10, y: 20, width: 800, height: 600},
    edge_pixels: 12345,
    contour_count: 5,
    method: 'canny'
}
```

### Batch Processing Result
```javascript
{
    success: true,
    count: 10,
    results: [
        {
            index: 0,
            success: true,
            steps: {
                edge_detection: {...},
                color_separation: {...},
                grid_detection: {...},
                quality_check: {...}
            }
        },
        // ... more results
    ]
}
```

---

## Common Tasks

### 1. Test All Images in Gallery
```javascript
quickBulkTest();
```

### 2. Test Specific Number of Images
```javascript
const images = Array.from(document.querySelectorAll('.gallery-item img')).slice(0, 5);
processBatch(images, {
    edge_detection: true,
    color_separation: true
});
```

### 3. Test Only Edge Detection
```javascript
bulkTestGallery({
    edge_detection: true,
    color_separation: false,
    grid_detection: false,
    quality_check: false
});
```

### 4. Copy Version Info
- Click on the version footer line, OR
- Click the "📋 Copy" button
- Version info is copied to clipboard

---

## Troubleshooting

### "quickBulkTest is not defined"
- **Solution:** Deploy hosting: `firebase deploy --only hosting`
- The function is in the code but needs to be deployed

### "No valid images found"
- **Solution:** Wait a few seconds for images to load
- Check that images are visible in the gallery
- Try: `setTimeout(() => quickBulkTest(), 3000);`

### CORS Errors
- **Solution:** Deploy Python service with CORS fix:
  ```powershell
  cd functions_python
  gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
  gcloud run deploy ecg-multi-method --image gcr.io/hv-ecg/ecg-multi-method --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi --timeout 300 --max-instances 10
  ```

### Images Not Loading
- Check browser console for errors
- Verify Firebase Storage permissions
- Refresh the page

---

## Available Functions

| Function | Description |
|----------|-------------|
| `quickBulkTest()` | Quick test all images with default options |
| `bulkTestGallery(options)` | Custom bulk test with options |
| `detectEdges(img, method, crop)` | Detect edges in single image |
| `processBatch(images, options)` | Process multiple images |
| `processGCSBatch(paths, bucket, options)` | Process GCS images |
| `copyVersionInfo()` | Copy version info to clipboard |

---

## Example Workflow

1. **Open gallery:** `https://hv-ecg.web.app/gallery.html`
2. **Wait for images to load** (see "Loaded X images" in console)
3. **Open console** (F12)
4. **Run bulk test:**
   ```javascript
   quickBulkTest();
   ```
5. **View results** in console
6. **Copy version info** by clicking footer or copy button

---

*Gallery Usage Guide - January 21, 2026*
