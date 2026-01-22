# ✅ Setup Complete! Next Steps

## What's Been Done

1. ✅ **Service account key file copied** to project root: `service-account-key.json`
2. ✅ **Project ID updated** to `hv-ecg` (lowercase) in scripts
3. ✅ **Scripts ready** to use your credentials

## 🚀 Next Steps

### Step 1: Set Authentication (Run This in PowerShell)

Open PowerShell and run:

```powershell
# Navigate to project
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"

# Set environment variable
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json"

# Verify it's set
echo $env:GOOGLE_APPLICATION_CREDENTIALS
```

**Note:** You'll need to run this `$env:GOOGLE_APPLICATION_CREDENTIALS` command each time you open a new PowerShell window.

### Step 2: Test Authentication

```powershell
# Test authentication
python -c "from google.cloud import storage; client = storage.Client(project='hv-ecg'); print('✓ Authentication successful!')"
```

If you see "✓ Authentication successful!", you're ready!

### Step 3: Enable APIs (If Not Already Enabled)

Make sure these APIs are enabled in your `hv-ecg` project:

1. Go to: https://console.cloud.google.com/apis/library?project=hv-ecg
2. Search for and enable:
   - **"Cloud Storage API"** → Enable
   - **"Cloud Storage JSON API"** → Enable

### Step 4: Create GCS Buckets

```powershell
# Make sure you're in project directory and authentication is set
python scripts/create_multiple_gcs_buckets.py
```

**Expected output:**
```
✓ Created bucket: ecg-competition-data-1
✓ Created bucket: ecg-competition-data-2
✓ Created bucket: ecg-competition-data-3
✓ Created bucket: ecg-competition-data-4
✓ Created bucket: ecg-competition-data-5
```

### Step 5: Transfer Images from Kaggle

**This takes a while (85GB of data):**

```powershell
# Make sure Kaggle credentials are set up (~/.kaggle/kaggle.json)
python scripts/kaggle_to_gcs_transfer.py
```

This will:
- ✅ List all images from Kaggle
- ✅ Distribute them across 5 buckets (~20GB each)
- ✅ Download ONE file at a time to temp
- ✅ Upload to GCS immediately
- ✅ Delete temp file immediately
- ✅ **Does NOT accumulate files on your computer**

### Step 6: Import Manifest to Firestore

```powershell
python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json
```

This imports the image metadata to Firestore so your training viewer can access it.

## 📋 Quick Reference Commands

```powershell
# Set authentication (run each time you open PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json"

# Create buckets
python scripts/create_multiple_gcs_buckets.py

# Transfer images (takes a while)
python scripts/kaggle_to_gcs_transfer.py

# Import to Firestore
python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json
```

## 🔒 Security

✅ **Service account key is in `.gitignore`** - it won't be committed to Git!

⚠️ **Never share this file publicly!**

## 🆘 Troubleshooting

### "Could not automatically determine credentials"
- ✅ Check `GOOGLE_APPLICATION_CREDENTIALS` is set
- ✅ Verify the path to `service-account-key.json` is correct
- ✅ Run the `$env:GOOGLE_APPLICATION_CREDENTIALS` command in PowerShell

### "Permission denied"
- ✅ Check service account has "Storage Admin" role
- ✅ Verify APIs are enabled (Storage API, Storage JSON API)

### "Project not found"
- ✅ Verify project ID is `hv-ecg` (lowercase)
- ✅ Check you have access to the project in Google Cloud Console

## ✅ You're Ready!

All scripts are configured with:
- Project ID: `hv-ecg`
- Service account: `kaggle-gcs-transfer@hv-ecg.iam.gserviceaccount.com`
- Credentials file: `service-account-key.json`

Just set the environment variable and run the scripts!
