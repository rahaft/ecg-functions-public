# How to Test Transformation Methods

## Quick Start - Testing in the Gallery UI

### Step 1: Open Gallery
1. Go to: **https://hv-ecg.web.app/gallery.html**
2. Wait for images to load (or click "Load Images")

### Step 2: Open Image Comparison
1. Click on any **image card** in the gallery
2. OR click the **"Compare"** button on an image
3. This opens the **Image Comparison Modal**

### Step 3: Access Transform Tab
1. In the modal, you'll see **3 tabs** at the top:
   - **Compare** - Side-by-side comparison
   - **Algorithm** - Polynomial mapping visualization
   - **Transform** - Transformation methods ⭐

2. Click the **"Transform"** tab

### Step 4: Test Transformations

#### Option A: Single Method (Barrel Distortion)
1. Click **"🔍 Detect & Transform"** button
2. This uses the **Barrel Distortion** method
3. You'll see:
   - Original image with detected grid lines (green overlay)
   - Transformed/corrected image
   - Status message with quality metrics

#### Option B: All Methods (Multi-Method Comparison)
1. Click **"🔄 Process All Methods"** button
2. This tests **all 4 methods**:
   - Barrel Distortion
   - Polynomial Transform
   - TPS (Thin Plate Spline)
   - Perspective Transform
3. You'll see:
   - **Method Comparison Cards** - Results from each method
   - **Rankings Table** - Sorted by quality score
   - **Best Method** highlighted with 🏆

### Step 5: View Results

#### Method Comparison Cards
Each card shows:
- Method name
- R² score (fit quality)
- RMSE (root mean square error in pixels)
- Quality rating (excellent/good/fair/poor)
- Processing time

#### Rankings Table
Shows all methods ranked by:
- Combined Score (weighted quality)
- R² value
- RMSE
- Quality rating
- Processing time

### Step 6: Apply Best Transformation
1. Review the rankings
2. Click **"Apply Best Transformation"** to download the corrected image
3. The best method (highest score) is automatically selected

---

## Current Status

### ✅ Working Now
- **UI is fully functional** - All buttons and displays work
- **Barrel Distortion** - Fully implemented (works with fallback detection)
- **Frontend integration** - Ready to display results

### ⏳ Pending Integration
- **Python Service** - Needs to be deployed to Cloud Run
- **Multi-Method Processing** - Currently shows "integration pending"
- **Full Method Results** - Will work once Python service is live

---

## Testing Locally (Python Code)

If you want to test the transformation methods directly in Python:

### Step 1: Install Dependencies
```bash
cd functions_python
pip install -r requirements.txt
```

### Step 2: Test Barrel Transformer
```python
import cv2
import numpy as np
from transformers.barrel_transformer import BarrelTransformer

# Load an ECG image
image = cv2.imread('path/to/ecg_image.png')

# Create transformer
transformer = BarrelTransformer()

# Apply transformation
result = transformer.transform(image)

# View results
print(f"Quality: {result['metrics']['quality']}")
print(f"R²: {result['metrics']['r2']:.3f}")
print(f"RMSE: {result['metrics']['rmse']:.2f} pixels")

# Save transformed image
cv2.imwrite('transformed.png', result['transformed_image'])
```

### Step 3: Test Multi-Method Processor
```python
from transformers.multi_method_processor import MultiMethodProcessor
import cv2

# Load image
image = cv2.imread('path/to/ecg_image.png')

# Process with all methods
processor = MultiMethodProcessor()
results = processor.process_all_methods(image)

# View rankings
print("Method Rankings:")
for i, ranking in enumerate(results['rankings']):
    print(f"{i+1}. {ranking['method']}: Score={ranking['combined_score']:.3f}, "
          f"R²={ranking['r2']:.3f}, RMSE={ranking['rmse']:.2f}")

# Get best result
best = results['best_method']
print(f"\nBest method: {best}")
```

### Step 4: Run Test Script
Create a test file `test_transformations.py`:

```python
import cv2
import sys
from transformers.multi_method_processor import MultiMethodProcessor

if len(sys.argv) < 2:
    print("Usage: python test_transformations.py <image_path>")
    sys.exit(1)

image_path = sys.argv[1]
image = cv2.imread(image_path)

if image is None:
    print(f"Error: Could not load image from {image_path}")
    sys.exit(1)

print(f"Processing {image_path}...")
print(f"Image size: {image.shape[1]}x{image.shape[0]}")

processor = MultiMethodProcessor()
results = processor.process_all_methods(image)

print("\n" + "="*60)
print("TRANSFORMATION RESULTS")
print("="*60)

print(f"\nTotal processing time: {results['total_processing_time']:.2f}s")
print(f"Best method: {results['best_method']}")

print("\nRankings:")
print("-" * 60)
for i, ranking in enumerate(results['rankings']):
    print(f"{i+1}. {ranking['method'].upper():12} | "
          f"Score: {ranking['combined_score']:.3f} | "
          f"R²: {ranking['r2']:.3f} | "
          f"RMSE: {ranking['rmse']:.2f}px | "
          f"Quality: {ranking['quality']}")

# Save best result
if results['best_method']:
    best_result = results['results'][results['best_method']]
    if best_result.get('success'):
        output_path = f"transformed_{results['best_method']}.png"
        cv2.imwrite(output_path, best_result['transformed_image'])
        print(f"\n✅ Saved best transformation to: {output_path}")
```

Run it:
```bash
python test_transformations.py path/to/your/ecg_image.png
```

---

## Testing with Sample Images

### Option 1: Use Gallery Images
1. Images are already in GCS buckets
2. Open any image in the gallery
3. Use the Transform tab

### Option 2: Upload Test Image
1. Go to gallery
2. Upload a test ECG image
3. Open it in comparison modal
4. Test transformations

### Option 3: Use Local Python
1. Download an ECG image from your GCS bucket
2. Run the Python test script above
3. Compare results

---

## Understanding the Results

### Quality Metrics

**R² (R-squared)**
- Range: 0.0 to 1.0
- Higher is better
- Measures how well the transformation fits the ideal grid
- > 0.95 = Excellent
- > 0.90 = Good
- > 0.85 = Fair
- < 0.85 = Poor

**RMSE (Root Mean Square Error)**
- Measured in pixels
- Lower is better
- Average distance error of grid intersections
- < 2px = Excellent
- < 5px = Good
- < 10px = Fair
- > 10px = Poor

**Combined Score**
- Weighted combination of all metrics
- 30% geometric + 70% signal quality
- Range: 0.0 to 1.0
- Higher is better

### Quality Ratings
- **Excellent**: R² > 0.95, RMSE < 2px
- **Good**: R² > 0.90, RMSE < 5px
- **Fair**: R² > 0.85, RMSE < 10px
- **Poor**: Below fair thresholds

---

## Troubleshooting

### "Integration pending" message
- **Cause**: Python service not deployed
- **Solution**: Deploy Python service to Cloud Run (see MULTI_METHOD_SETUP.md)
- **Workaround**: Test locally with Python scripts

### "No transformation available"
- **Cause**: Transformation not run yet
- **Solution**: Click "Detect & Transform" or "Process All Methods" first

### Images not loading
- **Cause**: GCS permissions or CORS
- **Solution**: Check bucket permissions (see FIX_GCS_PERMISSIONS.md)

### Barrel method works but others don't
- **Cause**: Other transformers not fully implemented
- **Status**: 
  - ✅ Barrel - Complete
  - 🚧 Polynomial - Partial (warp pending)
  - ⏳ TPS - Not implemented
  - ⏳ Perspective - Not implemented

---

## Next Steps

1. **Test Barrel Method** - Should work now with fallback detection
2. **Deploy Python Service** - For full multi-method comparison
3. **Complete Other Methods** - Finish polynomial, add TPS and perspective
4. **Compare Results** - See which method works best for your images

---

## Quick Reference

**Gallery URL**: https://hv-ecg.web.app/gallery.html

**Transform Tab Location**: 
1. Open any image
2. Click "Transform" tab in modal
3. Click "Process All Methods"

**Expected Results**:
- Method comparison cards
- Rankings table
- Best method highlighted
- Quality metrics for each method
