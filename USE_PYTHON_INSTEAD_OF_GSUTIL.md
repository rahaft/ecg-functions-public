# Use Python Scripts Instead of gsutil

## 🚨 Problem: gsutil Permission Error

`gsutil` is failing with permission errors. **Use Python scripts instead** - they work better and don't have this issue!

---

## ✅ Solution: Use Python Scripts

The Python scripts use the `google-cloud-storage` library directly, which:
- ✅ Doesn't have permission issues
- ✅ Uses application default credentials
- ✅ Works the same way

---

## 🔍 Step 1: Run Diagnostic Script (Python)

Instead of `gsutil ls`, use:

```powershell
python scripts/diagnose_gcs_buckets.py
```

This will:
- Check all buckets
- Find where images actually are
- Show sample files
- **No permission issues!**

---

## 📋 Step 2: List Images (Python)

Instead of `gsutil ls -r`, use:

```powershell
python scripts/list_gcs_images.py
```

This will:
- List all images from GCS buckets
- Generate manifest file
- **No permission issues!**

---

## 🔧 Fix gsutil (Optional)

If you really need `gsutil` to work:

### Option A: Run PowerShell as Administrator

1. Close current PowerShell
2. Right-click PowerShell → **Run as Administrator**
3. Navigate back to project:
   ```powershell
   cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"
   ```
4. Try `gsutil` commands again

### Option B: Use Python Scripts (Recommended)

**Just use the Python scripts - they're better anyway!** ✅

---

## 📊 Python Scripts Available

| Task | Python Script | Instead of gsutil |
|------|--------------|-------------------|
| List images | `list_gcs_images.py` | `gsutil ls -r` |
| Diagnose buckets | `diagnose_gcs_buckets.py` | `gsutil ls` |
| Make buckets public | `make_buckets_public.py` | `gsutil iam ch` |
| Configure CORS | `configure_gcs_cors.py` | `gsutil cors set` |

---

## 🚀 Quick Start

**Right now, run:**

```powershell
# 1. Find where images are
python scripts/diagnose_gcs_buckets.py

# 2. Once you know the prefix, update list_gcs_images.py if needed
# 3. Then generate manifest:
python scripts/list_gcs_images.py

# 4. Copy and deploy:
copy gcs_images_manifest.json public\gcs_images_manifest.json
firebase deploy --only hosting
```

---

**Python scripts are the way to go!** 🐍✅
