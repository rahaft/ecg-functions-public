# 📸 ECG Image Gallery - User Guide

## 🎯 Quick Access

**Gallery URL:** https://hv-ecg.web.app/gallery.html

## 🔐 Authentication

1. **When you first visit the gallery**, you'll see a sign-in prompt
2. Click **"Sign In"** to authenticate (uses anonymous authentication by default)
3. Once signed in, images will automatically load

## 📋 Features

### Image Grouping
- **Group by Folder**: Images are organized by their folder structure
- **No Grouping**: View all images in a single grid
- Each group shows:
  - Group name (folder name)
  - Number of images in the group
  - Actions: "Test All in Group" and "Select All"

### Image Display
- Each image card shows:
  - Thumbnail preview
  - Filename
  - File size
  - Set indicator (📚 Train or 🧪 Test)
- Click on an image card to select/deselect it
- Selected images are highlighted in green

### Controls
- **Subset Filter**: Filter by All/Train/Test
- **Group By**: Choose how to organize images (Folder or No Grouping)
- **Limit**: Set how many images to load (1-1000)
- **Load Images**: Refresh the gallery with current filters

### Testing Digitization

#### Test Single Image
1. Click the **"Test"** button on any image card
2. The algorithm will process the image
3. Results appear in the test panel below:
   - Quality Score (SNR)
   - Number of leads detected
   - Processing metadata

#### Test Entire Group
1. Click **"Test All in Group"** in a group header
2. All images in that group will be processed sequentially
3. Results for all images appear in the test panel

#### Select Multiple Images
1. Click **"Select"** on individual images, or
2. Click **"Select All"** in a group header
3. Selected count is shown in the stats bar

### Statistics Bar
- **Total Images**: Total number of images loaded
- **Groups**: Number of image groups
- **Selected**: Number of currently selected images

## 🎨 Visual Indicators

- **Green border**: Selected image
- **Blue badge**: Image is currently being processed
- **Hover effect**: Images lift slightly when you hover over them

## 🔧 How It Works

1. **Image Loading**: 
   - Calls `listGCSImages` Firebase function
   - Filters by subset (train/test/all)
   - Groups images by folder structure

2. **Image Display**:
   - Gets signed URLs from `getGCSImageUrl` function
   - Caches URLs for faster loading
   - Shows placeholder while loading

3. **Digitization Testing**:
   - Calls `processGCSImage` Firebase function
   - Processes image through digitization pipeline
   - Displays results with quality metrics

## 🐛 Troubleshooting

### Images don't load
- Check that you're signed in
- Verify Firestore has images in `kaggle_images` collection
- Check browser console (F12) for errors

### Test fails
- Check Firebase Functions logs
- Verify `processGCSImage` function is deployed
- Check that images have `gcs_bucket` and `gcs_path` fields

### Slow loading
- Reduce the limit (try 50 instead of 100)
- Check your internet connection
- Signed URLs are cached, so reloading is faster

## 📝 Next Steps

- **Batch Testing**: Add ability to test all selected images at once
- **Export Results**: Download test results as CSV/JSON
- **Comparison View**: Side-by-side comparison of original vs. digitized
- **Quality Filtering**: Filter images by quality scores
- **Sorting**: Sort images by quality, date, filename, etc.

## 🔗 Related Pages

- **Main App**: https://hv-ecg.web.app
- **Training Viewer**: https://hv-ecg.web.app/training_viewer.html
- **Digitization Test**: https://hv-ecg.web.app/digitization_test.html
