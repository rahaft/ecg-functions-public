# Deploy Training Viewer to Firebase

## What We Created

A new training data viewer page (`public/training_viewer.html`) that allows you to:

1. **Import from Kaggle** - Fetch training images directly from Kaggle competition
2. **View Image List** - Browse all imported images with thumbnails
3. **Compare Predictions vs Ground Truth** - Side-by-side comparison
4. **Navigate Between Images** - Easy navigation through training set
5. **View Metrics** - SNR, grid scores, accuracy comparisons

## Deploy to Firebase

```bash
firebase deploy --only hosting
```

## Access After Deployment

Visit: **https://hv-ecg.web.app/training_viewer.html**

## Features

### Image Import
- Direct Kaggle API integration (requires backend)
- Competition name: `physionet-ecg-image-digitization`
- Select subset: Train, Test, or All

### Comparison View
- **Left Panel**: Algorithm prediction with detected grid lines
- **Right Panel**: Ground truth / accurate values
- **Metrics Display**: 
  - SNR comparison
  - Grid score comparison
  - Accuracy calculation
  - Line count (horizontal/vertical)

### Navigation
- Click any image card to open comparison view
- Previous/Next buttons to navigate through dataset
- Image counter showing position (e.g., "Image 5 of 100")

## Backend Integration Needed

For full functionality, you need to:

1. **Deploy Kaggle API endpoint** in Firebase Functions
2. **Connect to Python pipeline** for image processing
3. **Load ground truth data** from competition dataset

### Quick Start (Without Full Backend)

For now, the page structure is ready. You can:

1. **Deploy the page**: `firebase deploy --only hosting`
2. **Test the interface**: Visit `https://hv-ecg.web.app/training_viewer.html`
3. **Add backend later**: Integrate Kaggle API and processing pipeline

## Next Steps

1. Deploy the page: `firebase deploy --only hosting`
2. Test the interface on the live site
3. Integrate backend endpoints for Kaggle API
4. Connect Python pipeline for image processing
