# Use GCS Buckets for Gallery (No Firebase Storage)

## 🎯 Goal

Display images directly from GCS buckets in the gallery, avoiding Firebase Storage costs.

---

## ✅ Step 1: Make GCS Buckets Public

Images need to be publicly readable:

```powershell
python scripts/make_buckets_public.py
```

This makes all 5 buckets (`ecg-competition-data-1` through `ecg-competition-data-5`) publicly readable.

---

## ✅ Step 2: Configure CORS on GCS Buckets

Allow the website to access images:

```powershell
python scripts/configure_gcs_cors.py
```

This configures CORS to allow requests from:
- `https://hv-ecg.web.app`
- `https://hv-ecg.firebaseapp.com`
- `http://localhost:5000`

---

## ✅ Step 3: Generate Image Manifest

Create a manifest file listing all images:

```powershell
python scripts/list_gcs_images.py
```

This creates `gcs_images_manifest.json` with all image URLs.

---

## ✅ Step 4: Host Manifest File

### Option A: Firebase Hosting (Easiest)

1. Copy `gcs_images_manifest.json` to `public/` folder:
   ```powershell
   copy gcs_images_manifest.json public\gcs_images_manifest.json
   ```

2. Deploy to Firebase Hosting:
   ```powershell
   firebase deploy --only hosting
   ```

3. Manifest will be available at: `https://hv-ecg.web.app/gcs_images_manifest.json`

### Option B: GCS Bucket (Alternative)

Upload manifest to a GCS bucket and make it public:

```powershell
gsutil cp gcs_images_manifest.json gs://ecg-competition-data-1/
gsutil acl ch -u AllUsers:R gs://ecg-competition-data-1/gcs_images_manifest.json
```

Then update `gallery.html` to use the GCS URL.

### Option C: Cloud Function API (Best for Large Datasets)

Create a Cloud Function that lists images dynamically (see `functions/listGCSImages.js` example below).

---

## ✅ Step 5: Update Gallery

The `gallery.html` has been updated to:
- Load from GCS buckets instead of Firebase Storage
- Use the manifest file for fast loading
- Fallback to direct GCS access if manifest unavailable

**No changes needed** - just deploy the updated `gallery.html`:

```powershell
firebase deploy --only hosting
```

---

## 🔄 Refresh Manifest (When New Images Added)

When you transfer new images from Kaggle:

1. **Regenerate manifest:**
   ```powershell
   python scripts/list_gcs_images.py
   ```

2. **Copy to public folder:**
   ```powershell
   copy gcs_images_manifest.json public\gcs_images_manifest.json
   ```

3. **Redeploy:**
   ```powershell
   firebase deploy --only hosting
   ```

---

## 📋 Quick Setup Checklist

- [ ] Run `make_buckets_public.py` - Make buckets publicly readable
- [ ] Run `configure_gcs_cors.py` - Configure CORS
- [ ] Run `list_gcs_images.py` - Generate manifest
- [ ] Copy manifest to `public/` folder
- [ ] Deploy: `firebase deploy --only hosting`
- [ ] Test gallery: https://hv-ecg.web.app/gallery.html

---

## 🚀 Alternative: Cloud Function API (For Dynamic Listing)

If you want the gallery to always show the latest images without regenerating the manifest:

### Create `functions/listGCSImages.js`:

```javascript
const { onRequest } = require('firebase-functions/v2/https');
const { Storage } = require('@google-cloud/storage');

const storage = new Storage({ projectId: 'hv-ecg' });
const BUCKETS = [
  'ecg-competition-data-1',
  'ecg-competition-data-2',
  'ecg-competition-data-3',
  'ecg-competition-data-4',
  'ecg-competition-data-5'
];
const PREFIX = 'kaggle-data/physionet-ecg/';

exports.listGCSImages = onRequest(async (req, res) => {
  res.set('Access-Control-Allow-Origin', '*');
  
  const images = [];
  
  for (const bucketName of BUCKETS) {
    try {
      const bucket = storage.bucket(bucketName);
      const [files] = await bucket.getFiles({ prefix: PREFIX });
      
      for (const file of files) {
        if (/\.(jpg|jpeg|png|tif|tiff|bmp|gif)$/i.test(file.name)) {
          images.push({
            name: file.name.split('/').pop(),
            path: file.name,
            url: `https://storage.googleapis.com/${bucketName}/${file.name}`,
            bucket: bucketName
          });
        }
      }
    } catch (error) {
      console.error(`Error listing ${bucketName}:`, error);
    }
  }
  
  res.json({ images, total: images.length });
});
```

### Deploy Function:

```powershell
firebase deploy --only functions:listGCSImages
```

### Update `gallery.html`:

Change `MANIFEST_URL` to:
```javascript
const MANIFEST_URL = 'https://us-central1-hv-ecg.cloudfunctions.net/listGCSImages';
```

---

## 💰 Cost Benefits

- ✅ **No Firebase Storage costs** - Images stay in GCS
- ✅ **Uses GCS credits** - You mentioned you have GCS credits
- ✅ **No transfer costs** - Images never leave GCS
- ✅ **Public URLs** - Direct access, no signed URLs needed

---

## ⚠️ Important Notes

1. **Public buckets** - Images are publicly accessible (anyone with URL can view)
2. **CORS required** - Must configure CORS for web app access
3. **Manifest updates** - Regenerate manifest when adding new images
4. **Bucket permissions** - Ensure buckets are public for reading

---

**After setup, your gallery will load images directly from GCS buckets!** 🚀
