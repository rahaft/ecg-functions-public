# Kaggle to S3 Direct Transfer + Viewer Setup Guide

## Overview

This guide will help you:
1. Transfer competition images from Kaggle directly to AWS S3 (without downloading locally)
2. Set up an authenticated viewer interface
3. View images with train/test/folder metadata

## Phase 1: Direct Kaggle to S3 Transfer

### Step 1.1: Setup AWS S3 Bucket

```bash
# Create S3 bucket (via AWS Console or CLI)
aws s3 mb s3://ecg-competition-data --region us-east-1

# Or set bucket name in script
export AWS_S3_BUCKET=ecg-competition-data
```

### Step 1.2: Configure AWS Credentials

```bash
# Set AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Step 1.3: Run Kaggle to S3 Transfer Script

The script (`scripts/kaggle_to_s3_transfer.py`) will:
- Get file list from Kaggle
- Stream files directly from Kaggle to S3
- Create manifest with train/test/folder metadata

```bash
# Update bucket name in script
nano scripts/kaggle_to_s3_transfer.py
# Change: S3_BUCKET = "ecg-competition-data"

# Run transfer
python scripts/kaggle_to_s3_transfer.py

# Output: image_manifest.json
```

**Note**: The script uses your Kaggle credentials from `~/.kaggle/kaggle.json` (already configured).

## Phase 2: Import Manifest to Firestore

### Step 2.1: Install Firebase Admin SDK

```bash
pip install firebase-admin
```

### Step 2.2: Get Firebase Service Account Key

1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Save as `serviceAccountKey.json` in project root

### Step 2.3: Import Manifest

```bash
# Import manifest to Firestore
python scripts/import_manifest_to_firestore.py image_manifest.json

# This creates documents in 'kaggle_images' collection
```

**Firestore Structure**:
```
kaggle_images/
  {image_id}/
    - filename: "train/images/001.png"
    - s3_key: "kaggle-data/physionet-ecg/train/images/001.png"
    - s3_url: "s3://bucket/..."
    - is_train: true
    - is_test: false
    - folder: "train/images"
    - size: 1234567
    - competition: "physionet-ecg-image-digitization"
    - ...
```

## Phase 3: Deploy Viewer with Authentication

### Step 3.1: Viewer Features

The training viewer (`public/training_viewer.html`) now includes:

1. **Authentication**: 
   - Sign in button (anonymous or Google)
   - User info display
   - Sign out button

2. **Image List**:
   - Loads from `kaggle_images` collection in Firestore
   - Shows train/test badges
   - Shows folder structure
   - Filter by train/test
   - Filter by folder

3. **Comparison View**:
   - Side-by-side prediction vs ground truth
   - Metrics comparison

### Step 3.2: Deploy

```bash
firebase deploy --only hosting
```

### Step 3.3: Access Viewer

Visit: **https://hv-ecg.web.app/training_viewer.html**

1. **Sign In**: Click "Sign In" button (uses anonymous auth by default)
2. **Import Images**: Click "Import Images from Kaggle" or "Load Local Images"
   - Will load from `kaggle_images` collection if manifest is imported
3. **Filter Images**: Use dropdowns to filter by train/test and folder
4. **View Image**: Click any image card to see comparison view

## Complete Workflow

```
1. Run kaggle_to_s3_transfer.py
   ↓
2. Creates image_manifest.json
   ↓
3. Import manifest to Firestore
   ↓
4. Deploy viewer
   ↓
5. Access viewer and see images with metadata
```

## File Structure

```
scripts/
  ├── kaggle_to_s3_transfer.py      # Transfer script
  └── import_manifest_to_firestore.py # Firestore import
  
public/
  └── training_viewer.html          # Viewer interface (with auth)
  
functions/
  └── index.js                      # Firebase Functions (for future API endpoints)
```

## Features

### ✅ Completed
- [x] Kaggle to S3 transfer script
- [x] Manifest creation with metadata
- [x] Firestore import script
- [x] Authenticated viewer interface
- [x] Train/test/folder filtering
- [x] Image metadata display

### 🚧 In Progress / Future
- [ ] Direct S3 image viewing (needs presigned URLs)
- [ ] Image processing integration
- [ ] Ground truth comparison
- [ ] Batch operations

## Troubleshooting

### Images not showing in viewer
- **Check**: Manifest imported to Firestore?
  ```bash
  python scripts/import_manifest_to_firestore.py image_manifest.json
  ```

### S3 transfer fails
- **Check**: AWS credentials configured?
  ```bash
  aws s3 ls s3://your-bucket/
  ```

### Authentication issues
- **Check**: Firebase Auth enabled in console?
- Try: Anonymous sign-in (should work without setup)

## Next Steps

1. Run the transfer script to move images to S3
2. Import manifest to Firestore
3. Deploy and test viewer
4. Set up S3 presigned URL generation for direct image access
