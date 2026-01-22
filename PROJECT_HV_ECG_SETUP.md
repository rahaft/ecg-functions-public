# Setting Up Google Cloud Storage for hv-ECG Project

## Your Project Information

- **Project Name**: `hv-ECG`
- **Project ID**: `hv-ECG` (or possibly `hv-ecg` - check in console)

## Important: Token vs Service Account Key

The token you provided (`AQ.Ab8RN6Lgrsy7Sz7t55tK_mXqfY2vpSgana8zydbmpO5G4VMNmg`) appears to be:
- A Firebase API key, OR
- An OAuth access token

**This won't work directly** for Google Cloud Storage Python scripts. The GCS scripts need a **Service Account JSON Key File**.

## Solution: Create Service Account in Your Existing Project

Since you already have a Google Cloud project (`hv-ECG`), let's create a service account in it:

### Step 1: Create Service Account in hv-ECG Project

1. **Go to:** https://console.cloud.google.com/iam-admin/serviceaccounts?project=hv-ECG
   - Or: https://console.cloud.google.com/iam-admin/serviceaccounts (make sure `hv-ECG` is selected)

2. **Click:** "Create Service Account"

3. **Fill in:**
   - **Service account name**: `kaggle-gcs-transfer`
   - **Description**: `For transferring Kaggle data to GCS`
   - Click **"Create and Continue"**

4. **Grant Role:**
   - Type: **"Storage Admin"** in the search box
   - Select: **Storage Admin**
   - Click **"Continue"**

5. **Click:** "Done"

### Step 2: Create JSON Key

1. **Click on the service account** you just created (`kaggle-gcs-transfer`)

2. **Go to:** "Keys" tab

3. **Click:** "Add Key" → "Create new key"

4. **Choose:** JSON

5. **Click:** "Create" → File downloads automatically

6. **Save the file:**
   - Rename it to: `service-account-key.json`
   - Move it to your project root:
     ```
     C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json
     ```

### Step 3: Set Up Authentication

Open PowerShell:

```powershell
# Navigate to your project
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"

# Set the environment variable
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json"

# Verify it's set
echo $env:GOOGLE_APPLICATION_CREDENTIALS

# Test authentication
python -c "from google.cloud import storage; client = storage.Client(project='hv-ECG'); print('✓ Authentication successful!')"
```

## Scripts Are Already Updated

✅ I've already updated `scripts/create_multiple_gcs_buckets.py` to use project ID: `hv-ECG`

✅ The scripts will now use your project automatically!

## Verify Your Project ID

If you're not sure of the exact project ID (might be `hv-ECG` or `hv-ecg`):

1. **Check in Google Cloud Console:**
   - Look at the top of the page - it shows your project ID
   - Or go to: https://console.cloud.google.com/home/dashboard

2. **Update the script if needed:**
   - Open: `scripts/create_multiple_gcs_buckets.py`
   - Line 22: `PROJECT_ID = "hv-ECG"` ← Change if your ID is different

## Enable Required APIs

Make sure these APIs are enabled in your `hv-ECG` project:

1. **Go to:** https://console.cloud.google.com/apis/library?project=hv-ECG

2. **Search and enable:**
   - **"Cloud Storage API"** → Enable
   - **"Cloud Storage JSON API"** → Enable

**Or use command line:**
```powershell
gcloud services enable storage-api.googleapis.com --project=hv-ECG
gcloud services enable storage-component.googleapis.com --project=hv-ECG
```

## Next Steps

Once you have `service-account-key.json` and authentication set:

1. ✅ **Create buckets:**
   ```powershell
   python scripts/create_multiple_gcs_buckets.py
   ```

2. ✅ **Transfer images:**
   ```powershell
   python scripts/kaggle_to_gcs_transfer.py
   ```

3. ✅ **Import manifest:**
   ```powershell
   python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json
   ```

## Troubleshooting

### "Permission denied" or "Access denied"
- ✅ Check service account has "Storage Admin" role
- ✅ Verify APIs are enabled (Storage API, Storage JSON API)
- ✅ Make sure you're using the correct project ID

### "Project not found"
- ✅ Verify project ID is correct (`hv-ECG` or `hv-ecg`)
- ✅ Check you have access to the project in Google Cloud Console

### "Could not automatically determine credentials"
- ✅ Check `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set
- ✅ Verify path to `service-account-key.json` is correct
- ✅ Use absolute path (starting with `C:\`)

## About the Token You Provided

The token (`AQ.Ab8RN6Lgrsy7Sz7t55tK_mXqfY2vpSgana8zydbmpO5G4VMNmg`) might be useful for:
- Firebase API calls
- OAuth authentication
- Other Google Cloud services

But for **Google Cloud Storage Python scripts**, you need the **Service Account JSON Key File** as described above.
