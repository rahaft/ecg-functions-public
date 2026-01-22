# CORS & Pagination - Complete Summary

## 🔒 What is CORS?

**CORS** = **Cross-Origin Resource Sharing**

It's a browser security feature that controls which websites can access resources from other domains.

### Why You Need It

When your website (`https://hv-ecg.web.app`) tries to load images from GCS (`https://storage.googleapis.com`), the browser blocks it because they're different domains.

**CORS configuration tells Google Cloud:**
> "Allow `https://hv-ecg.web.app` to access images in these buckets"

### Configure CORS:
```powershell
python scripts/configure_gcs_cors.py
```

**Without CORS:** ❌ Images won't load, gallery empty  
**With CORS:** ✅ Images load, gallery works!

---

## 📄 Pagination & Lazy Loading

### What's New

The gallery now loads **efficiently** with pagination:

- ✅ **Initial load:** Only 30 images or 3 groups
- ✅ **"Load More" button:** Loads next batch
- ✅ **Lazy loading:** Images load as you scroll
- ✅ **Smart limits:** Respects both group and image limits

### How It Works

1. **First load:** Shows up to 3 groups OR 30 images (whichever limit is hit first)
2. **Click "Load More":** Loads next batch
3. **Button shows:** Remaining group count
4. **Button hides:** When all groups are loaded

### Configuration

In `gallery.html`:
```javascript
const GROUPS_PER_PAGE = 3;  // Show 3 groups at a time
const IMAGES_PER_PAGE = 30; // Or 30 images total
```

---

## 🚀 Get Gallery Working

### Step 1: Convert Manifest
```powershell
python scripts/convert_manifest_for_gallery.py
```

### Step 2: Copy to Public
```powershell
copy gcs_images_manifest.json public\gcs_images_manifest.json
```

### Step 3: Configure CORS
```powershell
python scripts/configure_gcs_cors.py
```

### Step 4: Make Buckets Public
```powershell
python scripts/make_buckets_public.py
```

### Step 5: Deploy
```powershell
firebase deploy --only hosting
```

---

## ✅ Result

- ✅ Gallery loads 30 images or 3 groups initially
- ✅ "Load More" button at bottom
- ✅ Images grouped by prefix (before `-`) or folder
- ✅ Lazy loading for performance
- ✅ All 8,795 images accessible via pagination

---

**CORS allows access, pagination makes it efficient!** 🚀
