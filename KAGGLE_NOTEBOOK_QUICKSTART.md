# Kaggle Notebook Transfer - Quick Start

## ✅ You're All Set!

You have:
- ✅ Notebook created and attached to competition
- ✅ Google Cloud Services enabled
- ✅ Account `hi@pathomap.co` connected
- ✅ Competition data attached (train/ and test/ folders)

## 🚀 Copy & Paste Code

### Step 1: Open the Ready-to-Use Code

Open `kaggle_notebook_ready_to_use.py` and copy **all the code**.

### Step 2: Replace the Code in Your Notebook

1. **In your Kaggle notebook**, select **all the code** in the cell (Ctrl+A)
2. **Delete it**
3. **Paste** the code from `kaggle_notebook_ready_to_use.py`
4. **Make sure project ID is correct**: `PROJECT_ID = "hv-ecg"` (line 13)

### Step 3: Ensure You're Using the Right Account

**If you need to switch to hi@pathomap.co:**

1. In your Kaggle notebook, click **"Add-ons"** → **"Google Cloud Services"**
2. Make sure **hi@pathomap.co** is selected/active
3. If not, click the account and select it

### Step 4: Run!

1. **Click:** "Run All" (or press Shift+Enter)
2. **Wait for completion** - Progress bar will show transfer status
3. **Download the manifest** - The `image_manifest_gcs.json` will be in `/kaggle/working/`

## 📋 What the Code Does

1. ✅ **Connects to GCS** using project `hv-ecg`
2. ✅ **Verifies your 5 buckets** exist
3. ✅ **Scans** `/kaggle/input/physionet-ecg-image-digitization/` for image files
4. ✅ **Distributes** files across buckets (round-robin)
5. ✅ **Transfers** images directly from Kaggle to GCS
6. ✅ **Creates manifest** file for Firestore import

## 📊 Expected Output

```
✓ Connected to GCS project: hv-ecg
📁 Verifying buckets...
  ✓ ecg-competition-data-1
  ✓ ecg-competition-data-2
  ...
📋 Listing files from competition...
✓ Found X total files
  📸 Image files: Y
    - Train: Z
    - Test: W
☁️  Transferring Y images...
[Progress bar will show here]
✓ Transfer complete: Y/Y images
📝 Creating manifest...
✨ Transfer Complete!
```

## 🔍 Troubleshooting

### "No buckets found"
- ✅ Make sure buckets are created first
- ✅ Run locally: `python scripts/create_multiple_gcs_buckets.py`
- ✅ Verify project ID is `hv-ecg`

### "Competition data not found"
- ✅ Click "Add data" (right sidebar)
- ✅ Search: `physionet-ecg-image-digitization`
- ✅ Click "Add" to attach dataset

### "Permission denied"
- ✅ Check Google Cloud account is `hi@pathomap.co`
- ✅ Verify account has access to project `hv-ecg`
- ✅ Make sure "Cloud Storage" is enabled in Add-ons

### "Wrong account being used"
- ✅ Go to "Add-ons" → "Google Cloud Services"
- ✅ Select/activate `hi@pathomap.co` account
- ✅ Re-run the notebook

## ✅ After Transfer

1. **Download manifest:**
   - In Kaggle notebook, go to "Output" panel
   - Click "image_manifest_gcs.json" to download
   - Save to your project directory

2. **Import to Firestore:**
   ```powershell
   python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json
   ```

3. **Verify in GCS:**
   - Go to: https://console.cloud.google.com/storage/browser?project=hv-ecg
   - Check your buckets for transferred files

## 🎉 That's It!

Just copy, paste, and run! The transfer happens entirely in Kaggle - no local download needed.
