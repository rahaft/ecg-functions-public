# Google Cloud Storage Setup - Step-by-Step Instructions

## Prerequisites
- ✅ Google Cloud account with credits
- ✅ Python installed
- ✅ Kaggle API credentials configured (in `~/.kaggle/kaggle.json`)

---

## Step 1: Create Google Cloud Project (5 minutes)

1. Go to: **https://console.cloud.google.com/**
2. Click the **project dropdown** at the top
3. Click **"New Project"**
4. Enter:
   - **Project name**: `ecg-competition`
   - (Project ID will auto-generate)
5. Click **"Create"**
6. Wait 30 seconds for project creation

---

## Step 2: Enable Required APIs (2 minutes)

1. Go to: **APIs & Services** → **Library**
   - Or visit: https://console.cloud.google.com/apis/library

2. Search for and enable these APIs:
   - **"Cloud Storage API"** → Click → **Enable**
   - **"Cloud Storage JSON API"** → Click → **Enable**

**Or use command line:**
```powershell
# Install gcloud CLI first if needed: https://cloud.google.com/sdk/docs/install
gcloud services enable storage-api.googleapis.com
gcloud services enable storage-component.googleapis.com
```

---

## Step 3: Create Service Account (5 minutes)

**This gives your scripts permission to upload files:**

1. Go to: **IAM & Admin** → **Service Accounts**
   - Or visit: https://console.cloud.google.com/iam-admin/serviceaccounts

2. Click **"Create Service Account"**

3. Fill in:
   - **Service account name**: `kaggle-gcs-transfer`
   - **Description**: `For transferring Kaggle data to GCS`
   - Click **"Create and Continue"**

4. Grant role: **"Storage Admin"** (type "Storage Admin" in search)
   - Click **"Continue"**

5. Click **"Done"**

6. **Create a key:**
   - Click on the service account you just created
   - Go to **"Keys"** tab
   - Click **"Add Key"** → **"Create new key"**
   - Choose **JSON**
   - Click **"Create"** - file will download automatically
   - **Save this file** as `service-account-key.json` in your project root folder

---

## Step 4: Install Python Dependencies (2 minutes)

```powershell
# Make sure you're in your project directory
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"

# Install required packages
pip install google-cloud-storage kaggle tqdm
```

---

## Step 5: Set Up Authentication (1 minute)

**Option A: Using Service Account Key (Recommended)**

```powershell
# Set environment variable (Windows PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json"

# To make it permanent for this session, add to your PowerShell profile
# Or just run this command each time you open a new terminal
```

**Option B: Using gcloud CLI**

```powershell
# Install gcloud CLI: https://cloud.google.com/sdk/docs/install
gcloud auth login
gcloud auth application-default login
gcloud config set project ecg-competition
```

---

## Step 6: Update Project ID in Script (1 minute)

1. Open: `scripts/create_multiple_gcs_buckets.py`
2. Find line: `PROJECT_ID = "ecg-competition"`
3. Change to your actual project ID if different
   - Your project ID is shown in the Google Cloud Console at the top

---

## Step 7: Create GCS Buckets (2 minutes)

```powershell
# Make sure you're in your project directory
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"

# Make sure authentication is set (Step 5)
# Then run:
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

**Verify in Console:**
- Go to: **Cloud Storage** → **Buckets**
- You should see 5 buckets created

---

## Step 8: Set Up Billing Alerts (CRITICAL - 3 minutes)

**Avoid surprise charges!**

1. Go to: **Billing** → **Budgets & alerts**
   - Or visit: https://console.cloud.google.com/billing/budgets

2. Click **"Create Budget"**

3. Set up:
   - **Budget name**: `ECG Competition - $5 Alert`
   - **Budget amount**: `$5`
   - **Period**: `Monthly`
   - Click **"Next"**

4. Add alerts:
   - **Alert threshold 1**: `50%` ($2.50)
   - **Alert threshold 2**: `90%` ($4.50)
   - **Alert threshold 3**: `100%` ($5.00)
   - **Email notifications**: Add your email
   - Click **"Create Budget"**

---

## Step 9: Transfer Images from Kaggle to GCS (This takes time!)

```powershell
# Make sure you're in your project directory
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"

# Make sure authentication is set (Step 5)
# Make sure Kaggle credentials are set up

# Run the transfer script
python scripts/kaggle_to_gcs_transfer.py
```

**What this does:**
- ✅ Lists all images from Kaggle competition
- ✅ Distributes them across 5 buckets (~20GB each)
- ✅ Downloads ONE file at a time to temp directory
- ✅ Immediately uploads to GCS
- ✅ Deletes temp file immediately
- ✅ Does NOT accumulate files on your computer

**This will take a while** (85GB of data). You'll see a progress bar.

**Note:** The script uses minimal local storage - only one file at a time in temp directory.

---

## Step 10: Import Manifest to Firestore (2 minutes)

**After transfer completes, import the manifest for the viewer:**

```powershell
# Make sure you're in your project directory
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"

# Make sure Firebase is initialized (you should already have this from your Firebase setup)
# Make sure serviceAccountKey.json exists in project root

# Run the import script
python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json
```

**Expected output:**
```
✓ Firebase Firestore connected
Importing X images to Firestore...
✓ Import complete: X/X images
```

---

## Step 11: Verify Everything Works

1. **Check GCS Buckets:**
   - Go to: **Cloud Storage** → **Buckets**
   - Click on each bucket to see files

2. **Check Firestore:**
   - Go to: **Firestore Database**
   - Check `kaggle_images` collection
   - Should see image documents

3. **Test the Viewer:**
   - Deploy your Firebase app: `firebase deploy --only hosting`
   - Go to: `training_viewer.html`
   - Click "Load Local Images" to see imported images

---

## Troubleshooting

### "Access Denied" error
- ✅ Check service account has "Storage Admin" role
- ✅ Verify `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- ✅ Make sure the JSON key file path is correct

### "Bucket already exists" error
- Bucket names are globally unique
- The script will skip existing buckets
- Or change bucket prefix in the script

### "Project not found" error
- ✅ Update `PROJECT_ID` in `create_multiple_gcs_buckets.py`
- ✅ Or set: `gcloud config set project YOUR_PROJECT_ID`

### "Kaggle API not authenticated"
- ✅ Make sure `~/.kaggle/kaggle.json` exists
- ✅ Or set `KAGGLE_USERNAME` and `KAGGLE_KEY` environment variables

### Transfer is slow
- This is normal - 85GB takes time
- The script processes one file at a time
- Progress bar shows current status

---

## Cost Monitoring

**Check your usage:**
1. Go to: **Billing** → **Reports**
2. See current charges
3. Go to: **Billing** → **Budgets & alerts**
4. Check alert status

**Expected costs:**
- First 5GB: **FREE** (free tier)
- Next 80GB in Archive: **$0.10/month**
- **Total: ~$0.10/month**

**With your credits**, this will last a very long time!

---

## Quick Reference Commands

```powershell
# Set authentication (run each time you open new terminal)
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json"

# Create buckets
python scripts/create_multiple_gcs_buckets.py

# Transfer images
python scripts/kaggle_to_gcs_transfer.py

# Import to Firestore
python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json
```

---

## Next Steps After Setup

1. ✅ All images stored in GCS (distributed across 5 buckets)
2. ✅ Manifest imported to Firestore
3. ✅ Training viewer can access images
4. → Start processing images with your digitization pipeline!
