# Get Gallery Working - Quick Steps

## 🚀 3 Steps to Get Gallery Working

### Step 1: Convert Existing Manifest

You already have `image_manifest_gcs.json` with 8,795 images! Convert it:

```powershell
python scripts/convert_manifest_for_gallery.py
```

This creates `gcs_images_manifest.json` in the correct format.

### Step 2: Copy to Public Folder

```powershell
copy gcs_images_manifest.json public\gcs_images_manifest.json
```

### Step 3: Deploy

```powershell
firebase deploy --only hosting
```

---

## ✅ What the Gallery Will Show

- **Grouped by prefix** (before `-`) or by folder (test/train)
- **Group headers** showing:
  - 📚 Train images
  - 🧪 Test images
  - 📁 Other groups
- **Image count** per group
- **Click to open** images in new tab

---

## 🧪 Testing Functions

### Test All Images (up to 10):
```javascript
quickBulkTest()
```

### Test Specific Group:
```javascript
// Get group key from console or page
testGroup('test')  // Test all images in 'test' group
testGroup('train') // Test all images in 'train' group
```

### Test with Custom Options:
```javascript
bulkTestGallery({
    edge_detection: true,
    color_separation: true,
    grid_detection: true,
    quality_check: true
})
```

---

## 📋 Gallery Features

✅ **Groups images** by prefix (before `-`) or folder  
✅ **Shows group headers** with counts  
✅ **Parallel testing** - up to 10 images at once  
✅ **Group-specific testing** - test individual groups  
✅ **Click to view** - opens image in new tab  

---

## 🔍 If Gallery Still Empty

1. **Check manifest exists:**
   ```powershell
   Test-Path public\gcs_images_manifest.json
   ```

2. **Check browser console** for errors

3. **Verify buckets are public:**
   ```powershell
   python scripts/make_buckets_public.py
   ```

4. **Verify CORS is configured:**
   ```powershell
   python scripts/configure_gcs_cors.py
   ```

---

**After these 3 steps, your gallery will show all 8,795 images grouped by prefix/folder!** 🎉
