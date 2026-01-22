# Transfer from Kaggle Notebook to Google Cloud Storage

## 🎯 Why This is Better

**Running the transfer from a Kaggle notebook is MUCH better because:**
- ✅ **No local download** - Files transfer directly from Kaggle to GCS
- ✅ **Faster** - Uses Kaggle's infrastructure (no bandwidth limits)
- ✅ **No authentication issues** - Kaggle handles the competition data access
- ✅ **Free** - Uses Kaggle's free compute resources
- ✅ **Easier** - Just copy/paste code and run

## 📋 Step-by-Step Instructions

### Step 1: Create Kaggle Notebook

1. **Go to:** https://www.kaggle.com/code
2. **Click:** "New Notebook"
3. **Select competition:** `physionet-ecg-image-digitization`
4. **Click:** "Create"

### Step 2: Enable Google Cloud Services

1. **In your Kaggle notebook**, look for the **"Add-ons"** menu
2. **Click:** "Add-ons" → "Google Cloud Services"
3. **Enable:** "Cloud Storage"
4. **Authenticate** with your Google Cloud account
5. **Enter your project ID:** `hv-ecg`

### Step 3: Attach Competition Data

1. **In the notebook**, click **"Add data"** (on the right sidebar)
2. **Search for:** `physionet-ecg-image-digitization`
3. **Click:** "Add" to attach the competition dataset

### Step 4: Copy the Code

1. **Open:** `kaggle_notebook_transfer.py` (I created this for you)
2. **Copy all the code**
3. **Paste it into your Kaggle notebook**
4. **Update the project ID** if needed (line 10: `PROJECT_ID = "hv-ecg"`)

### Step 5: Run the Notebook

1. **Click:** "Run All" (or press Shift+Enter on each cell)
2. **Wait for completion** - This will transfer all images to your GCS buckets
3. **Download the manifest** - The `image_manifest_gcs.json` will be in the output

## 🔑 Authentication Setup

**For Google Cloud in Kaggle:**

1. **In Kaggle notebook**, go to **"Add-ons"** → **"Google Cloud Services"**
2. **Click:** "Connect to Google Cloud"
3. **Authenticate** with your Google account
4. **Select project:** `hv-ecg`
5. **Grant permissions** for Cloud Storage

**OR use service account:**

1. **Create a service account key** (you already have this: `service-account-key.json`)
2. **In Kaggle notebook**, go to **"Add-ons"** → **"Secrets"**
3. **Add secret:**
   - Name: `GOOGLE_APPLICATION_CREDENTIALS`
   - Value: Paste the entire JSON content from `service-account-key.json`
4. **Update code** to use the secret:
   ```python
   import os
   from google.oauth2 import service_account
   import json
   
   # Get credentials from Kaggle secrets
   creds_json = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
   creds_dict = json.loads(creds_json)
   credentials = service_account.Credentials.from_service_account_info(creds_dict)
   
   storage_client = storage.Client(project='hv-ecg', credentials=credentials)
   ```

## 📊 What Gets Transferred

- ✅ All image files from the competition
- ✅ Distributed across 5 GCS buckets (~20GB each)
- ✅ Metadata preserved (train/test, folder structure)
- ✅ Manifest file created for Firestore import

## ⚡ Advantages Over Local Transfer

| Local Transfer | Kaggle Notebook Transfer |
|---------------|-------------------------|
| Downloads 85GB to your computer | No local download |
| Uses your bandwidth | Uses Kaggle's bandwidth |
| Slow (depends on your internet) | Fast (Kaggle's infrastructure) |
| Authentication issues | Handled by Kaggle |
| Takes hours | Takes minutes |

## 🎯 After Transfer

1. **Download the manifest:**
   - In Kaggle notebook output, download `image_manifest_gcs.json`
   - Save it to your project directory

2. **Import to Firestore:**
   ```powershell
   python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json
   ```

3. **Verify in GCS:**
   - Go to: https://console.cloud.google.com/storage/browser?project=hv-ecg
   - Check your buckets for transferred files

## 🆘 Troubleshooting

### "Project not found"
- ✅ Check project ID is correct: `hv-ecg`
- ✅ Verify you have access to the project

### "Bucket not found"
- ✅ Make sure buckets are created first
- ✅ Run: `python scripts/create_multiple_gcs_buckets.py` (locally)

### "Permission denied"
- ✅ Check service account has "Storage Admin" role
- ✅ Verify authentication in Kaggle notebook

### "Competition data not found"
- ✅ Make sure competition dataset is attached to notebook
- ✅ Check dataset name matches: `physionet-ecg-image-digitization`

## ✅ Quick Start

1. Create Kaggle notebook
2. Enable Google Cloud Services
3. Attach competition data
4. Copy code from `kaggle_notebook_transfer.py`
5. Run!

That's it! Much simpler than local transfer.
