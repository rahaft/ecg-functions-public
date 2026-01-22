# Google Cloud Authentication Setup

## What You Need

For Google Cloud Storage scripts, you need a **Service Account JSON Key File**, not an API key token.

The format should look like this:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@project.iam.gserviceaccount.com",
  ...
}
```

## Step-by-Step: Create Service Account Key

### Option 1: Create New Service Account (Recommended)

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/iam-admin/serviceaccounts

2. **Select Your Project:**
   - Make sure "ecg-competition" (or your project) is selected at the top

3. **Create Service Account:**
   - Click **"Create Service Account"**
   - **Name**: `kaggle-gcs-transfer`
   - **Description**: `For transferring Kaggle data to GCS`
   - Click **"Create and Continue"**

4. **Grant Permissions:**
   - In "Grant this service account access to project"
   - Select role: **"Storage Admin"** (or search for "Storage Admin")
   - Click **"Continue"**
   - Click **"Done"**

5. **Create Key:**
   - Click on the service account you just created
   - Go to **"Keys"** tab
   - Click **"Add Key"** → **"Create new key"**
   - Choose **JSON**
   - Click **"Create"**
   - **File will download** - save it as `service-account-key.json`
   - **Move this file to your project root folder:**
     ```
     C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json
     ```

### Option 2: Use Application Default Credentials (Alternative)

If you have the gcloud CLI installed:

```powershell
# Install gcloud CLI if needed
# Download from: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Now scripts will use these credentials automatically
```

## Using the Token You Provided

The token you provided (`AQ.Ab8RN6Lgrsy7Sz7t55tK_mXqfY2vpSgana8zydbmpO5G4VMNmg`) might be:
- An OAuth refresh token
- A Firebase API key
- An access token

**This won't work directly** for Google Cloud Storage authentication in Python scripts.

**You need to either:**
1. Create a service account JSON key (Option 1 above) ✅ Recommended
2. Use gcloud CLI authentication (Option 2 above)

## Setting Up Authentication

### Once You Have service-account-key.json:

1. **Move the file to your project root:**
   ```
   C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json
   ```

2. **Set Environment Variable (Windows PowerShell):**
   ```powershell
   $env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json"
   ```

3. **Verify it's set:**
   ```powershell
   echo $env:GOOGLE_APPLICATION_CREDENTIALS
   ```

4. **Test authentication:**
   ```powershell
   python -c "from google.cloud import storage; client = storage.Client(); print('✓ Authentication successful!')"
   ```

### To Make It Permanent (Optional):

You can add the environment variable to your PowerShell profile:

```powershell
# Open PowerShell profile
notepad $PROFILE

# Add this line:
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json"

# Save and restart PowerShell
```

## Important Security Notes

⚠️ **NEVER** commit `service-account-key.json` to Git!

⚠️ **NEVER** share your service account key publicly!

✅ Add to `.gitignore`:
```
service-account-key.json
*.json
!firebase.json
!package.json
!tsconfig.json
```

## Next Steps

Once you have `service-account-key.json` in your project root and `GOOGLE_APPLICATION_CREDENTIALS` set:

1. ✅ Authentication is ready
2. ✅ Proceed to create buckets: `python scripts/create_multiple_gcs_buckets.py`
3. ✅ Then transfer images: `python scripts/kaggle_to_gcs_transfer.py`

## Troubleshooting

### "Could not automatically determine credentials"
- ✅ Check `GOOGLE_APPLICATION_CREDENTIALS` is set
- ✅ Verify path to JSON file is correct
- ✅ Make sure the JSON file is valid

### "Permission denied"
- ✅ Check service account has "Storage Admin" role
- ✅ Verify you're using the correct project ID

### "File not found"
- ✅ Check the path to `service-account-key.json`
- ✅ Use absolute path (full path from C:\)
- ✅ Make sure file exists at that location
