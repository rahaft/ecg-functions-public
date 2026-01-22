# Quick Setup: Gallery from GCS Buckets

## 🚀 3-Step Setup

### Step 1: Make Buckets Public & Configure CORS

```powershell
# Make buckets publicly readable
python scripts/make_buckets_public.py

# Configure CORS for web access
python scripts/configure_gcs_cors.py
```

### Step 2: Generate Image Manifest

```powershell
# List all images and create manifest
python scripts/list_gcs_images.py
```

This creates `gcs_images_manifest.json`.

### Step 3: Deploy Manifest & Gallery

```powershell
# Copy manifest to public folder
copy gcs_images_manifest.json public\gcs_images_manifest.json

# Deploy to Firebase Hosting
firebase deploy --only hosting
```

---

## ✅ Done!

Gallery will now load images from GCS buckets:
- **URL:** https://hv-ecg.web.app/gallery.html
- **Source:** GCS buckets (no Firebase Storage costs!)
- **Credits:** Uses your GCS credits

---

## 🔄 When Adding New Images

1. Transfer from Kaggle to GCS (existing process)
2. Regenerate manifest: `python scripts/list_gcs_images.py`
3. Copy to public: `copy gcs_images_manifest.json public\gcs_images_manifest.json`
4. Redeploy: `firebase deploy --only hosting`

---

**That's it!** 🎉
