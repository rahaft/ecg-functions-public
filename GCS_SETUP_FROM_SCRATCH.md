# Google Cloud Storage Setup from Scratch

## Google Cloud Free Tier

**Free Tier Includes:**
- **5 GB** of Standard Storage per month
- **5,000 Class A operations** (writes, list buckets)
- **50,000 Class B operations** (reads) per month
- **1 GB** network egress per month

**With $100 credits**, you can store much more!

## Strategy: Multiple Buckets + Cost Optimization

### Option 1: Multiple GCP Projects (True Free Tier)
- Each project gets 5GB free tier
- 5 projects = 25GB free
- More setup, but truly free

### Option 2: Single Project with $100 Credits (Recommended)
- Use credits efficiently
- Create multiple buckets for organization
- Monitor costs closely
- Use cost-saving storage classes

## Step-by-Step: Google Cloud Setup

### Step 1: Create Google Cloud Account

1. Go to: https://cloud.google.com/
2. Click "Get started for free"
3. Sign in with Google account
4. Enter payment information (required, but won't charge if you stay in free tier)
5. Accept terms
6. **You get $300 free credits for 90 days!**

### Step 2: Create a New Project

1. Go to: https://console.cloud.google.com/
2. Click project dropdown → "New Project"
3. Project name: `ecg-competition`
4. Click "Create"
5. Wait for project creation (30 seconds)

### Step 3: Enable Billing Alerts

**CRITICAL**: Set up alerts to avoid surprise charges!

1. Go to: https://console.cloud.google.com/billing
2. Select your billing account
3. Click "Budgets & alerts"
4. Click "Create budget"
5. Set:
   - Budget amount: $5
   - Alert threshold: 50%, 90%, 100%
   - Email notifications: your email
6. Click "Create"

### Step 4: Enable Required APIs

1. Go to: https://console.cloud.google.com/apis/library
2. Enable these APIs:
   - **Cloud Storage API**
   - **Cloud Storage JSON API**
   - **Cloud Resource Manager API**

Or use gcloud CLI:
```bash
gcloud services enable storage-api.googleapis.com
gcloud services enable storage-component.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

### Step 5: Create Service Account (For Script Access)

**Don't use your personal account!** Create a service account:

1. Go to: IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name: `kaggle-gcs-transfer`
4. Description: "For transferring Kaggle data to GCS"
5. Click "Create and Continue"
6. Grant role: **Storage Admin**
7. Click "Continue" → "Done"
8. Click on the service account → "Keys" tab
9. Click "Add Key" → "Create new key"
10. Choose **JSON**
11. **Download the key file** - save as `service-account-key.json`

### Step 6: Install Google Cloud SDK

**Windows:**
1. Download: https://cloud.google.com/sdk/docs/install
2. Run installer
3. Restart terminal

**Or use pip:**
```bash
pip install google-cloud-storage
```

### Step 7: Authenticate

```bash
# Option 1: Use service account key
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"

# Option 2: Use gcloud auth
gcloud auth login
gcloud auth application-default login
```

### Step 8: Create Multiple GCS Buckets

We'll create 5 buckets to organize data:

```bash
# Bucket naming convention: ecg-competition-data-{number}
# Region: us-central1 (cheapest)

gsutil mb -p ecg-competition -c STANDARD -l us-central1 gs://ecg-competition-data-1
gsutil mb -p ecg-competition -c STANDARD -l us-central1 gs://ecg-competition-data-2
gsutil mb -p ecg-competition -c STANDARD -l us-central1 gs://ecg-competition-data-3
gsutil mb -p ecg-competition -c STANDARD -l us-central1 gs://ecg-competition-data-4
gsutil mb -p ecg-competition -c STANDARD -l us-central1 gs://ecg-competition-data-5
```

**Or via Console:**
1. Go to: Cloud Storage → Buckets
2. Click "Create Bucket"
3. Name: `ecg-competition-data-1`
4. Location type: **Region**
5. Region: `us-central1` (Iowa - cheapest)
6. Storage class: **Standard**
7. Access control: **Uniform**
8. Protection: Enable object versioning (optional)
9. Click "Create"
10. Repeat for buckets 2-5

## Cost Optimization Strategies

### 1. Use Nearline Storage (After Free Tier)
- 50% cheaper than Standard
- Good for data accessed < once per month
- $0.010/GB vs $0.020/GB

### 2. Use Coldline Storage
- 70% cheaper than Standard
- Good for data accessed < once per quarter
- $0.004/GB

### 3. Use Archive Storage
- 80% cheaper than Standard
- $0.0012/GB (very cheap!)
- 365 day minimum storage
- Perfect for competition data you rarely access

### 4. Enable Lifecycle Policies
- Move old data to cheaper storage automatically
- Delete incomplete uploads after 7 days

## Cost Estimation (With $100 Credits)

**85GB competition data:**

| Storage Class | Cost/GB/Month | 85GB Cost | Notes |
|--------------|----------------|-----------|-------|
| Standard | $0.020 | $1.70/month | Default |
| Nearline | $0.010 | $0.85/month | 50% cheaper |
| Coldline | $0.004 | $0.34/month | 80% cheaper |
| Archive | $0.0012 | $0.10/month | 94% cheaper! |
| **Free Tier** | $0 | $0 | First 5GB free |

**Recommendation**: 
- First 5GB: Free tier
- Next 80GB: Use Archive = $0.10/month
- **Total: ~$0.10/month = $1.20/year**
- **With $100 credits: ~83 years of storage!**

## Integration with Firebase

**Good News**: Firebase Storage is built on Google Cloud Storage!

- Your Firebase project can access GCS buckets
- You can use GCS buckets directly from Firebase
- Or use Firebase Storage (which uses GCS under the hood)

## Next Steps

1. Follow steps above to create GCP account
2. Set up billing alerts
3. Create service account
4. Create 5 GCS buckets
5. Run the transfer script (will be updated to use GCS)
