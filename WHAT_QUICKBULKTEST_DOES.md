# What `quickBulkTest()` Tests

## 🎯 Overview

`quickBulkTest()` is a **bulk testing function** that processes up to **10 ECG images in parallel** to test the image processing pipeline.

---

## 📋 What It Tests

When you run `quickBulkTest()` in the browser console, it:

1. **Finds all images** in the gallery (up to 10)
2. **Sends them to the Python service** (`/process-batch` endpoint)
3. **Runs 4 processing steps** on each image:
   - ✅ Edge Detection
   - ✅ Color Separation
   - ✅ Grid Detection
   - ✅ Quality Check

---

## 🔬 Detailed Processing Steps

### Step 1: Edge Detection ✅
**What it does:**
- Detects edges in the ECG image using **Canny edge detection**
- Finds the bounding box of the ECG content
- Counts edge pixels

**Returns:**
```javascript
{
  bounding_box: { x, y, width, height },
  edge_pixels: 12345  // Number of edge pixels found
}
```

**Purpose:** Identifies where the ECG content is located in the image

---

### Step 2: Color Separation ✅
**What it does:**
- Separates the ECG trace (signal) from the grid background
- Uses **LAB color space** by default (or HSV if specified)
- Creates two masks:
  - `trace`: The ECG signal lines
  - `grid_mask`: The grid lines

**Returns:**
```javascript
{
  method: 'lab',  // or 'hsv'
  trace_pixels: 5678,  // Pixels in ECG trace
  grid_pixels: 8901    // Pixels in grid
}
```

**Purpose:** Isolates the actual ECG signal from the background grid

---

### Step 3: Grid Detection ✅
**What it does:**
- Detects ECG grid lines (1mm and 5mm squares)
- Uses **Multi-Scale Grid Detector**
- Counts fine lines (1mm) and bold lines (5mm)

**Returns:**
```javascript
{
  fine_lines: 50,   // 1mm grid lines detected
  bold_lines: 10    // 5mm grid lines detected
}
```

**Purpose:** Identifies the calibration grid for scaling measurements

---

### Step 4: Quality Check ✅
**What it does:**
- Runs **Quality Gates** checks:
  - **Blur score**: How sharp the image is (0-1, higher is better)
  - **DPI estimation**: Image resolution
  - **Contrast score**: Image contrast quality
- Determines if image passes quality thresholds

**Returns:**
```javascript
{
  passed: true,
  blur_score: 0.85,      // 0-1, higher = sharper
  dpi_estimate: 300,     // Estimated DPI
  contrast_score: 0.92   // 0-1, higher = better contrast
}
```

**Purpose:** Validates image quality before processing

---

## 📊 Complete Result Structure

When `quickBulkTest()` completes, you get:

```javascript
{
  success: true,
  count: 10,  // Number of images processed
  results: [
    {
      index: 0,
      success: true,
      steps: {
        edge_detection: {
          bounding_box: { x: 10, y: 20, width: 800, height: 600 },
          edge_pixels: 12345
        },
        color_separation: {
          method: 'lab',
          trace_pixels: 5678,
          grid_pixels: 8901
        },
        grid_detection: {
          fine_lines: 50,
          bold_lines: 10
        },
        quality_check: {
          passed: true,
          blur_score: 0.85,
          dpi_estimate: 300,
          contrast_score: 0.92
        }
      }
    },
    // ... more results for other images
  ]
}
```

---

## 🎯 Why Test This?

### 1. **Validate Processing Pipeline**
- Ensures all transformers work correctly
- Checks if images can be processed
- Identifies any errors in the pipeline

### 2. **Performance Testing**
- Tests parallel processing (up to 10 images)
- Measures processing speed
- Identifies bottlenecks

### 3. **Quality Assessment**
- Checks if images meet quality standards
- Identifies low-quality images
- Helps filter out unusable images

### 4. **Debugging**
- Shows which step fails (if any)
- Provides detailed metrics for each image
- Helps identify processing issues

---

## 🚀 How to Use

### Basic Test
```javascript
// In browser console (F12)
quickBulkTest();
```

### Custom Test
```javascript
// Test with specific options
bulkTestGallery({
    edge_detection: true,
    color_separation: true,
    grid_detection: false,  // Skip grid detection
    quality_check: true,
    crop_to_content: true,  // Crop to content area
    color_method: 'hsv'     // Use HSV instead of LAB
});
```

### Wait for Images First
```javascript
// Wait 3 seconds for images to load, then test
setTimeout(() => {
    quickBulkTest();
}, 3000);
```

---

## 📈 What Success Looks Like

**Console Output:**
```
Processing 10 images...
{success: true, count: 10, results: [...]}
```

**Each result should have:**
- ✅ `success: true`
- ✅ All 4 steps completed
- ✅ Quality check passed
- ✅ Metrics within expected ranges

---

## ⚠️ Common Issues

### "No valid images found"
- **Cause:** Images haven't loaded yet
- **Solution:** Wait a few seconds, then try again

### CORS Errors
- **Cause:** Python service not accessible
- **Solution:** Check service is running at Cloud Run URL

### Processing Fails
- **Cause:** Image format issue or processing error
- **Solution:** Check console for specific error message

---

## 🎯 Summary

**`quickBulkTest()` tests:**
1. ✅ Edge detection (finds ECG content boundaries)
2. ✅ Color separation (isolates signal from grid)
3. ✅ Grid detection (identifies calibration grid)
4. ✅ Quality check (validates image quality)

**On:** Up to 10 images in parallel

**Purpose:** Validate the entire ECG image processing pipeline works correctly

---

**This is your main testing tool for the ECG processing pipeline!** 🎉
