# Find Images in GCS Buckets

## 🚨 Problem: "No images found!"

The `list_gcs_images.py` script couldn't find images. Let's diagnose the issue.

---

## 🔍 Step 1: Run Diagnostic Script

```powershell
python scripts/diagnose_gcs_buckets.py
```

This will:
- Check if buckets exist
- Try different path prefixes
- Show sample files found
- Identify where images actually are

---

## 🔍 Step 2: Check Google Cloud Console

1. Go to: **https://console.cloud.google.com/storage/browser?project=hv-ecg**
2. Click on each bucket: `ecg-competition-data-1` through `ecg-competition-data-5`
3. Look for:
   - What folders/files exist?
   - What's the actual path structure?
   - Are there images at all?

---

## 🔍 Step 3: Check Transfer Status

If images haven't been transferred yet:

```powershell
# Check if transfer script exists
python scripts/kaggle_to_gcs_transfer.py --help

# Or check transfer logs/manifest
# Look for: image_manifest_gcs.json or similar
```

---

## 🔧 Step 4: Update Configuration

Once you find where images are:

### Option A: Images in different prefix

Edit `scripts/list_gcs_images.py`:

```python
# Change this line:
GCS_PREFIX = "kaggle-data/physionet-ecg/"

# To the actual prefix found, e.g.:
GCS_PREFIX = "train/"  # or whatever the diagnostic found
```

### Option B: Images in different buckets

Edit `scripts/list_gcs_images.py`:

```python
# Update bucket list:
GCS_BUCKETS = [
    "actual-bucket-name-1",
    "actual-bucket-name-2",
    # ... etc
]
```

### Option C: Images not transferred yet

Run the transfer script:

```powershell
python scripts/kaggle_to_gcs_transfer.py
```

---

## 📋 Common Issues

### Issue 1: Wrong Prefix

**Symptom:** Diagnostic finds images but with different prefix

**Fix:** Update `GCS_PREFIX` in `list_gcs_images.py`

### Issue 2: Buckets Don't Exist

**Symptom:** "Bucket does not exist" errors

**Fix:** 
- Check bucket names in Google Cloud Console
- Or create buckets: `python scripts/create_multiple_gcs_buckets.py`

### Issue 3: No Images Transferred

**Symptom:** Buckets exist but are empty

**Fix:** Transfer images from Kaggle:
```powershell
python scripts/kaggle_to_gcs_transfer.py
```

### Issue 4: Authentication Issue

**Symptom:** "Permission denied" or "Not authenticated"

**Fix:**
```powershell
gcloud auth application-default login
```

---

## ✅ After Finding Images

1. **Update `list_gcs_images.py`** with correct prefix/buckets
2. **Run again:**
   ```powershell
   python scripts/list_gcs_images.py
   ```
3. **Should now create manifest:**
   ```powershell
   copy gcs_images_manifest.json public\gcs_images_manifest.json
   firebase deploy --only hosting
   ```

---

**Run the diagnostic script first to see what's actually in your buckets!** 🔍
