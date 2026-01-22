# Google Cloud Storage Quick Start Guide

## Step 1: Create Google Cloud Account (5 minutes)

1. Go to: https://cloud.google.com/
2. Click "Get started for free"
3. Sign in with Google account
4. Enter payment info (required, but won't charge if you monitor usage)
5. **You get $300 free credits for 90 days!**

## Step 2: Create a Project

1. Go to: https://console.cloud.google.com/
2. Click project dropdown → "New Project"
3. Project name: `ecg-competition`
4. Click "Create"

## Step 3: Set Up Billing Alerts (CRITICAL!)

**Do this immediately to avoid surprise charges:**

1. Go to: https://console.cloud.google.com/billing
2. Select your billing account
3. Click "Budgets & alerts" → "Create budget"
4. Set:
   - Budget amount: $5
   - Alert threshold: 50%, 90%, 100%
   - Email: your email
5. Click "Create"

## Step 4: Enable APIs

```bash
# Install gcloud CLI first: https://cloud.google.com/sdk/docs/install

gcloud services enable storage-api.googleapis.com
gcloud services enable storage-component.googleapis.com
```

Or via Console:
1. Go to: APIs & Services → Library
2. Search "Cloud Storage API" → Enable
3. Search "Cloud Storage JSON API" → Enable

## Step 5: Create Service Account

1. Go to: IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name: `kaggle-gcs-transfer`
4. Grant role: **Storage Admin**
5. Click "Create and Continue" → "Done"
6. Click on service account → "Keys" → "Add Key" → "Create new key"
7. Choose **JSON** → Download as `service-account-key.json`

## Step 6: Install Google Cloud SDK

**Windows:**
```bash
# Download installer from: https://cloud.google.com/sdk/docs/install
# Or use pip:
pip install google-cloud-storage
```

## Step 7: Authenticate

```bash
# Option 1: Use service account key (recommended)
set GOOGLE_APPLICATION_CREDENTIALS=path\to\service-account-key.json

# Option 2: Use gcloud auth
gcloud auth login
gcloud auth application-default login
```

## Step 8: Create Multiple GCS Buckets

```bash
# Run the bucket creation script
python scripts/create_multiple_gcs_buckets.py

# This creates:
# - ecg-competition-data-1
# - ecg-competition-data-2
# - ecg-competition-data-3
# - ecg-competition-data-4
# - ecg-competition-data-5
```

**Or manually:**
```bash
gsutil mb -p ecg-competition -c STANDARD -l us-central1 gs://ecg-competition-data-1
gsutil mb -p ecg-competition -c STANDARD -l us-central1 gs://ecg-competition-data-2
gsutil mb -p ecg-competition -c STANDARD -l us-central1 gs://ecg-competition-data-3
gsutil mb -p ecg-competition -c STANDARD -l us-central1 gs://ecg-competition-data-4
gsutil mb -p ecg-competition -c STANDARD -l us-central1 gs://ecg-competition-data-5
```

## Step 9: Verify Setup

```bash
# List buckets
gsutil ls

# Or using Python
python -c "from google.cloud import storage; print([b.name for b in storage.Client().list_buckets()])"
```

## Step 10: Run Transfer

```bash
# Transfer images to GCS (distributed across buckets)
python scripts/kaggle_to_gcs_transfer.py
```

## Step 11: Import to Firestore

```bash
# Import manifest to Firestore for viewer
python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json
```

## Cost Monitoring

### Check Current Usage:
1. Go to: https://console.cloud.google.com/billing
2. Click "Reports" to see current charges
3. Click "Cost breakdown" for details

### Expected Costs (85GB data):

**Storage Costs:**
- First 5GB: **FREE** (free tier)
- Next 80GB in Standard: $1.60/month
- **OR** Next 80GB in Archive: $0.10/month ⭐ (recommended)

**With $300 free credits:**
- At $0.10/month = **3,000 months** (250 years!)
- You'll use less than $1 of credits

## Cost-Saving Tips

1. **Use Archive storage** for competition data (94% cheaper)
2. **Enable lifecycle policies** (auto-move to Archive)
3. **Monitor billing alerts** (set at $5, $10, $25)
4. **Use us-central1 region** (cheapest)
5. **Delete incomplete uploads** (lifecycle policy does this)

## Troubleshooting

### "Access Denied" error
- Check service account has Storage Admin role
- Verify credentials: `echo %GOOGLE_APPLICATION_CREDENTIALS%`

### "Bucket already exists"
- Bucket names are globally unique
- Try different bucket names or add random suffix

### "Project not found"
- Update PROJECT_ID in `create_multiple_gcs_buckets.py`
- Or set: `gcloud config set project ecg-competition`

## Integration with Firebase

**Good News**: Firebase Storage uses GCS under the hood!

- Your Firebase project can access GCS buckets
- You can use GCS buckets directly from Firebase Functions
- Or use Firebase Storage (which uses GCS)

## Next Steps

After setup:
1. ✅ GCP account created
2. ✅ Billing alerts configured
3. ✅ Service account created
4. ✅ Buckets created
5. ✅ Transfer script ready
6. → Run transfer: `python scripts/kaggle_to_gcs_transfer.py`
7. → Import manifest: `python scripts/import_gcs_manifest_to_firestore.py`
