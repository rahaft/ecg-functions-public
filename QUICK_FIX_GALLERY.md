# Quick Fix: Gallery from Existing Manifest

## ✅ Found Your Images!

You have **8,795 images** already transferred! The manifest shows:
- **Buckets:** ecg-competition-data-1 through ecg-competition-data-5
- **Path:** `kaggle-data/physionet-ecg/`
- **Manifest:** `image_manifest_gcs.json` (already exists!)

---

## 🚀 3-Step Fix

### Step 1: Convert Manifest to Gallery Format

```powershell
python scripts/convert_manifest_for_gallery.py
```

This converts your existing `image_manifest_gcs.json` to the format the gallery needs.

### Step 2: Copy to Public Folder

```powershell
copy gcs_images_manifest.json public\gcs_images_manifest.json
```

### Step 3: Deploy

```powershell
firebase deploy --only hosting
```

---

## 🔗 Direct Links to Check Your Buckets

1. **Bucket 1:** https://console.cloud.google.com/storage/browser/ecg-competition-data-1?project=hv-ecg
2. **Bucket 2:** https://console.cloud.google.com/storage/browser/ecg-competition-data-2?project=hv-ecg
3. **Bucket 3:** https://console.cloud.google.com/storage/browser/ecg-competition-data-3?project=hv-ecg
4. **Bucket 4:** https://console.cloud.google.com/storage/browser/ecg-competition-data-4?project=hv-ecg
5. **Bucket 5:** https://console.cloud.google.com/storage/browser/ecg-competition-data-5?project=hv-ecg

**All Buckets:** https://console.cloud.google.com/storage/browser?project=hv-ecg

---

## 📋 What the Manifest Shows

- ✅ **8,795 images** transferred
- ✅ **5 buckets** used
- ✅ **Path:** `kaggle-data/physionet-ecg/test/` and `kaggle-data/physionet-ecg/train/`
- ✅ **Public URLs:** `https://storage.googleapis.com/{bucket}/kaggle-data/physionet-ecg/{path}`

---

## ⚠️ Before Gallery Works

Make sure buckets are public and CORS is configured:

```powershell
# Make buckets public
python scripts/make_buckets_public.py

# Configure CORS
python scripts/configure_gcs_cors.py
```

---

## ✅ After Deploy

Gallery will show all **8,795 images** at:
**https://hv-ecg.web.app/gallery.html**

---

**Your images are already there - just need to convert the manifest!** 🎉
