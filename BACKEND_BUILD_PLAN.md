# Backend Build Plan - GCS Image Viewer & Digitization Testing

## Current Status
✅ Images transferred to GCS (5 buckets)
✅ Manifest created (image_manifest_gcs.json)
⏳ Need to import manifest to Firestore
⏳ Need backend functions to access GCS images
⏳ Need digitization testing interface

## Components to Build

### 1. Firebase Functions (functions/index.js)
- `listGCSImages` - List images from Firestore `kaggle_images` collection
- `getGCSImageUrl` - Generate signed URLs for GCS images
- `processGCSImage` - Download from GCS, process with digitization pipeline, return results
- `batchProcessImages` - Process multiple images at once

### 2. Frontend Updates (public/training_viewer.html)
- Load images from Firestore
- Display images with GCS signed URLs
- Add "Process" button for each image
- Show digitization results (grid lines, signals, quality metrics)

### 3. Python Integration
- Option A: Call Python Cloud Function/Cloud Run
- Option B: Use Python via HTTP endpoint
- Option C: Process locally for testing (quickest)

## Step-by-Step Implementation

### Step 1: Import Manifest to Firestore
```powershell
python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json
```

### Step 2: Add Firebase Functions
Add to `functions/index.js`:
- Functions to list images from Firestore
- Functions to get GCS signed URLs
- Functions to process images

### Step 3: Update Training Viewer
- Update `training_viewer.html` to use new functions
- Add processing UI
- Display results

### Step 4: Test Digitization
- Select test images
- Process through pipeline
- View results and adjust parameters
