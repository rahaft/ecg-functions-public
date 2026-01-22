# Pipeline Steps Reference Guide

**Purpose:** Define each step in the ECG digitization pipeline, including available methods, success criteria, and update mechanisms.

---

## 📋 Step 0: Kaggle Output Generator

### Purpose
Generate competition-ready CSV file from extracted ECG signals.

### Input
- ECG record ID (e.g., "record_0")
- 12 lead signals (arrays of 5000 points each)
- Lead names: `['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']`

### Output
- CSV file with format:
```csv
id,value
record_0_I,0.123
record_0_I,0.145
...
record_0_I,0.234
record_0_II,0.089
...
record_0_V6,-0.045
```
- Total rows: 60,000 (12 leads × 5000 points)

### Available Methods

#### Method 1: Direct CSV Writer
- **Library:** Python `csv` module
- **Implementation:**
  ```python
  import csv
  with open('output.csv', 'w', newline='') as f:
      writer = csv.writer(f)
      writer.writerow(['id', 'value'])
      for lead_idx, lead_name in enumerate(lead_names):
          for point_idx, value in enumerate(signals[lead_name]):
              row_id = f"record_{record_id}_{lead_name}"
              writer.writerow([row_id, value])
  ```
- **Pros:** Simple, no dependencies
- **Cons:** Slower for large datasets

#### Method 2: Pandas DataFrame Export
- **Library:** `pandas`
- **Implementation:**
  ```python
  import pandas as pd
  rows = []
  for lead_name in lead_names:
      for idx, value in enumerate(signals[lead_name]):
          rows.append({
              'id': f"record_{record_id}_{lead_name}",
              'value': value
          })
  df = pd.DataFrame(rows)
  df.to_csv('output.csv', index=False)
  ```
- **Pros:** Fast, easy validation
- **Cons:** Requires pandas dependency

### How to Tell It's Working
✅ **Success Indicators:**
- CSV file created successfully
- File has exactly 60,001 rows (header + 60,000 data rows)
- All IDs follow pattern: `record_{recordId}_{leadName}`
- All values are numeric and in range [-5, 5] mV
- File can be opened in spreadsheet software

❌ **Failure Indicators:**
- File not created
- Wrong number of rows
- Invalid ID format
- NaN or invalid values
- File is corrupted

### Validation Checks
1. **Row Count:** Must be 60,001 (1 header + 60,000 data)
2. **ID Format:** Must match `record_\d+_[I|II|III|aVR|aVL|aVF|V1|V2|V3|V4|V5|V6]`
3. **Value Range:** All values between -5.0 and 5.0
4. **No Missing Values:** No NaN, None, or empty cells
5. **File Readable:** Can be parsed as valid CSV

### Update Mechanism
- **Progress:** File generation percentage (0-100%)
- **Status:** "Generating CSV...", "Validating...", "Complete"
- **Errors:** Show specific validation failure
- **UI Display:** Download button appears when complete

---

## 📋 Step 1: Quality Gates (Pre-Processing Check)

### Purpose
Assess image quality before processing begins. Reject images that cannot be processed successfully.

### Input
- Raw ECG image (RGB or grayscale)

### Output
- Quality report dictionary:
```python
{
    'pass': bool,
    'blur_score': float,  # Laplacian variance
    'estimated_dpi': float,
    'contrast_std': float,  # Histogram standard deviation
    'grid_detectable': bool,
    'warnings': list,
    'recommendations': list
}
```

### Available Methods

#### Method 1: Standard Quality Checks
- **Libraries:** `cv2` (OpenCV), `numpy`
- **Checks:**
  1. Blur detection (Laplacian variance)
  2. Resolution estimation (DPI)
  3. Contrast analysis (histogram std)
  4. Grid detectability test
- **Implementation:** See `functions_python/transformers/quality_gates.py`

### How to Tell It's Working
✅ **Success Indicators:**
- Quality report generated
- Blur score > 100 (sharp image)
- Estimated DPI > 150
- Grid lines detected (≥5 lines)
- Pass/fail determination clear

❌ **Failure Indicators:**
- Blur score < 100 → Image too blurry
- DPI < 150 → Resolution too low
- No grid detected → Cannot proceed
- No quality report generated

### Validation Checks
- **Blur:** Laplacian variance ≥ 100 (PASS)
- **Resolution:** Estimated DPI ≥ 150 (PASS)
- **Grid:** ≥ 5 lines detected (PASS)
- **Overall:** All critical checks must pass

### Update Mechanism
- **Progress:** Check by check progress (1/4, 2/4, etc.)
- **Status:** "Checking blur...", "Checking resolution...", etc.
- **Results:** Color-coded (Green=PASS, Yellow=WARN, Red=FAIL)
- **UI Display:** Quality report panel with recommendations

---

## 📋 Step 2: Color Space Separation

### Purpose
Separate grid lines from ECG signals using color information. Handles red grids, black grids, and colored paper.

### Input
- RGB image

### Output
- Trace image (grayscale, ECG signals)
- Grid mask (binary, grid lines)
- Separation metadata

### Available Methods

#### Method 1: LAB Color Space (Default)
- **Library:** `cv2` (OpenCV)
- **Functions:** `cv2.cvtColor(COLOR_BGR2LAB)`, channel extraction
- **Best for:** Red/pink grids, most common cases
- **Implementation:** See `functions_python/transformers/color_separation.py`

#### Method 2: HSV Color Space
- **Library:** `cv2` (OpenCV)
- **Functions:** `cv2.cvtColor(COLOR_BGR2HSV)`, hue thresholding
- **Best for:** Specific colored grids, colored paper backgrounds
- **Implementation:** See `functions_python/transformers/color_separation.py`

### How to Tell It's Working
✅ **Success Indicators:**
- Trace image shows ECG signals clearly
- Grid mask shows grid lines only
- No grid lines in trace image
- No ECG signals in grid mask

❌ **Failure Indicators:**
- Grid lines visible in trace image
- ECG signals missing from trace
- Poor separation (both mixed)

### Update Mechanism
- **Progress:** Separation percentage
- **Status:** "Analyzing color channels...", "Separating...", "Complete"
- **Results:** Side-by-side trace and grid mask display
- **UI Display:** Before/after comparison with separation quality score

---

## 📋 Step 3: Illumination Normalization

### Purpose
Remove lighting artifacts (shadows, yellowing, uneven illumination).

### Input
- Separated trace image or original image

### Output
- Normalized image with uniform illumination
- Illumination map (optional)
- Normalization metadata

### Available Methods

#### Method 1: CLAHE (Default)
- **Library:** `cv2` (OpenCV)
- **Functions:** `cv2.createCLAHE()`, `apply()`
- **Best for:** Most cases, handles local contrast
- **Parameters:** clip_limit (default: 2.0), tile_grid_size (default: 8×8)
- **Implementation:** See `functions_python/transformers/illumination_normalization.py`

#### Method 2: Background Subtraction
- **Library:** `cv2` (OpenCV)
- **Functions:** `cv2.medianBlur()`, division operation
- **Best for:** Strong illumination gradients
- **Implementation:** See `functions_python/transformers/illumination_normalization.py`

#### Method 3: Morphological Background Division
- **Library:** `cv2` (OpenCV)
- **Functions:** `cv2.dilate()`, division operation
- **Best for:** Uneven paper color (yellowed, aged)
- **Implementation:** See `functions_python/transformers/illumination_normalization.py`

### How to Tell It's Working
✅ **Success Indicators:**
- Image has uniform brightness
- No visible shadows or gradients
- Grid lines remain sharp
- Contrast improved

❌ **Failure Indicators:**
- Still has shadows/uneven lighting
- Grid lines blurred or lost
- Contrast too low or too high

### Update Mechanism
- **Progress:** Normalization percentage
- **Status:** "Analyzing illumination...", "Normalizing...", "Complete"
- **Results:** Before/after comparison
- **UI Display:** Illumination map overlay, brightness histogram

---

## 📋 Step 4: Rotation Correction

### Purpose
Correct general 2D rotation to align grid lines with image axes.

### Input
- Normalized image (grayscale)

### Output
- Rotated image (grid aligned)
- Rotation angle (degrees)
- Confidence score (0-1)

### Available Methods

#### Method 1: Hough Transform (Default)
- **Libraries:** `cv2` (OpenCV)
- **Functions:** `cv2.HoughLines()`, angle calculation
- **Best for:** Clear grid lines
- **Implementation:** Angle detection from detected lines

#### Method 2: Radon Transform
- **Libraries:** `skimage.transform`
- **Functions:** `radon()`, peak detection
- **Best for:** Faint or noisy grids
- **Implementation:** Dominant angle from transform

#### Method 3: Projection Profile
- **Libraries:** `numpy`
- **Functions:** `np.sum()` along rows/columns
- **Best for:** Very regular grids
- **Implementation:** Angle with maximum variance

### How to Tell It's Working
✅ **Success Indicators:**
- Grid lines perfectly horizontal/vertical
- Rotation angle detected (typically -5° to +5°)
- Confidence score > 0.7
- Perpendicularity ≈ 90° after rotation

❌ **Failure Indicators:**
- Grid still rotated
- Confidence score < 0.5
- Wrong angle detected (off by >10°)

### Validation Checks
- **Confidence:** ≥ 0.7 (high confidence)
- **Angle Range:** -15° to +15° (reject if > 15°)
- **Perpendicularity:** H and V lines ≈ 90° apart after rotation

### Update Mechanism
- **Progress:** Detection → Rotation → Validation
- **Status:** "Detecting angle...", "Rotating...", "Validating..."
- **Results:** Before/after comparison with angle overlay
- **UI Display:** Detected angle shown, grid lines highlighted

---

## 📋 Step 5: Smudge Detection & Removal

### Purpose
Remove smudges, artifacts, and noise while preserving grid lines and ECG signals.

### Input
- Rotated image (grayscale)

### Output
- Cleaned image
- Smudge mask (binary, shows detected smudges)
- Severity score (0-100%)

### Available Methods

#### Method 1: OpenCV Inpainting (Default)
- **Library:** `cv2` (OpenCV)
- **Functions:** `cv2.inpaint()`, morphological operations
- **Method:** INPAINT_NS (Navier-Stokes)
- **Best for:** Precise smudge removal, preserves grid
- **Parameters:** inpaint_radius (default: 3)
- **Implementation:** See `functions_python/transformers/` (smudge removal)

#### Method 2: Morphological Cleaning
- **Library:** `cv2` (OpenCV)
- **Functions:** `cv2.morphologyEx()`, opening/closing
- **Best for:** Fast preprocessing, less precise
- **Implementation:** Morphological operations to separate smudges

#### Method 3: Connected Component Analysis
- **Library:** `cv2` (OpenCV)
- **Functions:** `cv2.findContours()`, blob analysis
- **Best for:** Large, distinct smudges
- **Implementation:** Detect blobs, filter by size/shape

### How to Tell It's Working
✅ **Success Indicators:**
- Smudges removed from image
- Grid lines preserved
- ECG signals intact
- Smudge mask shows only smudges (red overlay)
- Severity score decreases after removal

❌ **Failure Indicators:**
- Smudges still visible
- Grid lines damaged
- ECG signals removed or damaged
- Too aggressive (removed valid content)

### Update Mechanism
- **Progress:** Detection → Removal → Validation
- **Status:** "Detecting smudges...", "Removing...", "Validating..."
- **Results:** Red overlay on smudges, before/after comparison
- **UI Display:** Smudge count, severity score, cleaned image

---

## 📋 Step 6: Multi-Scale Grid Detection

### Purpose
Detect both 1mm (small) and 5mm (large) grid lines separately.

### Input
- Cleaned image (grayscale)

### Output
- Horizontal grid lines (list of Line objects)
- Vertical grid lines (list of Line objects)
- Grid intersections (array of (x,y) points)
- Grid quality score (0-1)

### Available Methods

#### Method 1: Morphological Detection (Default)
- **Library:** `cv2` (OpenCV)
- **Functions:** `cv2.morphologyEx()` with line kernels
- **Two-Pass:** Fine grid (1mm) and bold grid (5mm)
- **Best for:** Clear, well-defined grids
- **Implementation:** See `functions_python/transformers/multi_scale_grid_detector.py`

#### Method 2: Hough Line Transform
- **Library:** `cv2` (OpenCV)
- **Functions:** `cv2.HoughLinesP()`, angle filtering
- **Best for:** Thin or faded grid lines
- **Implementation:** Detect all lines, filter by angle

#### Method 3: Projection Profile
- **Libraries:** `numpy`
- **Functions:** `np.sum()` along axes, peak detection
- **Best for:** Very regular, periodic grids
- **Implementation:** Find peaks in row/column sums

#### Method 4: FFT-Based Detection
- **Libraries:** `numpy`, `scipy.fft`
- **Functions:** `np.fft.fft2()`, frequency analysis
- **Best for:** Periodic grids, validation
- **Implementation:** See Step 7

### How to Tell It's Working
✅ **Success Indicators:**
- 20+ horizontal lines detected
- 30+ vertical lines detected
- Lines are straight and continuous
- Intersections calculated correctly
- Grid quality score > 0.7

❌ **Failure Indicators:**
- < 10 lines detected (too few)
- Lines are broken or curved
- Many false positives (ECG waves detected as grid)
- No intersections found

### Validation Checks
- **Line Count:** ≥ 10 H lines, ≥ 10 V lines
- **Line Length:** ≥ 70% of image dimension
- **Angle Deviation:** < 5° from perfect H/V
- **Spacing Consistency:** CV < 0.15

### Update Mechanism
- **Progress:** Detection → Filtering → Intersection calculation
- **Status:** "Detecting lines...", "Filtering...", "Finding intersections..."
- **Results:** Lines overlaid on image (red=H, blue=V), intersections marked
- **UI Display:** Line count, quality score, grid overlay visualization

---

## 📋 Step 7: FFT Grid Reconstruction

### Purpose
Reconstruct missing or occluded grid sections using frequency domain analysis.

### Input
- Image with partial or missing grid
- Detected grid lines from Step 6

### Output
- Reconstructed grid (complete)
- Reconstruction quality score
- Frequency spectrum visualization

### Available Methods

#### Method 1: FFT-Based Reconstruction (Only Method)
- **Libraries:** `numpy`, `scipy.fft`
- **Functions:** `np.fft.fft2()`, `np.fft.ifft2()`, frequency filtering
- **Best for:** 40-60% grid missing, heavy occlusion
- **Implementation:** See `functions_python/transformers/fft_grid_reconstruction.py`

### How to Tell It's Working
✅ **Success Indicators:**
- Grid reconstructed even with 40%+ missing
- Reconstructed lines align with existing grid
- Quality score > 0.6
- Frequency peaks clearly visible

❌ **Failure Indicators:**
- Reconstruction doesn't match existing grid
- No clear frequency peaks
- Quality score < 0.4

### Update Mechanism
- **Progress:** FFT → Frequency analysis → Reconstruction
- **Status:** "Analyzing frequencies...", "Reconstructing...", "Validating..."
- **Results:** Frequency spectrum display, reconstructed grid overlay
- **UI Display:** Before/after grid comparison, frequency visualization

---

## 📋 Step 8: Grid Transformation

### Purpose
Transform detected grid to perfect ideal grid, correcting distortion.

### Input
- Detected grid lines and intersections
- Grid spacing information

### Output
- Transformation matrix
- RMSE (root mean square error)
- Transformation quality score
- Ideal grid overlay

### Available Methods

#### Method 1: Affine Transform (Default)
- **Library:** `cv2` (OpenCV)
- **Functions:** `cv2.getAffineTransform()`, `cv2.warpAffine()`
- **DOF:** 6 parameters (rotation, scale, translation, shear)
- **Best for:** Simple distortion, good grid quality
- **Implementation:** Map detected → ideal intersections

#### Method 2: Polynomial Transform
- **Libraries:** `numpy`, `scipy`
- **Functions:** Polynomial fitting, higher-order transform
- **DOF:** Variable (3rd order = 10 parameters)
- **Best for:** Smooth distortion, warped paper
- **Implementation:** Fit polynomial to intersection mapping

#### Method 3: Piecewise Affine
- **Library:** `cv2` (OpenCV), `scipy.spatial`
- **Functions:** Multiple affine transforms per region
- **Best for:** Complex, local distortions
- **Implementation:** Divide into regions, transform separately

### How to Tell It's Working
✅ **Success Indicators:**
- RMSE < 5 pixels
- Grid aligns with ideal grid
- Transformation quality score > 0.8
- Visual overlay shows good match

❌ **Failure Indicators:**
- RMSE > 10 pixels
- Grid still misaligned
- Quality score < 0.5

### Validation Checks
- **RMSE:** < 5 pixels (excellent), < 10 pixels (acceptable)
- **Jitter:** < 0.5 pixels (spacing variance)
- **Perpendicularity:** H and V lines ≈ 90° after transform

### Update Mechanism
- **Progress:** Analysis → Transformation calculation → Validation
- **Status:** "Analyzing grid...", "Computing transform...", "Validating..."
- **Results:** RMSE display, overlay visualization, error heatmap
- **UI Display:** Before/after grid comparison, RMSE value, quality score

---

## 📋 Step 9: ECG Signal Detection

### Purpose
Detect and identify 12 ECG leads with bounding boxes and labels.

### Input
- Original or processed image
- Grid information

### Output
- Lead bounding boxes (12 rectangles)
- Lead labels (I, II, III, aVR, aVL, aVF, V1-V6)
- Detection confidence scores
- Lead positions (x, y, width, height)

### Available Methods

#### Method 1: Template Matching (Default)
- **Library:** `cv2` (OpenCV)
- **Functions:** `cv2.matchTemplate()`, template database
- **Best for:** Standard 3×4 or 4×3 layouts
- **Implementation:** Match against known ECG layouts

#### Method 2: OCR Text Recognition
- **Libraries:** `pytesseract`, `cv2` (OpenCV)
- **Functions:** OCR to find lead labels, bounding box detection
- **Best for:** Images with visible lead labels
- **Implementation:** Detect text, match to lead names

#### Method 3: Signal Density Analysis
- **Library:** `cv2` (OpenCV), `numpy`
- **Functions:** Dark region detection, clustering
- **Best for:** No visible labels, layout unknown
- **Implementation:** Find dark regions (signals), cluster into leads

### How to Tell It's Working
✅ **Success Indicators:**
- 12 leads detected
- All lead names correct
- Bounding boxes enclose signals properly
- Confidence scores > 0.6

❌ **Failure Indicators:**
- < 10 leads detected
- Wrong lead names
- Bounding boxes miss signals or include extra content
- Low confidence scores

### Validation Checks
- **Lead Count:** Exactly 12 leads
- **Label Accuracy:** All labels match expected set
- **Box Quality:** Boxes properly enclose signals
- **Spacing:** Leads evenly distributed

### Update Mechanism
- **Progress:** Layout detection → Lead detection → Labeling
- **Status:** "Detecting layout...", "Finding leads...", "Labeling..."
- **Results:** Bounding boxes overlaid (green), labels shown
- **UI Display:** Lead count, confidence scores, labeled boxes

---

## 📋 Step 10: Signal Extraction & Calibration

### Purpose
Extract time-series signal data from each lead and calibrate to physical units.

### Input
- Lead bounding boxes
- Grid transformation information
- Calibration pulse (if available)

### Output
- 12 lead signals (5000 points each)
- Calibration parameters (pixels_per_mV, pixels_per_second)
- Signal quality scores per lead
- Resampled signals at 500 Hz

### Available Methods

#### Method 1: Column-Wise Scanning (Default)
- **Libraries:** `numpy`, `cv2` (OpenCV)
- **Functions:** Column-wise dark pixel detection
- **Best for:** Clean signals, fast processing
- **Implementation:** For each column, find darkest pixel

#### Method 2: Skeletonization + Tracing
- **Libraries:** `cv2` (OpenCV), `skimage.morphology`
- **Functions:** Skeletonization, path tracing
- **Best for:** Accurate centerline extraction
- **Implementation:** Skeletonize signal, trace path

#### Method 3: Least-Cost Path (Dijkstra)
- **Libraries:** `scipy.sparse`, graph algorithms
- **Functions:** Dijkstra shortest path
- **Best for:** Broken or noisy signals
- **Implementation:** Graph-based path finding

### Calibration

#### Voltage Calibration
- **Method 1:** Detect 1mV calibration pulse
- **Method 2:** Use grid spacing (1mm = 0.1mV)
- **Formula:** `voltage_mV = (baseline_y - pixel_y) / pixels_per_mV`

#### Time Calibration
- **Standard:** 25 mm/s paper speed
- **Formula:** `time_sec = pixel_x / pixels_per_second`
- **Resampling:** Interpolate to 500 Hz (5000 points)

### How to Tell It's Working
✅ **Success Indicators:**
- 12 signals extracted (5000 points each)
- Signals look like ECG waveforms
- Calibration reasonable (values in [-5, 5] mV range)
- Quality scores > 0.7
- Resampling successful

❌ **Failure Indicators:**
- Missing signals or < 5000 points
- Signals don't look like ECG
- Calibration wrong (values outside [-5, 5] mV)
- Low quality scores

### Validation Checks
- **Point Count:** Exactly 5000 points per lead
- **Value Range:** All values between -5 and +5 mV
- **SNR:** > 10 dB per lead
- **Smoothness:** Low derivative variance

### Update Mechanism
- **Progress:** Extraction → Calibration → Resampling
- **Status:** "Extracting signals...", "Calibrating...", "Resampling..."
- **Results:** Signal plots displayed, quality scores shown
- **UI Display:** 12 lead plots, calibration values, quality metrics

---

## 📋 Step 11: Validation & Quality Check

### Purpose
Validate all extracted data and calculate quality metrics.

### Input
- 12 extracted lead signals
- All intermediate results and metrics

### Output
- Validation report
- Overall quality score
- Pass/fail determination
- Recommendations

### Validation Checks

1. **Lead Count:** Exactly 12 leads
2. **Point Count:** 5000+ points per lead
3. **Value Range:** All values in [-5, 5] mV
4. **No NaN Values:** No missing data
5. **SNR:** Average SNR > 15 dB
6. **Grid RMSE:** < 5 pixels (from Step 8)

### Quality Metrics

- **Overall SNR:** Average of all lead SNRs
- **Signal Completeness:** Percentage of valid points
- **Calibration Accuracy:** Deviation from expected ranges
- **Grid Quality:** RMSE and jitter from Step 8

### How to Tell It's Working
✅ **Success Indicators:**
- All validation checks pass
- Overall quality score > 0.7
- SNR > 15 dB
- Status: "PASS - Ready for submission"

❌ **Failure Indicators:**
- Any validation check fails
- Quality score < 0.5
- SNR < 10 dB
- Status: "FAIL - Do not submit"

### Update Mechanism
- **Progress:** Check by check validation
- **Status:** "Validating...", "Calculating metrics...", "Complete"
- **Results:** Validation report with pass/fail for each check
- **UI Display:** Color-coded validation panel, overall status, recommendations

---

## 📋 Step 12: Final Output Generation

### Purpose
Generate all final outputs including Kaggle CSV (CRITICAL).

### Input
- Validated signals from Step 11
- Record ID

### Output
- Kaggle submission CSV (ALWAYS GENERATED)
- Quality report JSON
- Visualization summary (optional)
- Status confirmation

### Available Methods

#### Method 1: Kaggle CSV (CRITICAL - Always Runs)
- **Implementation:** See Step 0
- **Must work even if pipeline partially failed**
- **Fallback:** Generate from whatever signals available

#### Method 2: Quality Report JSON
- **Format:** JSON with all metrics and validation results
- **Contains:** SNR, validation checks, method used, timestamps

#### Method 3: Visualization Summary
- **Format:** PNG or PDF
- **Contains:** All 12 lead plots, quality metrics, processing summary

### How to Tell It's Working
✅ **Success Indicators:**
- Kaggle CSV generated (always)
- File downloadable
- Format valid
- All outputs created

❌ **Failure Indicators:**
- CSV not generated
- Invalid format
- File corrupted
- Cannot download

### Update Mechanism
- **Progress:** "Generating outputs...", "Validating...", "Complete"
- **Status:** Final status message
- **Results:** Download buttons for all outputs
- **UI Display:** Success message, download links, file size info

---

## 🔧 How to Add a New Method

### Step-by-Step Process

1. **Create Method Function**
   ```python
   def my_new_method(input_data, **params):
       """
       Method description
       
       Args:
           input_data: Input for this step
           **params: Method-specific parameters
       
       Returns:
           result: Output data
           metrics: Quality metrics dictionary
       """
       # Implementation
       result = process_data(input_data, params)
       metrics = calculate_metrics(result)
       return result, metrics
   ```

2. **Register Method**
   ```python
   from steps.base_step import register_method

   register_method(
       step_name="step_4_rotation",
       method_name="My New Method",
       method_function=my_new_method,
       libraries=["cv2", "numpy"],  # Required libraries
       parameters={
           "param1": {"type": "float", "default": 1.0, "description": "..."},
           "param2": {"type": "int", "default": 5, "description": "..."}
       }
   )
   ```

3. **Test Method**
   - Test with sample data
   - Verify output format matches step requirements
   - Check metrics are reasonable

4. **Update UI** (Automatic)
   - Method appears in dropdown automatically
   - Parameters shown in UI
   - Library badges displayed

### Method Requirements

- **Input/Output:** Must match step specification
- **Metrics:** Must return quality score (0-1)
- **Error Handling:** Must handle errors gracefully
- **Documentation:** Docstring required

---

## 📊 Status Update Format

### Standard Update Structure

```python
{
    "step": "step_name",
    "status": "in_progress" | "completed" | "failed" | "pending",
    "progress": 0-100,  # Percentage
    "current_operation": "Description of current task",
    "method": "method_name",
    "metrics": {
        "quality_score": 0.0-1.0,
        # Step-specific metrics
    },
    "visualization": "base64_encoded_image",  # Optional
    "errors": [],  # List of error messages if failed
    "warnings": [],  # List of warnings
    "timestamp": "ISO_timestamp"
}
```

### UI Display Format

- **Status Icon:** ✅ 🔄 ⏳ ❌
- **Progress Bar:** 0-100% with color coding
- **Current Operation:** Text description
- **Method Badge:** Method name with library icons
- **Metrics Panel:** Key metrics displayed prominently
- **Visualization:** Before/after images or charts

---

## 🎯 Success Criteria Summary

| Step | Critical Metric | Target | How to Verify |
|------|----------------|--------|---------------|
| 0 | CSV generated | Always | File exists, valid format |
| 1 | Quality pass | All checks | Green status indicators |
| 2 | Separation quality | Trace/grid separate | Visual inspection |
| 3 | Illumination uniform | No shadows | Before/after comparison |
| 4 | Grid alignment | Angle < 2° | Visual grid lines |
| 5 | Smudges removed | Severity < 5% | Red overlay shows none |
| 6 | Lines detected | 20+ H, 30+ V | Line count display |
| 7 | Grid reconstructed | Quality > 0.6 | Overlay matches |
| 8 | RMSE | < 5 pixels | RMSE display |
| 9 | Leads detected | 12 leads | Box count, labels |
| 10 | Signals extracted | 5000 pts/lead | Signal plots, point count |
| 11 | Validation pass | All checks | Green status |
| 12 | Outputs generated | All files | Download buttons |

---

**Document Version:** 1.0  
**Last Updated:** [Date]  
**Maintainer:** Development Team
