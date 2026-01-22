# Quick Gallery Guide - How to Use

## 🚀 Quick Start

1. **Go to:** `https://hv-ecg.web.app/gallery.html`
2. **Sign in** (anonymous sign-in is automatic)
3. **Wait for images to load** (see console: "Loaded X images")
4. **Open console** (Press F12)

---

## 📋 Copy Version Info

**Two ways to copy:**

1. **Click the footer** - Click anywhere on the version line at the bottom
2. **Click copy button** - Click the "📋 Copy" button (if visible)

**Copies this format:**
```
Version: 2.3.3 | Build: 2026.01.20.0715 | Deployed: 1/20/2026, 7:15:00 AM | Firebase SDK: 10.7.1
```

---

## 🧪 Bulk Testing

### Quick Test (All Images)

**In browser console:**
```javascript
quickBulkTest();
```

**What it does:**
- Finds all images in gallery
- Processes up to 10 images in parallel
- Tests: edge detection, color separation, grid detection, quality checks
- Shows results in console

### Custom Test

```javascript
bulkTestGallery({
    edge_detection: true,
    color_separation: true,
    grid_detection: true,
    quality_check: true
});
```

### Wait for Images First

If you see "No valid images found":
```javascript
// Wait 3 seconds, then test
setTimeout(() => quickBulkTest(), 3000);
```

---

## 🔍 Individual Image Functions

### Edge Detection
```javascript
const img = document.querySelector('.gallery-item img');
detectEdges(img, 'canny', true).then(console.log);
```

### Process Single Image
```javascript
const img = document.querySelector('.gallery-item img');
processBatch([img], {
    edge_detection: true,
    color_separation: true
}).then(console.log);
```

### Process Multiple Images
```javascript
const images = Array.from(document.querySelectorAll('.gallery-item img')).slice(0, 5);
processBatch(images, {
    edge_detection: true,
    color_separation: true,
    grid_detection: true
}).then(console.log);
```

---

## 📊 Understanding Results

### Successful Result
```javascript
{
    success: true,
    count: 10,
    results: [
        {
            index: 0,
            success: true,
            steps: {
                edge_detection: { bounding_box: {...}, edge_pixels: 12345 },
                color_separation: { method: 'lab', trace_pixels: 5678 },
                grid_detection: { fine_lines: 50, bold_lines: 10 },
                quality_check: { passed: true, blur_score: 0.85 }
            }
        }
    ]
}
```

### Failed Result
```javascript
{
    success: false,
    error: 'Failed to fetch'  // Usually CORS or service not available
}
```

---

## ⚠️ Common Issues

### "quickBulkTest is not defined"
**Solution:** Deploy hosting
```powershell
firebase deploy --only hosting
```

### CORS Errors
**Solution:** Deploy Python service with CORS fix
```powershell
cd functions_python
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
gcloud run deploy ecg-multi-method --image gcr.io/hv-ecg/ecg-multi-method --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi --timeout 300 --max-instances 10
```

### "No valid images found"
**Solution:** Wait for images to load
```javascript
setTimeout(() => quickBulkTest(), 3000);
```

---

## 🎯 Typical Workflow

1. Open gallery page
2. Wait for images (check console: "Loaded X images")
3. Open console (F12)
4. Run: `quickBulkTest()`
5. View results in console
6. Copy version info by clicking footer

---

*Quick Gallery Guide - January 21, 2026*
