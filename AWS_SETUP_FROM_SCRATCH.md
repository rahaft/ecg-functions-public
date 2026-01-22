# AWS Setup from Scratch - Multiple S3 Buckets Guide

## AWS Free Tier Limits (Per Account)

**Important**: AWS free tier is **5GB TOTAL** per account, not per bucket!

- **5 GB** of Standard Storage
- **20,000 GET** requests per month
- **2,000 PUT** requests per month  
- **15 GB** data transfer out per month

**With $100 credits**, you can store much more, but let's optimize!

## Strategy: Multiple Buckets + Cost Optimization

### Option 1: Multiple AWS Accounts (True Free Tier)
- Each account gets 5GB free tier
- 5 accounts = 25GB free
- More setup, but truly free

### Option 2: Single Account with $100 Credits (Recommended)
- Use credits efficiently
- Create multiple buckets for organization
- Monitor costs closely
- Use cost-saving storage classes

## Step-by-Step: AWS Account Setup

### Step 1: Create AWS Account

1. Go to: https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Enter email and choose account name
4. Choose "Personal" account type
5. Enter payment information (required, but won't charge if you stay in free tier)
6. Verify phone number
7. Choose support plan: **Basic (Free)**

### Step 2: Activate Free Tier

1. Go to: https://console.aws.amazon.com/billing/home#/freetier
2. Verify free tier is active
3. Set up billing alerts (important!)

### Step 3: Set Up Billing Alerts

**CRITICAL**: Set up alerts to avoid surprise charges!

1. Go to: https://console.aws.amazon.com/billing/home#/preferences
2. Enable "Receive Billing Alerts"
3. Go to CloudWatch → Alarms → Billing
4. Create alarm:
   - Metric: EstimatedCharges
   - Threshold: $5 (alert at $5)
   - Email: your email

### Step 4: Create IAM User (For Script Access)

**Don't use root credentials!** Create an IAM user:

1. Go to: IAM → Users → Add users
2. Username: `kaggle-s3-transfer`
3. Access type: ✅ Programmatic access
4. Attach policy: `AmazonS3FullAccess` (or create custom policy)
5. **Save credentials**:
   - Access Key ID
   - Secret Access Key
   - Download CSV file

### Step 5: Create Multiple S3 Buckets

We'll create 5 buckets to organize data:

```bash
# Bucket naming convention: ecg-competition-data-{number}
# Region: us-east-1 (cheapest)

aws s3 mb s3://ecg-competition-data-1 --region us-east-1
aws s3 mb s3://ecg-competition-data-2 --region us-east-1
aws s3 mb s3://ecg-competition-data-3 --region us-east-1
aws s3 mb s3://ecg-competition-data-4 --region us-east-1
aws s3 mb s3://ecg-competition-data-5 --region us-east-1
```

**Or via AWS Console:**
1. Go to S3 → Create bucket
2. Bucket name: `ecg-competition-data-1`
3. Region: `us-east-1` (cheapest)
4. Block all public access: ✅ (keep private)
5. Versioning: Disable (saves money)
6. Default encryption: Enable (AES-256, free)
7. Repeat for buckets 2-5

## Cost Optimization Strategies

### 1. Use S3 Intelligent-Tiering (After Free Tier)
- Automatically moves to cheaper storage
- Small monitoring fee, but saves on storage

### 2. Use S3 Standard-IA (Infrequent Access)
- 50% cheaper than Standard
- Good for data accessed < once per month
- $0.0125/GB vs $0.023/GB

### 3. Use S3 Glacier (For Archival)
- $0.004/GB (very cheap!)
- 3-5 hour retrieval time
- Perfect for competition data you rarely access

### 4. Enable Lifecycle Policies
- Move old data to cheaper storage automatically
- Delete incomplete uploads after 7 days

## Cost Estimation (With $100 Credits)

**85GB competition data:**

| Storage Class | Cost/GB/Month | 85GB Cost | Notes |
|--------------|----------------|-----------|-------|
| S3 Standard | $0.023 | $1.96/month | Default |
| S3 Standard-IA | $0.0125 | $1.06/month | 50% cheaper |
| S3 Glacier | $0.004 | $0.34/month | 83% cheaper! |
| **Free Tier** | $0 | $0 | First 5GB free |

**Recommendation**: 
- First 5GB: Free tier
- Next 80GB: Use S3 Glacier = $0.32/month
- **Total: ~$0.32/month = $3.84/year**
- **With $100 credits: ~26 years of storage!**

## Next Steps

1. Follow steps above to create AWS account
2. Set up billing alerts
3. Create IAM user
4. Create 5 S3 buckets
5. Run the transfer script (will be updated to distribute across buckets)
