# 12-Hour Sprint: ECG Digitization Pipeline Implementation

**Sprint Date:** [Date TBD]  
**Duration:** 12 hours  
**Goal:** Complete working end-to-end pipeline with consistent Kaggle output generation

---

## 🎯 Sprint Objectives

### Primary Goal
**Most Critical:** Ensure Kaggle output file is consistently generated with correct format for every successful pipeline run.

### Secondary Goals
1. Enhance existing transformation UI with improved inputs/outputs visibility
2. Add method-specific details for each transformation stage
3. Make it easy to add new methods to each stage
4. Improve step-by-step feedback and status reporting

---

## 📊 Current System Status

### ✅ Already Implemented

1. **UI Infrastructure**
   - Gallery page with transformation interface (`public/gallery.html`)
   - Dropdown-based step navigation (Test Mode)
   - Image comparison views
   - Step status indicators (✅ Completed, 🔄 In Progress, ⏳ Pending, ❌ Failed)

2. **Transformer Modules** (`functions_python/transformers/`)
   - ✅ `quality_gates.py` - Pre-flight quality checks
   - ✅ `color_separation.py` - LAB/HSV color space separation
   - ✅ `illumination_normalization.py` - CLAHE, background subtraction
   - ✅ `multi_scale_grid_detector.py` - 1mm and 5mm grid detection
   - ✅ `fft_grid_reconstruction.py` - Reconstruct missing grids
   - ✅ `adaptive_processor.py` - 3-tier fallback pipeline
   - ✅ `low_contrast_rejection.py` - Final quality check
   - ✅ `base_transformer.py` - Base class for all transformers

3. **Backend Infrastructure**
   - Firebase Functions for processing triggers
   - Python pipeline structure (`functions_python/digitization_pipeline.py`)
   - Visualization UI (`public/visualization.html`)

### ❌ Not Yet Implemented

1. **Kaggle Output Generator** ⚠️ CRITICAL
   - CSV formatter for competition submission
   - Validation checks
   - Consistent generation regardless of pipeline path

2. **Full Pipeline Integration**
   - Step 0: Kaggle output (missing)
   - Steps 1-9: Need to be connected end-to-end
   - Method selection and switching
   - Checkpoint saving/loading

3. **Enhanced UI Features**
   - Method-specific input/output displays
   - Real-time status updates for each method
   - Library/OpenCV version indicators
   - Easy method addition interface

---

## 🏗️ Sprint Architecture

### Pipeline Steps (Aligned with PRD)

```
0. Kaggle Output Generator (CRITICAL - MUST WORK)
   ↓
1. Quality Gates (Pre-processing check)
   ↓
2. Color Space Separation
   ↓
3. Illumination Normalization
   ↓
4. Rotation Correction
   ↓
5. Smudge Detection & Removal
   ↓
6. Multi-Scale Grid Detection
   ↓
7. FFT Grid Reconstruction (if needed)
   ↓
8. Grid Transformation
   ↓
9. ECG Signal Detection
   ↓
10. Signal Extraction & Calibration
   ↓
11. Validation & Final Output
   ↓
12. Kaggle CSV Generation (ALWAYS RUNS)
```

---

## ⏱️ Hour-by-Hour Breakdown

### **HOUR 1: Kaggle Output Generator + Base Infrastructure** 🔴 CRITICAL

**Priority:** MUST COMPLETE FIRST

**Tasks:**
1. Create `functions_python/transformers/step0_kaggle_output.py`
   - CSV formatter with proper format: `id,value`
   - Row generation: `record_{recordId}_{lead}_{index}`
   - Validation: 60,000 rows per ECG (12 leads × 5000 points)
   
2. Integrate with existing pipeline
   - Ensure it runs after signal extraction
   - Create fallback even if pipeline fails partially
   - Add to UI as final step indicator

3. Test with mock data
   - Generate sample CSV
   - Validate format matches Kaggle requirements
   - Test with incomplete data (handle gracefully)

**Success Criteria:**
- ✅ Can generate valid Kaggle CSV from any 12-lead signal data
- ✅ Format validation passes
- ✅ File is downloadable from UI

**Deliverable:** Working Kaggle CSV generator that ALWAYS produces output

---

### **HOUR 2: Step Integration & Method Framework**

**Tasks:**
1. Create unified step execution framework
   - Base step class enhancement
   - Method registry system
   - Result comparison and selection

2. Connect existing transformers to pipeline
   - Map transformers to steps
   - Create step wrappers
   - Add method selection logic

3. Update UI to show current methods
   - Method dropdown per step
   - Library indicators (OpenCV, scikit-image, etc.)
   - Method-specific parameters

**Success Criteria:**
- ✅ All existing transformers accessible via UI
- ✅ Can switch methods per step
- ✅ Method names and libraries visible

---

### **HOUR 3: Enhanced Input/Output Display**

**Tasks:**
1. Create input/output visualization component
   - Show input image for each step
   - Show output image after processing
   - Display key metrics prominently

2. Add method-specific displays
   - Parameters used for each method
   - Quality scores/metrics
   - Processing time

3. Improve status reporting
   - Real-time progress updates
   - Clear success/failure indicators
   - Error messages with actionable feedback

**Success Criteria:**
- ✅ Input/output visible for each step
- ✅ Method details shown clearly
- ✅ Status updates are immediate and clear

---

### **HOUR 4: Missing Pipeline Steps - Part 1**

**Tasks:**
1. Implement Step 1: Rotation Correction
   - Wrap existing rotation methods
   - Add Hough Transform, Radon Transform, Projection Profile
   - Create visualization

2. Implement Step 5: Smudge Removal
   - Connect existing smudge detection
   - Add multiple removal methods
   - Show before/after with smudge overlay

3. Test end-to-end flow Steps 0→1→5→0

**Success Criteria:**
- ✅ Rotation correction works with multiple methods
- ✅ Smudge removal shows visual feedback
- ✅ Pipeline can run from start through smudge removal

---

### **HOUR 5-6: Grid Detection & Transformation** 🔴 CRITICAL

**Tasks:**
1. Enhance Step 6: Multi-Scale Grid Detection
   - Connect existing `multi_scale_grid_detector.py`
   - Add method options (Hough, FFT, Morphological)
   - Create comprehensive visualization

2. Implement Step 7: FFT Grid Reconstruction
   - Connect existing `fft_grid_reconstruction.py`
   - Add reconstruction quality metrics
   - Show frequency domain visualization

3. Implement Step 8: Grid Transformation
   - Affine transform
   - Polynomial transform
   - RMSE validation

**Success Criteria:**
- ✅ Grid lines detected (20+ H, 30+ V lines)
- ✅ Grid intersections calculated
- ✅ Transformation RMSE < 5 pixels

---

### **HOUR 7-8: ECG Signal Detection & Extraction**

**Tasks:**
1. Implement Step 9: ECG Signal Detection
   - Detect 12 leads
   - Bounding box detection
   - Lead labeling (I, II, III, etc.)

2. Implement Step 10: Signal Extraction
   - Column-wise scanning
   - Skeletonization method
   - Least-cost path method
   - Calibration (pixels → mV, pixels → seconds)

3. Resample to 500 Hz (5000 points per lead)

**Success Criteria:**
- ✅ 12 leads detected
- ✅ Signals extracted (5000 points each)
- ✅ Calibrated in mV and seconds

---

### **HOUR 9: Validation & Method Selection**

**Tasks:**
1. Implement Step 11: Validation
   - Check lead count (12)
   - Check point count (5000+ per lead)
   - Value range validation (-5 to +5 mV)
   - SNR calculation

2. Enhance method selection logic
   - Automatic best method selection per step
   - Quality score comparison
   - Fallback mechanisms

3. Test full pipeline with validation

**Success Criteria:**
- ✅ Validation catches errors
- ✅ Best methods selected automatically
- ✅ Pipeline completes successfully

---

### **HOUR 10: Easy Method Addition System**

**Tasks:**
1. Create method registration interface
   - Simple decorator or registry
   - Method metadata (name, library, parameters)
   - Quality scoring interface

2. Document method addition process
   - Step-by-step guide
   - Example method implementations
   - Testing requirements

3. Add 1-2 example new methods
   - Demonstrate the system
   - Show it's easy to extend

**Success Criteria:**
- ✅ Can add new method in < 30 minutes
- ✅ Method automatically appears in UI
- ✅ Method tested automatically

---

### **HOUR 11: UI Polish & Status Reporting**

**Tasks:**
1. Enhance dropdown UI
   - Better visual hierarchy
   - Method icons/indicators
   - Library badges (OpenCV, scikit-image, etc.)

2. Improve status reporting
   - Real-time progress bars
   - Detailed error messages
   - Success metrics display

3. Add checkpoint system
   - Save after each step
   - Load from checkpoint
   - Visual checkpoint indicator

**Success Criteria:**
- ✅ UI is clear and intuitive
- ✅ Status updates are informative
- ✅ Checkpoints work reliably

---

### **HOUR 12: Integration Testing & Kaggle Output Verification** 🔴 CRITICAL

**Tasks:**
1. Full end-to-end testing
   - Test with multiple images
   - Verify Kaggle output consistency
   - Check all validation passes

2. Error handling
   - Graceful degradation
   - Partial success handling
   - Clear error messages

3. Documentation
   - Update README
   - Document method addition process
   - Create troubleshooting guide

**Success Criteria:**
- ✅ Pipeline completes successfully on test images
- ✅ Kaggle CSV generated correctly every time
- ✅ All validation checks pass
- ✅ Documentation complete

---

## 🔧 Technical Stack Per Step

### Step 0: Kaggle Output
- **Libraries:** `csv`, `pandas`
- **Dependencies:** None (core Python)

### Step 1: Quality Gates
- **Libraries:** `cv2` (OpenCV), `numpy`
- **Functions:** `cv2.Laplacian()`, histogram analysis

### Step 2: Color Separation
- **Libraries:** `cv2` (OpenCV)
- **Functions:** `cv2.cvtColor()` with `COLOR_BGR2LAB`, `COLOR_BGR2HSV`

### Step 3: Illumination Normalization
- **Libraries:** `cv2` (OpenCV)
- **Functions:** `cv2.createCLAHE()`, morphological operations

### Step 4: Rotation Correction
- **Libraries:** `cv2` (OpenCV), `scipy.ndimage`, `skimage.transform`
- **Functions:** `cv2.HoughLines()`, `skimage.transform.radon()`

### Step 5: Smudge Removal
- **Libraries:** `cv2` (OpenCV)
- **Functions:** `cv2.inpaint()`, morphological operations

### Step 6: Multi-Scale Grid Detection
- **Libraries:** `cv2` (OpenCV), `numpy`
- **Functions:** `cv2.HoughLinesP()`, morphological kernels

### Step 7: FFT Grid Reconstruction
- **Libraries:** `numpy`, `scipy.fft`
- **Functions:** `np.fft.fft2()`, frequency analysis

### Step 8: Grid Transformation
- **Libraries:** `cv2` (OpenCV), `scipy.spatial`, `numpy`
- **Functions:** `cv2.getAffineTransform()`, polynomial fitting

### Step 9: ECG Signal Detection
- **Libraries:** `cv2` (OpenCV), `pytesseract` (optional OCR)
- **Functions:** Template matching, OCR, density analysis

### Step 10: Signal Extraction
- **Libraries:** `cv2` (OpenCV), `scipy.ndimage`, `skimage.morphology`
- **Functions:** Skeletonization, Dijkstra path finding

### Step 11: Validation
- **Libraries:** `numpy`, `scipy.signal`
- **Functions:** SNR calculation, statistical validation

---

## 📋 UI Enhancements Required

### Current State
- ✅ Step dropdowns exist
- ✅ Status indicators work
- ✅ Test Mode implemented

### Enhancements Needed

1. **Method Selection UI**
   - Dropdown per step showing available methods
   - Method description on hover
   - Library badge (OpenCV, scikit-image, etc.)
   - Current method highlighted

2. **Input/Output Display**
   - Side-by-side before/after images
   - Metrics panel showing:
     - Processing time
     - Quality scores
     - Method used
     - Parameters applied

3. **Status Reporting**
   - Real-time progress indicator
   - Step-by-step log
   - Error details with suggestions
   - Success metrics summary

4. **Method Addition Interface**
   - "Add Method" button per step
   - Form for method metadata
   - Code template generator
   - Test interface

---

## 🎯 Success Metrics

### Must Achieve
- [x] Kaggle CSV generated consistently
- [ ] All 12 steps work in sequence
- [ ] Multiple methods available per step
- [ ] UI shows clear method information
- [ ] Can add new methods easily

### Nice to Have
- [ ] Automatic best method selection
- [ ] Checkpoint save/load
- [ ] Method performance comparison
- [ ] Export transformation parameters

---

## 🚨 Risk Mitigation

### Critical Risks

1. **Kaggle Output Not Generated**
   - **Mitigation:** Implement Step 0 first, test independently
   - **Fallback:** Always generate output even if pipeline fails

2. **Pipeline Breaks Mid-Step**
   - **Mitigation:** Try-catch at each step
   - **Fallback:** Save partial results, allow resume

3. **Method Not Working**
   - **Mitigation:** Multiple methods per step
   - **Fallback:** Automatic fallback to simpler method

4. **UI Doesn't Update**
   - **Mitigation:** Real-time status polling
   - **Fallback:** Manual refresh button

---

## 📝 Notes

- Keep existing UI structure - only enhance, don't rebuild
- All new code must integrate with existing transformers
- Prioritize Kaggle output consistency above all else
- Document library versions and dependencies clearly
- Make method addition as simple as possible

---

**Next Steps:** Review this sprint plan, then create detailed Steps Reference Document.
