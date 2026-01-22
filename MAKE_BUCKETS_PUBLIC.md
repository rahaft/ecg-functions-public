# Quick Fix: Make GCS Buckets Public

The fastest way to fix the image loading issue is to make your GCS buckets public for reading. This eliminates the need for signed URLs and IAM permissions.

## Your Buckets (from console logs):
- `ecg-competition-data-1`
- `ecg-competition-data-2`
- `ecg-competition-data-3`
- `ecg-competition-data-4`
- `ecg-competition-data-5`

## Option 1: Using Google Cloud Console (Manual)

1. **Go to Google Cloud Storage Console:**
   https://console.cloud.google.com/storage/browser?project=hv-ecg

2. **For each bucket listed above:**
   - Click on the bucket name
   - Go to the **"Permissions"** tab
   - Click **"ADD PRINCIPAL"**
   - In "New principals", enter: `allUsers`
   - Select role: **"Storage Object Viewer"**
   - Click **"SAVE"**
   - Confirm the warning about making the bucket public

3. **Repeat for all 5 buckets**

## Option 2: Using Python Script (Automated)

Run the provided script:
```bash
python scripts/make_buckets_public.py
```

Make sure you have:
- Google Cloud SDK installed
- Authenticated with: `gcloud auth application-default login`
- Or set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

## After Making Buckets Public:

The gallery will automatically use public URLs (format: `https://storage.googleapis.com/BUCKET_NAME/PATH`) instead of trying to generate signed URLs. No code changes needed - the gallery already tries public URLs first!

## Security Note:

Making buckets public means anyone with the URL can access the images. For a public gallery, this is usually fine. If you need private images, you'll need to fix the IAM permissions instead (see `FIX_GCS_PERMISSIONS.md`).
