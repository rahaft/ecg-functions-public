# Multi-Method Transformation Implementation Plan

## Overview
Implementing a comprehensive multi-method transformation system for ECG images that applies multiple correction algorithms and automatically selects the best one.

## Current Status

### ✅ Completed
1. **Base Infrastructure**
   - Created `transformers/` module structure
   - Implemented `BaseTransformer` abstract class
   - Created `BarrelTransformer` with full implementation
   - Created `PolynomialTransformer` (partial - needs warp implementation)
   - Created `MultiMethodProcessor` for parallel processing

### 🚧 In Progress
- Grid detection improvements
- Polynomial warp implementation
- TPS transformer
- Perspective transformer

### 📋 Next Steps

## Phase 1: Complete Core Transformers (Priority: HIGH)

### Task 1.1: Complete Polynomial Transformer
- [ ] Implement full polynomial warp mapping
- [ ] Add inverse transformation
- [ ] Test on sample images
- **File**: `functions_python/transformers/polynomial_transformer.py`

### Task 1.2: Implement TPS Transformer
- [ ] Install scikit-image
- [ ] Implement Thin Plate Spline transformation
- [ ] Create source→destination point mapping
- [ ] Apply TPS warp
- **File**: `functions_python/transformers/tps_transformer.py` (NEW)

### Task 1.3: Implement Perspective Transformer
- [ ] Detect ECG paper corners
- [ ] Calculate homography matrix
- [ ] Apply perspective warp
- **File**: `functions_python/transformers/perspective_transformer.py` (NEW)

## Phase 2: Enhanced Grid Detection (Priority: HIGH)

### Task 2.1: Improve Grid Detection
- [ ] Enhance Hough Transform parameters
- [ ] Add projection-based fallback
- [ ] Implement line deduplication
- [ ] Add sub-pixel intersection refinement
- **File**: `functions_python/grid_detection.py` (UPDATE)

### Task 2.2: Calibration Detection
- [ ] Detect 1mV calibration pulse
- [ ] Calculate pixels per mm
- [ ] Calculate pixels per mV
- [ ] Calculate pixels per second
- **File**: `functions_python/calibration_detector.py` (NEW)

## Phase 3: Scoring System (Priority: MEDIUM)

### Task 3.1: Geometric Scorer
- [ ] Grid RMSE calculator
- [ ] Orthogonality score
- [ ] Aspect ratio consistency
- **File**: `functions_python/scorers/geometric_scorer.py` (NEW)

### Task 3.2: Signal Scorer
- [ ] SNR calculation
- [ ] SSIM implementation
- [ ] Waveform smoothness
- [ ] Polynomial fit quality (R²)
- **File**: `functions_python/scorers/signal_scorer.py` (NEW)

### Task 3.3: Combined Scoring
- [ ] Weighted scoring function
- [ ] Normalize all metrics
- [ ] Calculate final combined score
- **File**: `functions_python/scorers/combined_scorer.py` (NEW)

## Phase 4: Integration with Gallery (Priority: HIGH)

### Task 4.1: Update Transform Tab
- [ ] Add method selection dropdown
- [ ] Show all 4 method results
- [ ] Display comparison scores
- [ ] Highlight best method
- **File**: `public/gallery.html` (UPDATE)

### Task 4.2: Cloud Function Integration
- [ ] Create `processMultiMethodTransform` function
- [ ] Call Python service with all methods
- [ ] Return comparison results
- [ ] Store in Firestore
- **File**: `functions/index.js` (UPDATE)

### Task 4.3: Python Service Endpoint
- [ ] Create Flask endpoint for multi-method processing
- [ ] Integrate with MultiMethodProcessor
- [ ] Return JSON with all results
- **File**: `functions_python/main.py` (UPDATE)

## Phase 5: Signal Extraction (Priority: MEDIUM)

### Task 5.1: Column-wise Extraction
- [ ] Extract signal from each column
- [ ] Find darkest pixels
- [ ] Convert to voltage
- **File**: `functions_python/signal_extractor.py` (UPDATE)

### Task 5.2: Skeletonization Method
- [ ] Binarize signal
- [ ] Apply morphological thinning
- [ ] Trace skeleton
- **File**: `functions_python/signal_extractor.py` (UPDATE)

### Task 5.3: Least-Cost Path
- [ ] Create cost matrix
- [ ] Implement Dijkstra's algorithm
- [ ] Find optimal path
- **File**: `functions_python/signal_extractor.py` (UPDATE)

## File Structure Created

```
functions_python/
├── transformers/
│   ├── __init__.py
│   ├── base_transformer.py ✅
│   ├── barrel_transformer.py ✅
│   ├── polynomial_transformer.py 🚧
│   ├── tps_transformer.py ⏳
│   └── perspective_transformer.py ⏳
├── scorers/
│   ├── geometric_scorer.py ⏳
│   ├── signal_scorer.py ⏳
│   └── combined_scorer.py ⏳
└── multi_method_processor.py ✅
```

## Integration Points

### Frontend (gallery.html)
- Transform tab already exists
- Need to add method comparison UI
- Show side-by-side results
- Display quality scores

### Backend (functions/index.js)
- Add `processMultiMethodTransform` Cloud Function
- Call Python service
- Return comparison results

### Python Service (functions_python/)
- MultiMethodProcessor ready
- Need to integrate with Flask API
- Add endpoint for multi-method processing

## Next Immediate Steps

1. **Complete Polynomial Transformer** - Finish warp implementation
2. **Add TPS Transformer** - Implement Thin Plate Spline
3. **Add Perspective Transformer** - Implement homography-based correction
4. **Update Transform Tab UI** - Show all methods and comparison
5. **Create Cloud Function** - Connect frontend to Python service

## Testing Strategy

1. Test each transformer individually
2. Test MultiMethodProcessor with sample images
3. Validate quality scores
4. Test method selection logic
5. End-to-end integration test

## Estimated Timeline

- **Week 1**: Complete all 4 transformers
- **Week 2**: Scoring system and method comparison
- **Week 3**: Frontend integration and testing
- **Week 4**: Signal extraction and optimization
