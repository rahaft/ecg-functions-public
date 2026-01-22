# Quick Authentication Setup for Google Cloud Storage

## ❌ The Token You Provided

The token you shared (`AQ.Ab8RN6Lgrsy7Sz7t55tK_mXqfY2vpSgana8zydbmpO5G4VMNmg`) is **not the right format** for Google Cloud Storage scripts.

## ✅ What You Need Instead

You need a **Service Account JSON Key File** that looks like this:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create Service Account

1. **Go to:** https://console.cloud.google.com/iam-admin/serviceaccounts
   - Make sure your project is selected at the top

2. **Click:** "Create Service Account"

3. **Fill in:**
   - **Name**: `kaggle-gcs-transfer`
   - Click **"Create and Continue"**

4. **Grant Role:**
   - Type: **"Storage Admin"**
   - Select: **Storage Admin**
   - Click **"Continue"** → **"Done"**

5. **Create Key:**
   - Click on the service account you just created
   - Go to **"Keys"** tab
   - Click **"Add Key"** → **"Create new key"**
   - Choose **JSON**
   - Click **"Create"** → **File downloads automatically**

6. **Save the file:**
   - Save it as: `service-account-key.json`
   - Move it to your project root:
     ```
     C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json
     ```

### Step 2: Set Up Authentication

Open PowerShell and run:

```powershell
# Navigate to your project
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"

# Set the environment variable (run each time you open PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json"

# Verify it's set
echo $env:GOOGLE_APPLICATION_CREDENTIALS
```

### Step 3: Test Authentication

```powershell
# Test that it works
python -c "from google.cloud import storage; client = storage.Client(); print('✓ Authentication successful!')"
```

If you see "✓ Authentication successful!", you're ready to go!

## 🔒 Security Note

⚠️ **NEVER commit `service-account-key.json` to Git!**

Make sure it's in `.gitignore`:

```powershell
# Check .gitignore
echo "service-account-key.json" >> .gitignore
```

## ✅ What's Next?

Once authentication is set up:

1. ✅ Create buckets: `python scripts/create_multiple_gcs_buckets.py`
2. ✅ Transfer images: `python scripts/kaggle_to_gcs_transfer.py`
3. ✅ Import manifest: `python scripts/import_gcs_manifest_to_firestore.py`

## 🆘 Troubleshooting

### "Could not automatically determine credentials"
- Check `GOOGLE_APPLICATION_CREDENTIALS` is set
- Verify the path to JSON file is correct
- Use **absolute path** (full path starting with `C:\`)

### "Permission denied"
- Check service account has **"Storage Admin"** role
- Verify you're using the correct project ID

### "File not found"
- Check the JSON file exists at the path
- Use forward slashes or escape spaces in path
