# Migrate from Firebase Storage to Google Cloud Storage

## Current Status

### ✅ Already Using GCS
- **Gallery**: Loads images from GCS buckets (`ecg-competition-data-1` through `ecg-competition-data-5`)
- **Python Processing**: Processes images from GCS buckets

### ❌ Still Using Firebase Storage
- **User Uploads** (`public/app.js`): Uploads to Firebase Storage `ecg_images/{userId}/{recordId}/{fileName}`
- **Storage Trigger** (`functions/index.js`): Triggers on Firebase Storage uploads
- **Visualization** (`public/visualization.js`): Fetches images from Firebase Storage

## Migration Plan

### Step 1: Create GCS Bucket for User Data

Create a new GCS bucket for user uploads and processed results:

```bash
# Create bucket
gsutil mb -p hv-ecg -c STANDARD -l us-central1 gs://hv-ecg-user-data

# Set CORS
gsutil cors set gcs-cors.json gs://hv-ecg-user-data

# Set permissions (make readable by authenticated users)
gsutil iam ch allUsers:objectViewer gs://hv-ecg-user-data
```

### Step 2: Update Upload Code

Replace Firebase Storage uploads with GCS uploads using signed URLs or direct upload.

### Step 3: Update Storage Trigger

Change from Firebase Storage trigger to GCS Pub/Sub notification or HTTP trigger.

### Step 4: Update Visualization

Change from Firebase Storage URLs to GCS URLs.

## GCS Bucket Structure

```
gs://hv-ecg-user-data/
├── uploads/
│   └── {userId}/
│       └── {recordId}/
│           └── {fileName}
├── processed/
│   └── {userId}/
│       └── {recordId}/
│           └── {fileName}
└── training/
    └── {datasetId}/
        └── {fileName}
```

## Implementation Options

### Option A: Direct GCS Upload (Recommended)
- Frontend uploads directly to GCS using signed URLs
- Backend generates signed URLs for upload
- No Firebase Storage dependency

### Option B: Backend Proxy Upload
- Frontend uploads to Cloud Function
- Cloud Function uploads to GCS
- More control but adds latency

### Option C: Use Existing GCS Buckets
- Use one of the existing `ecg-competition-data-*` buckets
- Add user uploads to a separate folder
- Simplest but mixes competition data with user data

## Recommended Approach

**Use Option A with a new dedicated bucket:**
1. Create `gs://hv-ecg-user-data` bucket
2. Update upload code to use signed URLs
3. Update storage trigger to use GCS Pub/Sub
4. Update visualization to use GCS URLs
5. Remove Firebase Storage dependencies
