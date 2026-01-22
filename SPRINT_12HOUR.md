# 12-Hour Sprint: Enhanced ECG Transformation Pipeline

**Sprint Goal**: Enhance the existing transformation pipeline with improved method selection, consistent Kaggle output generation, and better UI feedback

**Duration**: 12 hours  
**Status**: Planning Phase  
**Date**: January 2026

---

## 🎯 Sprint Objectives

### Critical Goals
1. **✅ Ensure Kaggle output file is consistently generated** (HIGHEST PRIORITY)
2. Improve UI inputs/outputs for each transformation step
3. Add method-specific details and library documentation per stage
4. Make it easy to add new methods to each stage
5. Provide clear feedback on step success/failure

### Current State Assessment

**✅ Already Implemented:**
- Basic transformation UI with dropdowns in `gallery.html`
- Transformer modules in `functions_python/transformers/`:
  - Quality Gates
  - Color Separation (LAB/HSV)
  - Illumination Normalization
  - Multi-Scale Grid Detection
  - FFT Grid Reconstruction
  - Adaptive Processor
  - Low Contrast Rejection
- Test/Production mode toggle capability
- Step-by-step pipeline structure

**⚠️ Needs Improvement:**
- Kaggle output generation reliability
- Method selection UI/details
- Input/output visualization per step
- Library documentation per method
- Success criteria display
- Method addition workflow

---

## 📊 Sprint Breakdown

### Hour 1: Kaggle Output Generator (CRITICAL)

**Priority**: 🔴 MUST COMPLETE FIRST

**Tasks:**
- [ ] Create robust Kaggle CSV generator with validation
- [ ] Implement error handling for missing/incomplete data
- [ ] Add format validation (row count, ID format, value ranges)
- [ ] Create test suite for output generation
- [ ] Document output format requirements

**Deliverables:**
- `functions_python/output/kaggle_csv_generator.py`
- Unit tests for CSV generation
- Validation checks
- Error messages for common failures

**Success Criteria:**
- Can generate valid CSV from any valid 12-lead data
- Handles edge cases (missing leads, partial data)
- Validates format before saving

---

### Hour 2: Enhanced Step 1 - Rotation Correction

**Current State**: Basic rotation detection exists

**Tasks:**
- [ ] Enhance method dropdown with library info
- [ ] Add input/output preview
- [ ] Display metrics (angle, confidence, perpendicularity)
- [ ] Add method comparison visualization
- [ ] Document OpenCV usage

**Methods to Display:**
1. **Hough Transform** (OpenCV `cv2.HoughLinesP`)
   - Library: `opencv-python`
   - Input: Grayscale image
   - Output: Rotation angle, confidence
   - Success: Confidence > 0.7, angle < 15°

2. **Radon Transform** (scikit-image `skimage.transform.radon`)
   - Library: `scikit-image`
   - Input: Grayscale image
   - Output: Dominant angle
   - Success: Clear peak in Radon transform

3. **Projection Profile** (NumPy-based)
   - Library: `numpy`
   - Input: Grayscale image
   - Output: Angle from projection variance
   - Success: Clear minimum in variance

**UI Improvements:**
- Show selected method library in dropdown
- Display input image and rotated output side-by-side
- Show detected angle with visual indicator
- Confidence score display with color coding

**How to Add New Method:**
1. Add method class to `functions_python/transformers/rotation_methods.py`
2. Register in dropdown config
3. Add library to requirements if needed

---

### Hour 3: Enhanced Step 2 - Smudge Detection & Removal

**Current State**: Inpainting method exists

**Tasks:**
- [ ] Enhance method selection UI
- [ ] Add smudge mask visualization
- [ ] Display before/after comparison
- [ ] Show severity metrics
- [ ] Document OpenCV inpainting

**Methods to Display:**
1. **OpenCV Inpainting** (Default) ✅
   - Library: `opencv-python` (`cv2.inpaint`)
   - Method: `cv2.INPAINT_NS` (Navier-Stokes)
   - Input: Image, smudge mask
   - Output: Cleaned image, mask visualization
   - Success: Smudges removed, grid preserved

2. **Morphological Operations**
   - Library: `opencv-python` (`cv2.morphologyEx`)
   - Input: Grayscale image
   - Output: Cleaned image
   - Success: Smudges removed

**UI Improvements:**
- Red overlay showing detected smudges
- Before/after slider comparison
- Severity score (0-100%)
- Method parameters (threshold, inpaint radius)

---

### Hour 4: Enhanced Step 3 - Quality Assessment

**Current State**: Quality gates exist

**Tasks:**
- [ ] Enhance quality gate display
- [ ] Add blur/DPI/resolution metrics
- [ ] Show edge map visualization
- [ ] Display quality report
- [ ] Document metrics calculation

**Methods to Display:**
1. **Laplacian Variance** (Blur Detection)
   - Library: `opencv-python` (`cv2.Laplacian`)
   - Metric: Variance of Laplacian
   - Threshold: > 100 = sharp, < 100 = blurry

2. **Edge Density Analysis**
   - Library: `opencv-python` (`cv2.Canny`)
   - Metric: Edge pixel count
   - Threshold: > 1000 pixels

3. **DPI Estimation**
   - Library: Calculation-based
   - Metric: Estimated dots per inch
   - Threshold: > 150 DPI required

**UI Improvements:**
- Color-coded quality indicators (Green/Yellow/Red)
- Edge map visualization
- Quality report panel
- Recommendations for failures

---

### Hour 5-6: Enhanced Step 4 - Grid Line Detection (CRITICAL)

**Current State**: Multi-scale grid detector exists

**Tasks:**
- [ ] Enhance method selection with details
- [ ] Add chunk visualization
- [ ] Display H/V line detection separately
- [ ] Show intersection points
- [ ] Document detection methods

**Methods to Display:**
1. **Morphological Line Detection** (Default)
   - Library: `opencv-python` (`cv2.morphologyEx`)
   - Kernels: H lines (1×10), V lines (10×1)
   - Input: Processed image
   - Output: H lines list, V lines list
   - Success: 20+ H lines, 30+ V lines

2. **Hough Line Transform**
   - Library: `opencv-python` (`cv2.HoughLinesP`)
   - Input: Edge-detected image
   - Output: Line segments
   - Success: Lines detected, filtered by angle

3. **FFT Grid Reconstruction** (Fallback)
   - Library: `numpy` (`np.fft.fft2`)
   - Input: Image with missing grid
   - Output: Reconstructed grid
   - Success: 40-60% missing grid reconstructed

**UI Improvements:**
- Multi-panel view: Original → Chunks → H Lines → V Lines → Combined
- Color coding: H lines (red), V lines (blue), intersections (green)
- Line count display
- Quality score (0-1)

---

### Hour 7-8: Enhanced Step 5 - ECG Signal Detection

**Current State**: Basic lead detection exists

**Tasks:**
- [ ] Enhance lead detection UI
- [ ] Add bounding box visualization
- [ ] Display lead labels
- [ ] Show signal density maps
- [ ] Document OCR/detection methods

**Methods to Display:**
1. **Template Matching**
   - Library: `opencv-python` (`cv2.matchTemplate`)
   - Input: Image, 3×4 or 4×3 template
   - Output: Lead bounding boxes
   - Success: 12 leads detected

2. **OCR Label Recognition**
   - Library: `pytesseract` (Tesseract OCR)
   - Input: Image regions
   - Output: Lead labels (I, II, III, etc.)
   - Success: Labels matched to leads

3. **Signal Density Analysis**
   - Library: `opencv-python`, `numpy`
   - Input: Image regions
   - Output: Dark region detection
   - Success: Signal regions identified

**UI Improvements:**
- Bounding boxes on image (green rectangles)
- Lead labels displayed
- Signal count per lead
- Interactive lead adjustment (if time permits)

---

### Hour 9: Enhanced Step 6 - Grid Transformation

**Current State**: Polynomial transformer exists

**Tasks:**
- [ ] Enhance transform method display
- [ ] Show RMSE visualization
- [ ] Display ideal vs detected grid overlay
- [ ] Add transformation matrix details
- [ ] Document transformation libraries

**Methods to Display:**
1. **Affine Transform**
   - Library: `opencv-python` (`cv2.getAffineTransform`)
   - Parameters: 6 DOF (rotation, scale, translation, shear)
   - Success: RMSE < 2 pixels

2. **Polynomial Transform**
   - Library: `opencv-python` (`cv2.warpPolynomial`)
   - Order: 3rd order polynomial
   - Success: RMSE < 5 pixels

3. **Perspective Transform (Homography)**
   - Library: `opencv-python` (`cv2.findHomography`)
   - Parameters: 8 DOF
   - Success: Perspective correction applied

**UI Improvements:**
- Overlay comparison (detected vs ideal grid)
- RMSE heatmap
- Transformation parameters display
- Quality score

---

### Hour 10: Enhanced Step 7 - Polynomial Fitting

**Current State**: Polynomial fitter exists

**Tasks:**
- [ ] Enhance polynomial display
- [ ] Show fit equations
- [ ] Display R² scores per line
- [ ] Add polynomial order visualization
- [ ] Document NumPy polyfit usage

**Methods to Display:**
1. **NumPy Polyfit**
   - Library: `numpy` (`np.polyfit`)
   - Orders: 1-4 (linear to quartic)
   - Input: Grid line points
   - Output: Coefficients, R², AIC
   - Success: R² > 0.95

2. **RANSAC Polynomial Fitting**
   - Library: `scikit-learn` (`sklearn.linear_model.RANSACRegressor`)
   - Input: Line points with outliers
   - Output: Robust polynomial fit
   - Success: Outliers removed, good fit

**UI Improvements:**
- Equation overlay on lines
- Color-coded polynomial orders
- R² scores displayed
- Best fit highlighted (green)

---

### Hour 11: Enhanced Step 8 - Signal Extraction

**Current State**: Basic extraction exists

**Tasks:**
- [ ] Enhance extraction method display
- [ ] Show signal comparison
- [ ] Display quality scores per method
- [ ] Add calibration visualization
- [ ] Document extraction libraries

**Methods to Display:**
1. **Column-wise Scanning**
   - Library: `numpy` (array operations)
   - Input: Lead region
   - Output: Signal array
   - Success: 5000 points extracted

2. **Skeletonization + Tracing**
   - Library: `scikit-image` (`skimage.morphology.skeletonize`)
   - Input: Binary signal image
   - Output: Centerline signal
   - Success: Continuous signal extracted

3. **Least-Cost Path (Dijkstra)**
   - Library: `scipy` (`scipy.sparse.csgraph.dijkstra`)
   - Input: Cost map
   - Output: Optimal path
   - Success: Handles broken signals

**UI Improvements:**
- Side-by-side method comparison
- Quality scores (SNR per method)
- Ensemble result display
- Calibration pulse detection overlay

---

### Hour 12: Enhanced Step 9 - Validation & Final Output

**Current State**: Basic validation exists

**Tasks:**
- [ ] Enhance validation display
- [ ] Show all check results
- [ ] Display final quality report
- [ ] Generate Kaggle CSV with validation
- [ ] Create summary visualization

**Validation Checks:**
1. Lead count (must be 12)
2. Points per lead (≥ 4500)
3. Value range (-5 to +5 mV)
4. No NaN values
5. SNR average (> 15 dB)
6. Grid RMSE (< 5 pixels)

**UI Improvements:**
- Check list with pass/fail indicators
- Overall status badge
- Quality report panel
- Download buttons (CSV, JSON, PNG)
- Summary visualization

---

## 📋 Implementation Guidelines

### Method Addition Workflow

To add a new method to any step:

1. **Create Method Class:**
   ```python
   # functions_python/transformers/[step]_methods.py
   class NewMethod:
       def __init__(self):
           self.name = "New Method Name"
           self.library = "opencv-python"  # or numpy, scikit-image, etc.
           self.parameters = {}
       
       def process(self, input_data):
           # Implementation
           return result, metrics
   ```

2. **Register in Step Config:**
   ```python
   # Add to step configuration
   methods = [
       ExistingMethod1(),
       ExistingMethod2(),
       NewMethod(),  # Add here
   ]
   ```

3. **Update UI Config:**
   - Add method to dropdown options
   - Add library documentation
   - Add success criteria

4. **Update Documentation:**
   - Add to steps doc
   - Document library requirements
   - Add usage examples

### Library Requirements Per Step

**Step 1 (Rotation):**
- `opencv-python` (Hough, Radon)
- `scikit-image` (Radon alternative)
- `numpy` (Projection profile)

**Step 2 (Smudge):**
- `opencv-python` (Inpainting, Morphology)

**Step 3 (Quality):**
- `opencv-python` (Laplacian, Canny)

**Step 4 (Grid):**
- `opencv-python` (Morphology, Hough)
- `numpy` (FFT)

**Step 5 (ECG):**
- `opencv-python` (Template matching)
- `pytesseract` (OCR, optional)

**Step 6 (Transform):**
- `opencv-python` (Affine, Polynomial, Homography)

**Step 7 (Polynomial):**
- `numpy` (polyfit)
- `scikit-learn` (RANSAC, optional)

**Step 8 (Extraction):**
- `numpy` (Column scanning)
- `scikit-image` (Skeletonization)
- `scipy` (Dijkstra)

**Step 9 (Validation):**
- `numpy` (Validation calculations)
- `pandas` (CSV generation)

---

## ✅ Success Metrics

### Hour 1 (Kaggle Output)
- [ ] Can generate valid CSV from any valid input
- [ ] Handles all edge cases gracefully
- [ ] Validation catches format errors

### Hour 2-3 (Steps 1-2)
- [ ] Method dropdowns show library info
- [ ] Input/output previews work
- [ ] Metrics displayed correctly

### Hour 4 (Step 3)
- [ ] Quality gates display correctly
- [ ] Color coding works (Green/Yellow/Red)
- [ ] Recommendations shown for failures

### Hour 5-6 (Step 4)
- [ ] Multi-panel visualization works
- [ ] Line detection shows H/V separately
- [ ] Intersection points displayed

### Hour 7-8 (Step 5)
- [ ] Lead bounding boxes displayed
- [ ] Labels shown correctly
- [ ] Signal density maps visible

### Hour 9-10 (Steps 6-7)
- [ ] Grid transformation visualization
- [ ] RMSE displayed
- [ ] Polynomial equations shown

### Hour 11 (Step 8)
- [ ] Method comparison works
- [ ] Quality scores displayed
- [ ] Ensemble result shown

### Hour 12 (Step 9)
- [ ] All validation checks displayed
- [ ] Final report generated
- [ ] Kaggle CSV downloadable

---

## 🚨 Risk Mitigation

**Risk 1: Kaggle output generation fails**
- **Mitigation**: Implement robust error handling, validation checks, fallback mechanisms
- **Priority**: Fix immediately if issues arise

**Risk 2: UI improvements take too long**
- **Mitigation**: Focus on critical visualizations first, add enhancements incrementally

**Risk 3: Method integration issues**
- **Mitigation**: Test each method independently before integration

**Risk 4: Library conflicts**
- **Mitigation**: Document all library versions, test in clean environment

---

## 📝 Notes

- Keep existing UI structure with dropdowns
- Enhance rather than replace current functionality
- Focus on clarity and ease of adding new methods
- Document everything for future developers
- Test thoroughly after each hour

---

**Sprint Leader**: Development Team  
**Review Date**: End of Sprint  
**Next Steps**: Begin Hour 1 - Kaggle Output Generator
