# How to View the Gallery and Test ECG Digitization

## 🎯 Quick Access

Your application is now live at: **https://hv-ecg.web.app**

## 📸 Viewing the Image Gallery

1. **Go to the Training Viewer:**
   - Visit: https://hv-ecg.web.app/training_viewer.html
   - Or click "Training Viewer" from the main page

2. **Load Images from Firestore:**
   - Click the **"Load from Firestore"** button
   - This will load images from your `kaggle_images` collection in Firestore
   - Images are loaded from Google Cloud Storage (GCS) via signed URLs

3. **Filter Images:**
   - Use the **"Set"** dropdown to filter by:
     - **All**: Show all images
     - **Train**: Show only training set images
     - **Test**: Show only test set images
   - Use the **"Folder"** dropdown to filter by folder structure

4. **View Image Details:**
   - Click on any image card to see it in detail
   - The comparison view shows:
     - The original ECG image
     - Metadata (filename, size, folder, etc.)

## 🧪 Testing the Digitization Algorithm

### Option 1: From Training Viewer
1. In the Training Viewer, click on an image card
2. Click the **"Test Digitization"** button on the image card
3. The algorithm will process the image and show results

### Option 2: Dedicated Test Page
1. **Go to the Digitization Test Page:**
   - Visit: https://hv-ecg.web.app/digitization_test.html
   - Or click "Test Digitization" from the main page

2. **Load Images:**
   - Select a subset (Train/Test/All) from the dropdown
   - Set a limit (default: 50 images)
   - Click **"Load Images"**

3. **Select Images to Test:**
   - Click on image cards to select them (they'll turn green)
   - You can select multiple images for batch testing

4. **Run Digitization:**
   - Click **"Test Selected Images"** button
   - The algorithm will process each selected image
   - Results will show:
     - Quality metrics (SNR, etc.)
     - Signal visualization
     - Processing metadata

## 🔧 How It Works

### Backend Functions (Deployed)
- **`listGCSImages`**: Lists images from Firestore `kaggle_images` collection
- **`getGCSImageUrl`**: Generates signed URLs for GCS images (secure, temporary access)
- **`processGCSImage`**: Processes images through the digitization pipeline

### Data Flow
1. Images are stored in Google Cloud Storage buckets
2. Metadata is stored in Firestore (`kaggle_images` collection)
3. Frontend calls Firebase Functions to:
   - List images (with filters)
   - Get secure signed URLs for viewing
   - Process images through the digitization algorithm

## 🐛 Troubleshooting

### If images don't load:
1. **Check Firestore:**
   - Go to Firebase Console → Firestore
   - Verify `kaggle_images` collection exists
   - Check that documents have `gcs_bucket` and `gcs_path` fields

2. **Check Functions:**
   - Go to Firebase Console → Functions
   - Verify `listGCSImages`, `getGCSImageUrl`, and `processGCSImage` are deployed
   - Check function logs for errors

3. **Check Authentication:**
   - Make sure you're signed in (anonymous or Google)
   - Some functions may require authentication

### If digitization fails:
- Check the browser console (F12) for error messages
- Check Firebase Functions logs in the console
- The `processGCSImage` function currently returns mock data - you'll need to integrate the actual Python pipeline

## 📝 Next Steps

1. **Integrate Real Pipeline:**
   - The `processGCSImage` function currently uses mock data
   - You'll need to integrate your Python digitization pipeline
   - Options:
     - Call a Cloud Run service
     - Use a separate Python Cloud Function
     - Use inline processing (if Node.js can handle it)

2. **Add More Features:**
   - Side-by-side comparison with ground truth
   - Export results
   - Batch processing with progress tracking
   - Quality filtering and sorting

## 🔗 Useful Links

- **Main App**: https://hv-ecg.web.app
- **Training Viewer**: https://hv-ecg.web.app/training_viewer.html
- **Digitization Test**: https://hv-ecg.web.app/digitization_test.html
- **Firebase Console**: https://console.firebase.google.com/project/hv-ecg/overview
