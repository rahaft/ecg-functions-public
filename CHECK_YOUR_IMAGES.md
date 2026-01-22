# Check Your Images - Direct Links

## 🔗 Direct Links to Check Your Buckets

### Google Cloud Console Links:

1. **Bucket 1:** https://console.cloud.google.com/storage/browser/ecg-competition-data-1?project=hv-ecg
2. **Bucket 2:** https://console.cloud.google.com/storage/browser/ecg-competition-data-2?project=hv-ecg
3. **Bucket 3:** https://console.cloud.google.com/storage/browser/ecg-competition-data-3?project=hv-ecg
4. **Bucket 4:** https://console.cloud.google.com/storage/browser/ecg-competition-data-4?project=hv-ecg
5. **Bucket 5:** https://console.cloud.google.com/storage/browser/ecg-competition-data-5?project=hv-ecg

### All Buckets Overview:
https://console.cloud.google.com/storage/browser?project=hv-ecg

---

## 📋 Use Existing Manifest

I found `image_manifest_gcs.json` in your project! This should show where images are.

### Option 1: Use Existing Manifest

```powershell
# Check the manifest
Get-Content image_manifest_gcs.json | Select-Object -First 50

# If it has the right format, copy it:
copy image_manifest_gcs.json public\gcs_images_manifest.json
firebase deploy --only hosting
```

### Option 2: Regenerate Manifest (Updated Script)

The `list_gcs_images.py` script has been updated to:
- ✅ Try multiple prefixes automatically
- ✅ Find images wherever they are
- ✅ Show which prefix worked

```powershell
python scripts/list_gcs_images.py
```

---

## 🔍 Quick Check Commands

### Check if manifest exists:
```powershell
Test-Path image_manifest_gcs.json
```

### View manifest structure:
```powershell
Get-Content image_manifest_gcs.json | ConvertFrom-Json | Select-Object -First 1
```

### Count images in manifest:
```powershell
(Get-Content image_manifest_gcs.json | ConvertFrom-Json).images.Count
```

---

## ✅ Next Steps

1. **Check the links above** - See what's actually in your buckets
2. **Check existing manifest** - `image_manifest_gcs.json` might already have the info
3. **Run updated script** - `list_gcs_images.py` now searches all prefixes automatically
4. **Deploy manifest** - Copy to `public/` and deploy

---

**The updated script will find your images automatically!** 🚀
