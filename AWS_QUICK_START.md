# AWS Quick Start Guide - $100 Credits Setup

## Step 1: Create AWS Account (5 minutes)

1. Go to: https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Fill in:
   - Email address
   - Password
   - Account name: "ECG Competition"
4. Choose "Personal" account
5. Enter payment info (required, but won't charge if you monitor usage)
6. Verify phone number
7. Choose support plan: **Basic (Free)**

## Step 2: Set Up Billing Alerts (CRITICAL!)

**Do this immediately to avoid surprise charges:**

1. Go to: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:
2. Click "Create alarm"
3. Select metric: "Billing" → "EstimatedCharges"
4. Set threshold: $5
5. Add email notification
6. Click "Create alarm"

**Also set up:**
- Alert at $10
- Alert at $25
- Alert at $50

## Step 3: Create IAM User (For Scripts)

1. Go to: IAM → Users → Add users
2. Username: `kaggle-s3-transfer`
3. Access type: ✅ Programmatic access
4. Permissions: Attach policy `AmazonS3FullAccess`
5. **IMPORTANT**: Download the CSV file with credentials!

## Step 4: Configure AWS CLI

```bash
# Install AWS CLI (if not installed)
# Windows: Download from https://aws.amazon.com/cli/
# Or: pip install awscli

# Configure
aws configure

# Enter:
# AWS Access Key ID: [from CSV file]
# AWS Secret Access Key: [from CSV file]
# Default region: us-east-1
# Default output: json
```

## Step 5: Create Multiple S3 Buckets

```bash
# Run the bucket creation script
python scripts/create_multiple_s3_buckets.py

# This creates:
# - ecg-competition-data-1
# - ecg-competition-data-2
# - ecg-competition-data-3
# - ecg-competition-data-4
# - ecg-competition-data-5
```

## Step 6: Verify Setup

```bash
# List buckets
aws s3 ls

# Should see your 5 buckets
```

## Step 7: Run Transfer

```bash
# Transfer images to S3 (distributed across buckets)
python scripts/kaggle_to_s3_multi_bucket.py
```

## Cost Monitoring

### Check Current Usage:
1. Go to: https://console.aws.amazon.com/billing/home
2. Click "Bills" to see current charges
3. Click "Cost Explorer" for detailed breakdown

### Expected Costs (85GB data):

**Storage Costs:**
- First 5GB: **FREE** (free tier)
- Next 80GB in S3 Standard: $1.84/month
- **OR** Next 80GB in S3 Glacier: $0.32/month ⭐ (recommended)

**With $100 credits:**
- At $0.32/month = **312 months** (26 years!)
- You'll use less than $1 of credits

## Cost-Saving Tips

1. **Use S3 Glacier** for archival data (83% cheaper)
2. **Enable lifecycle policies** (auto-move to Glacier)
3. **Monitor billing alerts** (set at $5, $10, $25)
4. **Delete incomplete uploads** (lifecycle policy does this)
5. **Use us-east-1 region** (cheapest)

## Troubleshooting

### "Access Denied" error
- Check IAM user has S3 permissions
- Verify AWS credentials: `aws s3 ls`

### "Bucket already exists"
- Bucket names are globally unique
- Try different bucket names or add random suffix

### "Insufficient permissions"
- Attach `AmazonS3FullAccess` policy to IAM user
- Or create custom policy with S3 permissions

## Next Steps

After setup:
1. ✅ AWS account created
2. ✅ Billing alerts configured
3. ✅ IAM user created
4. ✅ Buckets created
5. ✅ Transfer script ready
6. → Run transfer: `python scripts/kaggle_to_s3_multi_bucket.py`
