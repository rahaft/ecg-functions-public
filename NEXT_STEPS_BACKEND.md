# Next Steps: Build Backend for Image Viewing & Digitization Testing

## ✅ What's Complete

1. **Images in GCS**: 8,795 images transferred to 5 buckets ✓
2. **Manifest imported**: Images metadata in Firestore `kaggle_images` collection ✓
3. **Firebase credentials**: Service account key configured ✓

## 🚀 Next: Build Backend Functions

Now we need to build Firebase functions to:
1. **List images** from Firestore
2. **Get signed URLs** for viewing images in GCS
3. **Process images** through digitization pipeline for testing

## 📋 Step 1: Add Firebase Functions

We'll add these to `functions/index.js`:
- `listGCSImages` - Query Firestore for images
- `getGCSImageUrl` - Generate signed URLs for viewing
- `processGCSImage` - Download from GCS, process, return results

## 📋 Step 2: Update Training Viewer

Update `public/training_viewer.html` to:
- Call new Firebase functions
- Display images with signed URLs
- Add "Test Digitization" button for each image
- Show processing results

## 📋 Step 3: Test Digitization

Once functions are ready:
1. Open `training_viewer.html` in browser
2. Select an image
3. Click "Test Digitization"
4. View results (grid lines, signals, quality metrics)

## 🎯 Ready to Build?

Let me know if you want me to:
1. **Add the Firebase functions** now
2. **Update the training viewer** to use them
3. **Create a testing interface** for digitization

Which should we start with?
