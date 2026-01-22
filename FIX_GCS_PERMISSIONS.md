# Fix GCS Image Loading Permissions

The gallery is experiencing permission errors when loading images from Google Cloud Storage. The Firebase service account needs additional IAM roles to generate signed URLs.

## Error
```
Permission 'iam.serviceAccounts.signBlob' denied on resource
```

## Solution

The Firebase service account needs the **Service Account Token Creator** role to sign URLs for GCS objects.

### Steps to Fix:

1. Go to [Google Cloud Console IAM](https://console.cloud.google.com/iam-admin/iam?project=hv-ecg)

2. Find the Firebase service account (usually named `hv-ecg@appspot.gserviceaccount.com` or `firebase-adminsdk-xxxxx@hv-ecg.iam.gserviceaccount.com`)

3. Click the edit/pencil icon for that service account

4. Click "ADD ANOTHER ROLE"

5. Add the following roles:
   - **Service Account Token Creator** (required for signing URLs)
   - **Storage Object Viewer** (if not already present, for reading GCS objects)

6. Click "SAVE"

### Alternative: Make Buckets Public (Not Recommended for Production)

If you want to skip signed URLs entirely, you can make the GCS buckets public:

1. Go to [GCS Buckets](https://console.cloud.google.com/storage/browser?project=hv-ecg)
2. Select each bucket
3. Go to "Permissions" tab
4. Add "allUsers" with "Storage Object Viewer" role
5. Images will be accessible via public URLs (format: `https://storage.googleapis.com/BUCKET_NAME/PATH`)

### Verify Fix

After adding the roles, wait a few minutes for IAM changes to propagate, then refresh the gallery page. Images should load without permission errors.
