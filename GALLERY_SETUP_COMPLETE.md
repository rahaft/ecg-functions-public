# Gallery Setup - Complete Guide

## ✅ Gallery is Updated!

The gallery now:
- ✅ Loads from GCS manifest (not Firebase Storage)
- ✅ Groups images by prefix (before `-`) or folder (test/train)
- ✅ Shows group headers with counts
- ✅ Supports parallel testing (up to 10 images)
- ✅ Supports group-specific testing

---

## 🚀 Get It Working (3 Steps)

### Step 1: Convert Manifest

```powershell
python scripts/convert_manifest_for_gallery.py
```

This converts your existing `image_manifest_gcs.json` (8,795 images) to gallery format.

### Step 2: Copy to Public

```powershell
copy gcs_images_manifest.json public\gcs_images_manifest.json
```

### Step 3: Deploy

```powershell
firebase deploy --only hosting
```

---

## 🎨 Gallery Features

### Image Grouping

Images are grouped by:
1. **Prefix before `-`** (if filename has `-`)
2. **Folder name** (test/train) if no `-`
3. **Filename prefix** as fallback

### Group Display

Each group shows:
- **Header** with icon (📚 Train, 🧪 Test, 📁 Other)
- **Group name** (folder or prefix)
- **Image count** in group
- **All images** in grid below

### Testing Functions

#### Test All (up to 10 images):
```javascript
quickBulkTest()
```

#### Test Specific Group:
```javascript
// Test all images in 'test' group
testGroup('test')

// Test all images in 'train' group  
testGroup('train')

// Test by prefix (if images have prefix-xxx format)
testGroup('1006427285')
```

#### Test with Options:
```javascript
bulkTestGallery({
    edge_detection: true,
    color_separation: true,
    grid_detection: true,
    quality_check: true,
    crop_to_content: false,
    color_method: 'lab'
}, 'test')  // Optional: group key
```

---

## 📋 Console Functions Available

- `quickBulkTest()` - Test first 10 images
- `bulkTestGallery(options, groupKey)` - Test with options
- `testGroup(groupKey, options)` - Test specific group
- `processBatch(images, options)` - Process image array
- `detectEdges(imgElement, method, crop)` - Single image edge detection

---

## 🔍 Verify Setup

### Check Manifest:
```powershell
Test-Path public\gcs_images_manifest.json
```

### Check Buckets Public:
```powershell
python scripts/make_buckets_public.py
```

### Check CORS:
```powershell
python scripts/configure_gcs_cors.py
```

---

## 🎯 Expected Result

After deployment, visit: **https://hv-ecg.web.app/gallery.html**

You should see:
- ✅ Group headers (📚 Train, 🧪 Test)
- ✅ Image counts per group
- ✅ All 8,795 images displayed
- ✅ Click images to view full size
- ✅ Console functions work for testing

---

**Run the 3 steps above and your gallery will work!** 🚀
