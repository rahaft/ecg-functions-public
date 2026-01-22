# Deploy Updates - CORS Fix & Bulk Testing

## What Needs to Be Deployed

### 1. Python Service with CORS Fix ✅
- **File:** `functions_python/main.py`
- **Change:** Added CORS support for cross-origin requests
- **Status:** Code ready, needs deployment

### 2. Gallery with Bulk Testing Functions ✅
- **File:** `public/gallery.html`
- **Changes:**
  - Added `bulkTestGallery()` function
  - Added `quickBulkTest()` function
  - Improved footer (easier to copy version info)
  - Fixed image loading in `getImageAsBase64()`
- **Status:** Code ready, needs deployment

---

## Quick Deploy Commands

### Step 1: Deploy Python Service (CORS Fix)

```powershell
cd functions_python
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
gcloud run deploy ecg-multi-method --image gcr.io/hv-ecg/ecg-multi-method --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi --timeout 300 --max-instances 10
cd ..
```

### Step 2: Deploy Hosting (Bulk Testing & Footer)

```powershell
firebase deploy --only hosting
```

---

## After Deployment

### Test Bulk Testing

1. Go to: `https://hv-ecg.web.app/gallery.html`
2. Wait for images to load
3. Open console (F12)
4. Run: `quickBulkTest()`

### Test Footer Copy

1. Scroll to bottom of page
2. Click "Copy Version Info" button
3. Version info will be copied to clipboard in format:
   ```
   Version: 2.3.3
   Build: 2026.01.21.2235
   Deployed: 1/21/2026, 10:35:00 PM
   Firebase SDK: 10.7.1
   ```

---

## What's Fixed

✅ **CORS Error** - Python service now allows requests from `https://hv-ecg.web.app`  
✅ **Bulk Testing** - `quickBulkTest()` and `bulkTestGallery()` functions available  
✅ **Image Loading** - Fixed null image error in `getImageAsBase64()`  
✅ **Footer Copy** - Easy copy button for version info  

---

*Deploy Updates - January 21, 2026*
