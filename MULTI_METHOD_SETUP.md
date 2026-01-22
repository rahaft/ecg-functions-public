# Multi-Method Transformation System - Setup Guide

## Overview
The multi-method transformation system applies 4 different correction algorithms to ECG images and automatically selects the best one based on quality scores.

## Architecture

### Components

1. **Frontend (gallery.html)**
   - Transform tab with "Process All Methods" button
   - Method comparison UI showing all 4 results
   - Rankings table with quality scores
   - Best method highlighting

2. **Backend Cloud Function (functions/index.js)**
   - `processMultiMethodTransform` - Calls Python service
   - Handles image data transfer
   - Returns comparison results

3. **Python Service (functions_python/)**
   - `transformers/` - Transformation method implementations
   - `multi_method_processor.py` - Orchestrates all methods
   - `main.py` - Flask API endpoint

## Transformation Methods

### 1. Barrel Distortion Correction ✅
- **File**: `transformers/barrel_transformer.py`
- **Status**: Fully implemented
- **Use Case**: Lens distortion, camera artifacts
- **Formula**: `r_corrected = r * (1 + k₁r² + k₂r⁴ + k₃r⁶)`

### 2. Polynomial Transform 🚧
- **File**: `transformers/polynomial_transformer.py`
- **Status**: Partial (needs warp implementation)
- **Use Case**: Smooth distortions, warped paper
- **Method**: 4th degree polynomial fitting

### 3. TPS (Thin Plate Spline) ⏳
- **File**: `transformers/tps_transformer.py` (to be created)
- **Status**: Not implemented
- **Use Case**: Crumpled/warped paper, complex distortions
- **Method**: Point-based warping

### 4. Perspective Transform ⏳
- **File**: `transformers/perspective_transformer.py` (to be created)
- **Status**: Not implemented
- **Use Case**: Angled photos, perspective distortion
- **Method**: Homography matrix

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd functions_python
pip install -r requirements.txt
```

### Step 2: Test Locally

```bash
# Test barrel transformer
python -c "from transformers.barrel_transformer import BarrelTransformer; print('OK')"

# Test multi-method processor
python -c "from transformers.multi_method_processor import MultiMethodProcessor; print('OK')"
```

### Step 3: Deploy Python Service to Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
gcloud run deploy ecg-multi-method \
  --image gcr.io/hv-ecg/ecg-multi-method \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300
```

### Step 4: Update Cloud Function

Set the Python service URL:

```bash
firebase functions:config:set python.multi_method_url="https://ecg-multi-method-XXXXX.run.app"
```

Or update `functions/index.js` directly:

```javascript
const pythonServiceUrl = process.env.PYTHON_MULTI_METHOD_URL || 
                         'https://ecg-multi-method-XXXXX.run.app';
```

### Step 5: Deploy Cloud Functions

```bash
firebase deploy --only functions:processMultiMethodTransform
```

## Usage

### From Gallery UI

1. Open an image in the comparison modal
2. Click the "Transform" tab
3. Click "🔄 Process All Methods"
4. View results:
   - Method comparison cards
   - Rankings table
   - Best method highlighted
5. Click "Apply Best Transformation" to use the selected method

### API Call

```javascript
const result = await processMultiMethodTransform({
  imageData: base64ImageData,
  imageWidth: 1000,
  imageHeight: 800
});

console.log('Best method:', result.best_method);
console.log('Rankings:', result.rankings);
```

## Response Format

```json
{
  "success": true,
  "results": {
    "barrel": {
      "transformed_image_base64": "...",
      "params": { "k1": 0.01, "k2": -0.003, ... },
      "metrics": { "r2": 0.95, "rmse": 2.3, "quality": "excellent" },
      "processing_time": 1.2
    },
    "polynomial": { ... },
    "tps": { ... },
    "perspective": { ... }
  },
  "rankings": [
    {
      "method": "barrel",
      "combined_score": 0.92,
      "r2": 0.95,
      "rmse": 2.3,
      "quality": "excellent"
    },
    ...
  ],
  "best_method": "barrel",
  "total_processing_time": 4.5
}
```

## Next Steps

1. **Complete Polynomial Transformer**
   - Implement full warp mapping
   - Test on sample images

2. **Implement TPS Transformer**
   - Install scikit-image
   - Implement Thin Plate Spline
   - Test on crumpled images

3. **Implement Perspective Transformer**
   - Detect paper corners
   - Calculate homography
   - Test on angled photos

4. **Enhance Scoring System**
   - Add geometric metrics (orthogonality, aspect ratio)
   - Add signal metrics (SNR, SSIM)
   - Improve combined scoring

5. **Integration Testing**
   - Test end-to-end flow
   - Validate method selection
   - Performance optimization

## Troubleshooting

### "Multi-method processor not available"
- Check that `transformers/` module is in Python path
- Verify imports work: `from transformers.multi_method_processor import MultiMethodProcessor`

### "Python service not responding"
- Check Cloud Run service is deployed
- Verify URL is correct in Cloud Function config
- Check Cloud Run logs for errors

### "Timeout errors"
- Increase Cloud Function timeout (max 300s)
- Increase Cloud Run timeout
- Optimize transformer implementations

## Files Created

- `functions_python/transformers/__init__.py`
- `functions_python/transformers/base_transformer.py`
- `functions_python/transformers/barrel_transformer.py`
- `functions_python/transformers/polynomial_transformer.py`
- `functions_python/transformers/multi_method_processor.py`
- `MULTI_METHOD_IMPLEMENTATION.md`
- `MULTI_METHOD_SETUP.md` (this file)

## References

- See `transformation_task_list.md` for full implementation plan
- See `MULTI_METHOD_IMPLEMENTATION.md` for detailed task breakdown
