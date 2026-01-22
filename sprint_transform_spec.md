# Transform & Comparison Specification

**Version:** 1.0  
**Last Updated:** January 2026  
**Status:** In Development

---

## Overview

This document specifies the image transformation and comparison workflow for ECG digitization. The system allows users to compare images side-by-side, apply transformations step-by-step, and visualize results at each stage.

---

## Table of Contents

1. [Image Comparison Interface](#image-comparison-interface)
2. [Compare Popup](#compare-popup)
3. [Transform Workflow](#transform-workflow)
4. [Transformation Steps](#transformation-steps)
5. [Technical Implementation](#technical-implementation)

---

## Image Comparison Interface

### Image Matching

**Requirement:** When clicking "Compare", the image must match exactly between:
- The front/gallery page (source image)
- The "Image Comparison & Algorithm Analysis" page (comparison target)

**Implementation:**
- Store image reference/URL when "Compare" is clicked
- Pass image identifier to comparison page
- Load same image on both pages from shared source
- Verify image identity matches before displaying

---

## Compare Popup

### Layout

When "Compare" button is clicked, a popup/modal opens with:

#### Top Section: Image Display
- **Left Side:** Comparative/Reference Image
- **Right Side:** Test Image (current image being analyzed)
- **Toggle Options:**
  - "Both" - Show both images side-by-side (50% width each)
  - "Comparative Only" - Show only reference image (100% width)
  - "Test Only" - Show only test image (100% width)

#### Image Controls (per image)
1. **Open in New Window** button
   - Opens image in new browser tab/window
   - Full resolution view
   - Independent zoom controls

2. **Zoom Controls**
   - Zoom In (+ button)
   - Zoom Out (- button)
   - Reset Zoom (return to fit-to-screen)
   - Zoom slider (optional, for precise control)
   - Zoom range: 10% to 500%

#### Transform Button
- Located on the compare screen
- Initiates transformation workflow
- Shows transformation menu when clicked

---

## Transform Workflow

### Transformation Menu

When "Transform" is clicked, a menu appears under each image showing:

1. **Current Stage** indicator
2. **Progress Bar** showing completion percentage
3. **Stage List** with status indicators:
   - ✅ Completed
   - 🔄 In Progress
   - ⏳ Pending
   - ❌ Failed

### Steps Dropdown

Under each image, there is a collapsible dropdown menu listing all transformation steps:

```
[▶] Transformation Steps
  ├─ [✓] 1. Assumptions
  ├─ [✓] 2. Rotation Correction
  ├─ [✓] 3. Smudge Detection & Removal
  ├─ [🔄] 4. Grid Line Detection
  ├─ [⏳] 5. Grid Spacing Estimation
  ├─ [⏳] 6. Affine/Homography Transform
  ├─ [⏳] 7. ECG Trace Extraction
  ├─ [⏳] 8. Apply Transform to Trace
  ├─ [⏳] 9. Skeletonize
  └─ [⏳] 10. Convert to Signal
```

Each step can be:
- Clicked to view details
- Expanded to see sub-options
- Re-run with different parameters

---

## Transformation Steps

### Step 1: Assumptions Tab

**Purpose:** Set initial parameters and assumptions about the image.

#### Grid Ratio Settings

**Small Squares (Default):**
- Width Ratio: `1 mm` = `1` pixel (editable via text input)
- Height Ratio: `1 mm` = `1` pixel (editable via text input)

**Large Squares:**
- Width Ratio: `5 mm` = `5` pixels (editable via text input)
- Height Ratio: `5 mm` = `5` pixels (editable via text input)

**UI Elements:**
- Text input fields for width and height ratios
- Default values shown
- Real-time validation
- Save button to persist settings

#### ECG Lines Count

- Input field: Number of ECG leads/lines
- Default: 12 (standard 12-lead ECG)
- Reset button to restore default
- Validation: Accept values 1-20

---

### Step 2: Rotation Correction

**Purpose:** Correct general 2D rotation to align grid lines.

**Method:** 
- Detect if one side or top/bottom lines can be aligned without rotation
- Find dominant angle of grid lines
- Apply rotation transform to align grid horizontally/vertically

**Approach:**
1. Use edge detection to find grid lines
2. Apply Hough Transform to detect line angles
3. Find most common angle
4. Rotate image to align with horizontal/vertical axes

**Output:**
- Rotated image
- Rotation angle (degrees)
- Before/after comparison

---

### Step 3: Smudge Detection & Removal

**Purpose:** Remove small smudges and artifacts from the document.

**Default Method:** Method 1 - OpenCV Inpainting

#### Method 1: OpenCV Inpainting (Default) ✅

**Best for:** ECG grids with smudges that need precise removal

**Process:**
1. Convert to grayscale
2. Create mask of smudged regions (dark blobs below threshold)
3. Remove thin lines (grid lines) from mask
4. Keep only large blobs (smudges)
5. Apply morphological operations to clean mask
6. Use OpenCV inpainting (Navier-Stokes method) to fill smudges

**Parameters:**
- Threshold: 50 (adjustable)
- Inpaint radius: 3 pixels
- Method: Navier-Stokes (INPAINT_NS) for better quality

**Implementation:**
```python
def remove_smudges_inpainting(image):
    """
    Remove smudges using OpenCV inpainting
    Works great for preserving grid lines
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Step 1: Create mask of smudged regions
    _, dark_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    
    # Step 2: Remove thin lines (grid lines) from mask
    kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
    kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))
    
    vertical_lines = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel_vertical)
    horizontal_lines = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel_horizontal)
    
    # Remove grid lines from mask
    grid_mask = cv2.bitwise_or(vertical_lines, horizontal_lines)
    smudge_mask = cv2.subtract(dark_mask, grid_mask)
    
    # Step 3: Clean up mask - only keep large blobs
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    smudge_mask = cv2.morphologyEx(smudge_mask, cv2.MORPH_OPEN, kernel)
    smudge_mask = cv2.morphologyEx(smudge_mask, cv2.MORPH_CLOSE, kernel)
    
    # Step 4: Expand mask slightly to cover smudge edges
    smudge_mask = cv2.dilate(smudge_mask, kernel, iterations=2)
    
    # Step 5: Apply inpainting (Navier-Stokes method)
    inpainted_ns = cv2.inpaint(gray, smudge_mask, 3, cv2.INPAINT_NS)
    
    return inpainted_ns, smudge_mask
```

**UI Options:**
- Method selector: "Method 1: Inpainting" (default) or "Method 2: Morphological"
- Threshold slider (0-255, default: 50)
- Inpaint radius input (1-10, default: 3)
- Preview button to see smudge mask
- Apply button to execute

#### Method 2: Morphological Operations (Alternative)

**Best for:** Fast preprocessing, less precise

**Process:**
1. Enhance contrast using CLAHE
2. Use morphological operations to separate smudges from lines
3. Extract vertical and horizontal grid lines
4. Reconstruct image from grid + signal only

**Implementation:**
```python
def remove_smudges_morphological(image):
    """
    Use morphological operations to separate smudges from lines
    Best as preprocessing before inpainting
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # Step 1: Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Step 2: Separate smudges from lines using morphology
    # Extract vertical lines (grid)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
    vertical_lines = cv2.morphologyEx(enhanced, cv2.MORPH_OPEN, vertical_kernel)
    
    # Extract horizontal lines (grid)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
    horizontal_lines = cv2.morphologyEx(enhanced, cv2.MORPH_OPEN, horizontal_kernel)
    
    # Combine grid lines
    grid = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0)
    
    # Reconstruct image from grid + signal only
    cleaned = cv2.addWeighted(enhanced, 1.0, grid, 0.5, 0)
    
    return cleaned
```

**UI Options:**
- Method selector dropdown
- CLAHE clip limit (0.5-4.0, default: 2.0)
- Kernel size sliders

---

### Step 4: Grid Line Detection

**Purpose:** Detect individual grid lines using multiple methods.

#### Method A: Hough Lines (Primary)

**Approach:**
- Apply Hough Transform to detect straight lines
- Separate horizontal and vertical lines
- Filter lines by length and angle
- Group parallel lines

**Output:**
- List of detected horizontal lines (coordinates)
- List of detected vertical lines (coordinates)
- Line intersections
- Visualization overlay

#### Method B: Fast Fourier Transform (FFT) Analysis

**Purpose:** Analyze periodic patterns in grid

**Approach:**
1. Apply FFT to detect frequency components
2. Identify dominant frequencies corresponding to grid spacing
3. Reconstruct grid pattern from frequencies
4. Validate against Hough line detection

**When to use:**
- Regular, periodic grids
- Validation of Hough results
- Grid spacing estimation

**Output:**
- Frequency spectrum
- Detected grid frequencies
- Reconstructed grid pattern

**UI Options:**
- Toggle between Hough-only or Hough + FFT
- FFT window size
- Frequency filtering threshold

---

### Complete Transformation Pipeline

The following steps complete the full transformation workflow. Each step has default methods with options to switch:

```
1. Input Image
   └─ Load from comparison source

2. Color Separation
   ├─ Default: Lab color space
   ├─ Alternative: HSV color space
   └─ Purpose: Separate grid from ECG traces

3. Edge Detection
   ├─ Default: Canny edge detection
   ├─ Alternatives: Sobel, Scharr, Laplacian
   └─ Parameters: Low/high thresholds (adjustable)

4. Hough Transform → Rotation Correction
   ├─ Default: Probabilistic Hough Lines
   ├─ Alternative: Standard Hough Lines
   └─ Output: Rotation angle and corrected image

5. Grid Isolation
   ├─ Default: FFT-based frequency analysis
   ├─ Alternative: Morphological operations
   └─ Purpose: Separate grid from ECG signals

6. Grid Line Detection
   ├─ Default: Hough Lines + FFT validation
   ├─ Alternative: Line tracking algorithms
   └─ Output: Horizontal/vertical line coordinates

7. Grid Spacing Estimation
   ├─ Default: Statistical analysis of intersections
   ├─ Alternative: FFT frequency analysis
   └─ Output: Pixels per mm (using assumptions from Step 1)

8. Compute Affine/Homography Transform
   ├─ Default: Affine transform (6 DOF)
   ├─ Alternative: Homography transform (8 DOF)
   └─ Purpose: Correct perspective distortion

9. ECG Trace Extraction
   ├─ Default: Region-based extraction
   ├─ Alternative: Contour detection
   └─ Output: Individual ECG lead traces

10. Apply Transform to ECG Trace
    └─ Apply computed transform to each trace

11. Skeletonize
    ├─ Default: Zhang-Suen algorithm
    ├─ Alternative: Morphological thinning
    └─ Purpose: Extract centerline of ECG waveforms

12. Convert to Signal (mV vs sec)
    ├─ Default: Vertical sampling along grid
    ├─ Calibration: Use grid spacing from Step 7
    ├─ Time axis: Based on horizontal spacing
    └─ Voltage axis: Based on vertical spacing (assumed 0.1mV/mm)
    └─ Output: Time-series data array
```

---

## Technical Implementation

### Backend (Python)

**Location:** `functions_python/transformers/transform_pipeline.py`

**Structure:**
```python
class TransformPipeline:
    def __init__(self, assumptions):
        self.assumptions = assumptions
        self.steps = []
    
    def step_rotation_correction(self, image):
        # Implementation
    
    def step_smudge_removal(self, image, method='inpainting'):
        # Implementation
    
    def step_grid_detection(self, image):
        # Implementation
    
    # ... other steps
```

**API Endpoint:** `/transform-pipeline`
- Accepts: Image data, assumptions, step configuration
- Returns: Result at each step, intermediate images

### Frontend (JavaScript)

**Location:** `public/gallery.html` and `public/transform_ui.js`

**Key Components:**
1. Compare popup modal
2. Image viewer with zoom controls
3. Transform menu component
4. Step dropdown/accordion
5. Progress indicator
6. Before/after comparison views

**State Management:**
- Current image references
- Transformation state at each step
- User-selected parameters
- Method selections

---

## UI/UX Requirements

### Compare Popup

**Responsive Design:**
- Mobile: Stack images vertically
- Tablet: Side-by-side with toggle
- Desktop: Full side-by-side with controls

**Accessibility:**
- Keyboard navigation (arrow keys, tab)
- Screen reader support
- High contrast mode support
- Zoom controls accessible via keyboard

### Transform Menu

**Visual Feedback:**
- Color coding: Green (complete), Blue (in progress), Gray (pending), Red (error)
- Animated progress bar
- Real-time image updates
- Loading indicators for each step

**User Interaction:**
- Click step to view details
- Expand/collapse step dropdown
- Modify parameters and re-run step
- Undo/redo functionality
- Export intermediate results

---

## Error Handling

### Common Issues

1. **Image Not Found**
   - Verify image reference
   - Show error message
   - Provide retry option

2. **CORS Errors**
   - Fallback to server-side processing
   - Clear error message
   - Suggest configuration fix

3. **Transformation Failures**
   - Show step where failure occurred
   - Provide error details
   - Suggest parameter adjustments
   - Allow step re-run with different parameters

4. **Low Quality Detection**
   - Warn user about poor results
   - Suggest image quality improvements
   - Offer manual parameter adjustment

---

## Testing Requirements

### Unit Tests
- Each transformation step independently
- Parameter validation
- Method switching

### Integration Tests
- Full pipeline execution
- Image matching between pages
- Popup functionality
- Zoom and view controls

### User Acceptance Tests
- Compare workflow end-to-end
- Transform workflow with all steps
- Method switching
- Parameter modification

---

## Future Enhancements

### Phase 2
- Batch processing multiple images
- Save transformation presets
- Export transformation parameters
- Comparison metrics between reference and test

### Phase 3
- AI-assisted parameter suggestions
- Automatic method selection
- Learning from user corrections
- Advanced visualization options

---

---

## Test vs Production Mode

### Mode Toggle

**Requirement:** Add a toggle/switch in the transform interface to switch between:
- **Test Mode** - Manual step-by-step execution
- **Production Mode** - Automatic pipeline execution

**Location:** Top of transformation menu

**UI Element:**
```
[Test Mode] ← → [Production Mode]
     ●                ○
```

### Test Mode Features

**Purpose:** Allows manual control and debugging of each transformation step

**Behavior:**
- Each step must be manually triggered
- "Next Step" button appears after each step completes
- User can review results before proceeding
- User can adjust parameters between steps
- User can skip steps (with warning)
- User can go back to previous steps
- Real-time visualization after each step

**UI Elements:**
- **"Execute Step"** button for each pending step
- **"Next Step"** button (appears after step completes)
- **"Skip Step"** button (with confirmation)
- **"Restart Pipeline"** button
- **"Go to Step X"** dropdown

**Step Status in Test Mode:**
```
[✓] Step 1: Assumptions - COMPLETED
[🔄] Step 2: Quality Gates - IN PROGRESS
[▶] Step 3: Color Separation - Click to Execute
[⏸] Step 4: Rotation Correction - WAITING
...
```

### Production Mode Features

**Purpose:** Automatic execution of all steps without manual intervention

**Behavior:**
- All steps execute automatically in sequence
- Progress bar shows overall completion
- Each step runs to completion before next begins
- On error, pipeline stops and shows error
- Results stored automatically after each step
- Final result saved when complete

**UI Elements:**
- **"Start Pipeline"** button
- **"Pause Pipeline"** button (pause at current step)
- **"Cancel Pipeline"** button
- Overall progress bar (0-100%)
- Current step indicator

---

## Universal Preprocessing Pipeline (Phase 1)

### Step 1: Quality Gates (Pre-Processing Check)

**Purpose:** Automatic image quality assessment before processing begins

**Quality Checks:**

1. **Blur Detection (Laplacian Variance)**
   - Threshold: < 100 → REJECT
   - Message: "Image too blurry - please rescan with higher quality"
   - Pass: ≥ 100 → Continue

2. **Resolution Check (DPI Estimation)**
   - Threshold: < 150 DPI → REJECT
   - Warning: 150-200 DPI → WARN "Low resolution - accuracy reduced"
   - Pass: ≥ 200 DPI → Continue
   - Message if fail: "Resolution too low - minimum 150 DPI required"

3. **Contrast Analysis (Histogram Standard Deviation)**
   - Threshold: Std < 30 → REJECT (deferred to final step)
   - Warning: Std 30-50 → WARN "Poor contrast - using CLAHE boost"
   - Pass: Std > 50 → Continue
   - **Note:** Final contrast rejection happens at the END (Step N+1)

4. **Grid Detectability Test**
   - Test: Can we detect any grid lines?
   - Result: 0 lines → FAIL → Try FFT method
   - Result: < 5 lines → WARN "Partial grid only"
   - Result: ≥ 5 lines → PASS

**Implementation:**
```python
def quality_gates(image):
    results = {
        'blur': check_blur(image),
        'resolution': check_resolution(image),
        'contrast': check_contrast(image),  # Deferred to final step
        'grid_detectability': test_grid_detection(image)
    }
    
    if results['blur'] < 100:
        return {'pass': False, 'reason': 'Too blurry', 'results': results}
    
    if results['resolution'] < 150:
        return {'pass': False, 'reason': 'Resolution too low', 'results': results}
    
    # Contrast rejection happens at END (last step)
    
    if results['grid_detectability'] == 0:
        return {'pass': False, 'reason': 'No grid detected', 
                'recommendation': 'Try FFT method', 'results': results}
    
    return {'pass': True, 'results': results}
```

**UI Display:**
- Quality report panel showing all checks
- Color coding: Green (pass), Yellow (warn), Red (fail)
- Recommendations for failures
- Ability to proceed despite warnings (with confirmation)

---

### Step 2: Color Space Separation

**Purpose:** Handle ANY color combination (red grids, black grids, colored paper)

**Method 1: LAB Color Space (Default)**

**Process:**
1. Convert RGB → LAB
2. Extract L-channel (Lightness) → ECG trace (always darker)
3. Extract A-channel (Red/Green axis) → Grid if red/pink

**Implementation:**
```python
def color_separation_lab(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    # L-channel contains trace (dark = signal)
    trace_image = l_channel
    
    # A-channel shows red/green (red = positive = grid lines)
    grid_mask = a_channel > threshold  # Red grid lines
    
    return trace_image, grid_mask
```

**Method 2: HSV Color Space (Alternative)**

**Process:**
1. Convert RGB → HSV
2. Extract H-channel (Hue) → Isolate specific colors
3. Extract S-channel (Saturation) → Separate grid from signal

**UI Options:**
- Method selector: LAB (default) or HSV
- Color threshold sliders
- Preview mode to see separation results

**Handles:**
- ✅ Red/pink grid + black ECG (most common)
- ✅ Black grid + blue ECG
- ✅ Colored paper backgrounds
- ✅ Faded/aged ink

---

### Step 3: Illumination Normalization

**Purpose:** Remove lighting artifacts (shadows, yellowing, uneven illumination)

**Method 1: CLAHE (Contrast Limited Adaptive Histogram Equalization) - Default**

**Process:**
1. Apply CLAHE to boost local contrast
2. Makes faint grids visible
3. Handles uneven lighting

**Method 2: Background Subtraction**

**Process:**
1. Create background model using median blur
2. Divide original by background
3. Flattens lighting, whitens paper

**Method 3: Morphological Background Division**

**Process:**
1. Dilate image to remove lines
2. Use as illumination map
3. Divide original by illumination map

**UI Options:**
- Method selector dropdown
- CLAHE parameters (clip limit, tile size)
- Kernel size for morphological operations

**Handles:**
- ✅ Yellowed/aged paper
- ✅ Scanner shadows
- ✅ Uneven lighting from photos
- ✅ Dark corners/vignetting

---

### Step 4: Multi-Scale Grid Detection

**Purpose:** Detect both 1mm (small) and 5mm (large) grid lines

**Two-Pass Detection:**

**Pass 1: Fine Grid (1mm)**
- Small kernels: (1×10), (10×1)
- Detects thin grid lines

**Pass 2: Bold Grid (5mm)**
- Large kernels: (3×20), (20×3)
- Detects thick grid lines

**Validation:**
- Spacing ratio should be ~5:1 (5mm / 1mm)
- If ratio not correct, adjust detection parameters

**Output:**
- Combined grid map with both scales
- Separate lists: fine grid lines, bold grid lines
- Validation report

---

### Step 5: FFT-Based Grid Reconstruction

**Purpose:** Reconstruct missing grid sections using frequency analysis

**Process:**
1. Convert image to frequency domain (FFT)
2. Grid creates periodic peaks (bright spots)
3. Identify grid frequency peaks
4. Create perfect grid from frequencies
5. **Can reconstruct even if 40-60% of grid is missing!**

**Advantages:**
- Works when morphology fails
- Handles heavy occlusion (smudges)
- Reconstructs missing sections
- Very robust to noise

**Implementation:**
```python
def fft_grid_reconstruction(image):
    # Transform to frequency domain
    f = np.fft.fft2(image)
    fshift = np.fft.fftshift(f)
    
    # Find grid frequencies (will show as bright spots)
    magnitude = np.log(np.abs(fshift) + 1)
    
    # Identify peaks at grid spacing frequencies
    # Reconstruct perfect grid even if 40% is missing
    
    # Create grid from frequencies
    reconstructed_grid = reconstruct_from_frequencies(fshift, grid_frequencies)
    
    return reconstructed_grid
```

**Use Cases:**
- Heavy smudges covering grid
- Partial grid visibility
- Faded grids
- When other methods fail

**UI Options:**
- Toggle FFT reconstruction on/off
- Frequency filtering parameters
- Show frequency spectrum visualization

---

### Step 6: Adaptive Processing Pipeline

**Purpose:** 3-tier fallback strategy with automatic method selection

**Decision Logic:**

```
Attempt 1: Standard Pipeline
├─ Grayscale conversion
├─ Morphological filtering
└─ Score: 0.9 → SUCCESS ✓

If score < 0.7:
Attempt 2: LAB + CLAHE Pipeline
├─ LAB color separation
├─ CLAHE contrast boost
├─ Morphological filtering
└─ Score: 0.6 → Continue to Attempt 3

If score < 0.5:
Attempt 3: FFT Reconstruction
├─ FFT analysis
├─ Grid reconstruction
├─ Frequency filtering
└─ Score: 0.4 → Flag for manual review

If score < 0.3:
└─ Flag: "Unable to process - manual review needed"
```

**Features:**
- Try simple methods first (fast)
- Escalate to advanced methods if needed
- Always return best result
- Log which method worked

---

## Enhanced Error Handling & Validation

### Grid RMSE Validation

**Purpose:** Validates grid accuracy after detection

**Metrics:**
- **RMSE (Root Mean Square Error)**
  - Measures deviation from perfect grid
  - Target: < 2 pixels
  - Formula: `RMSE = sqrt(1/n * Σ(x_actual - x_ideal)²)`

- **Spacing Jitter**
  - Variance in grid line spacing
  - Should be consistent (1mm, 1mm, 1mm...)
  - Target: Jitter < 0.5px

- **Perpendicularity**
  - Angles should be exactly 90°
  - Deviation indicates poor detection
  - Target: < 2° deviation

**Quality Score:**
- RMSE < 2px & Jitter < 0.5px → Excellent (0.9-1.0)
- RMSE 2-5px & Jitter < 1px → Good (0.7-0.9)
- RMSE 5-10px → Fair (0.5-0.7)
- RMSE > 10px → Poor (<0.5) - Flag for review

---

### Rotation Sanity Checks

**Purpose:** Prevents false rotation detection

**Validation:**
1. Detect lines using Hough Transform
2. Cluster lines by angle
3. Expected: Two clusters at 0° and 90°
4. If lines scattered → FAILED (detected ECG waves, not grid)

**Requirements:**
- Horizontal cluster: angles near 0° or 180°
- Vertical cluster: angles near 90°
- Must have 3+ lines in each cluster
- Clusters must be ~90° apart

**If failed:**
- Don't rotate → Use original image
- Try FFT method instead

---

### Perspective Distortion Detection

**Purpose:** Automatically detect if perspective transform needed

**Check:**
1. Extend parallel lines
2. Find intersection points
3. If parallel lines converge → Perspective distortion!
4. Calculate vanishing point
5. Determine severity

**Decision:**
- No convergence → Use simple Affine transform
- Mild convergence → Use Homography
- Severe convergence → Flag + recommend re-scan

---

### RANSAC Outlier Rejection

**Purpose:** Filters phantom lines (noise or ECG waves detected as grid)

**Algorithm:**
1. Assume grid lines are equally spaced
2. Fit model: y_i = start + spacing × i
3. Lines that don't fit → Outliers (phantom lines)
4. Remove outliers
5. Keep only inliers (real grid lines)

**Benefits:**
- Removes noise-based false detections
- Removes ECG waves mistaken as lines
- Improves grid quality significantly

---

## Final Step: Low Contrast Rejection

**Purpose:** Final quality check - reject images with insufficient contrast

**Location:** LAST STEP in pipeline (after all transformations)

**Process:**
1. Calculate contrast after all preprocessing
2. Use histogram standard deviation
3. Threshold: Std < 30 → REJECT

**Implementation:**
```python
def final_contrast_rejection(image):
    """
    Final quality check - reject low contrast images
    This is the LAST step before signal extraction
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # Calculate histogram standard deviation
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    mean = np.mean(hist)
    std = np.std(hist)
    
    # Rejection threshold
    MIN_CONTRAST_STD = 30
    
    if std < MIN_CONTRAST_STD:
        return {
            'rejected': True,
            'reason': 'Low contrast - insufficient detail after processing',
            'contrast_std': std,
            'threshold': MIN_CONTRAST_STD,
            'recommendation': 'Please use higher quality scan or adjust preprocessing parameters'
        }
    
    return {
        'rejected': False,
        'contrast_std': std,
        'quality': 'excellent' if std > 50 else 'good' if std > 35 else 'fair'
    }
```

**UI Display:**
- Final contrast check result
- Contrast value (standard deviation)
- Rejection status with clear message
- Recommendation if rejected

**When Rejected:**
- Stop pipeline
- Show error message
- Offer options:
  - Adjust preprocessing parameters and retry
  - Use different preprocessing method
  - Manual review flag

---

## Complete Integrated Pipeline

**Updated Step Order:**

```
0. Assumptions (User Input)
   └─ Grid ratios, ECG lines count

1. Quality Gates (Pre-Processing)
   ├─ Blur detection
   ├─ Resolution check
   ├─ Contrast check (preliminary)
   └─ Grid detectability test

2. Color Space Separation
   ├─ LAB (default)
   └─ HSV (alternative)

3. Illumination Normalization
   ├─ CLAHE (default)
   ├─ Background subtraction
   └─ Morphological background division

4. Multi-Scale Grid Detection
   ├─ Fine grid (1mm)
   └─ Bold grid (5mm)

5. Smudge Detection & Removal
   ├─ Inpainting (default)
   └─ Morphological (alternative)

6. Rotation Correction
   └─ With sanity checks

7. FFT-Based Grid Reconstruction
   └─ If needed (adaptive)

8. Grid Line Detection
   ├─ Hough Lines (primary)
   └─ FFT Analysis (validation)

9. Grid Spacing Estimation
   └─ Using assumptions from Step 0

10. Affine/Homography Transform
    └─ With perspective detection

11. Grid RMSE Validation
    └─ Quality scoring

12. ECG Trace Extraction
    └─ Multiple methods

13. Apply Transform to Trace
    └─ Warp correction

14. Skeletonize
    └─ Centerline extraction

15. Convert to Signal (mV vs sec)
    └─ Time-series data

16. Low Contrast Rejection ⚠️ FINAL STEP
    └─ Final quality check
```

---

---

## 🚀 Stretch Goals: Competitive Performance & Advanced Features

### Performance Targets vs. State-of-the-Art

**Target Performance Metrics:**

| Metric | Target | Industry Average | Top Tools | Notes |
|--------|--------|------------------|-----------|-------|
| **PCC (Pearson)** | > 0.94 | ~0.93 | 0.954-0.977 | Competitive with top tools |
| **RMSE** | < 0.05 mV | ~0.10 | 0.001-0.10 | Better than most |
| **SNR (dB)** | > 25 dB | ~12 dB | 12.5-15 dB | **Primary competition metric** |
| **Grid RMSE** | < 2 pixels | N/A | N/A | Our unique metric |
| **Speed** | < 60s | 30-60s | 1-7s | Acceptable for batch |
| **Success Rate** | > 85% | ~65% | ~70% | On all image types |

**Competition Goal**: Top 15-20% leaderboard position

---

### Competitive Advantages

#### 1. Competition-Specific SNR Optimization

**Unique Focus:**
- Industry tools optimize for clinical accuracy (P-QRS-T intervals, diagnostic precision)
- **We optimize for SNR (competition primary metric)**
- Multi-method ensemble reduces noise accumulation
- Grid-first philosophy improves calibration accuracy

**Expected Improvement**: +10 dB SNR over industry average

#### 2. Grid-First Philosophy (Unique)

**Most Tools:**
- Remove grid as noise (e.g., ECGMiner step 2)
- Focus on signal extraction

**Our Approach:**
- **Grid is ground truth** - use for calibration
- 4 transformation methods to perfect grid alignment
- RMSE validation of grid quality before signal extraction
- Extract signal only after grid is perfectly aligned

**Advantage**: Better calibration = better SNR

#### 3. Multi-Method Ensemble (Unique)

**Signal Extraction Methods:**
```
Run 3 extraction methods in parallel:
├─ Column-wise scanning (fast, good for clean)
├─ Skeletonization (accurate centerline)
└─ Least-cost path (handles broken signals)

Ensemble Results:
└─ Weighted average by quality score
```

**Transformation Methods:**
```
Run 4 transformation methods in parallel:
├─ TPS (warped paper)
├─ Polynomial (smooth distortion)
├─ Perspective (angled photos)
└─ Barrel (lens distortion)

Select best based on combined score
```

**Advantage**: Averages out method-specific errors

#### 4. FFT Grid Reconstruction (Rare)

**Industry Status**: Research papers only, not in production tools

**Our Implementation:**
- Can reconstruct grid even if 40-60% is missing
- Frequency domain analysis finds periodic patterns
- Rebuilds perfect grid from partial information
- Handles heavily damaged images others can't process

**Use Cases:**
- Heavy smudges covering grid
- Partial grid visibility
- Faded grids
- When other methods fail

#### 5. Comprehensive Error Recovery

**3-Tier Adaptive Pipeline:**
```
Attempt 1: Standard Pipeline
├─ Grayscale conversion
├─ Morphological filtering
└─ Score: 0.9 → SUCCESS ✓

If score < 0.7:
Attempt 2: LAB + CLAHE Pipeline
├─ LAB color separation
├─ CLAHE contrast boost
├─ Morphological filtering
└─ Score: 0.6 → Continue to Attempt 3

If score < 0.5:
Attempt 3: FFT Reconstruction
├─ FFT analysis
├─ Grid reconstruction
├─ Frequency filtering
└─ Score: 0.4 → Flag for manual review
```

**Advantage**: Higher success rate on challenging images (85% vs 65%)

---

### Feature Comparison vs. State-of-the-Art

| Feature | ECGtizer | ECGMiner | PMcardio | **Our Pipeline** |
|---------|----------|----------|----------|------------------|
| **Colored Grid Handling** | Limited | Limited | Good | **Excellent** (LAB separation) |
| **Aged/Yellowed Paper** | Limited | Limited | Good | **Excellent** (Background division) |
| **Heavy Smudges** | Poor | Poor | Moderate | **Very Good** (Inpainting + FFT) |
| **Partial Grid** | Poor | Poor | Moderate | **Excellent** (FFT reconstruction) |
| **Smartphone Photos** | Good | Poor | Good | **Excellent** (Perspective detection) |
| **Grid Validation** | No | No | No | **Yes** (RMSE, orthogonality) |
| **Multi-Method Transforms** | No (1) | No (1) | No (1) | **Yes** (4 methods + selection) |
| **Signal Extraction Methods** | 3 options | 1 method | 1 method | **3 methods + ensemble** |
| **Error Recovery** | Limited | Limited | Good | **Excellent** (3-tier fallback) |
| **Quality Gates** | No | No | No | **Yes** (pre-flight checks) |
| **Competition SNR Focus** | No | No | No | **Yes** (primary goal) |

---

### Unique Features (Not in Other Tools)

#### 1. Quality Gates System (Unique)
**Purpose**: Catch bad images early, provide specific feedback

**Checks:**
- Blur detection (Laplacian variance < 100 → REJECT)
- Resolution check (DPI < 150 → REJECT)
- Contrast analysis (Std < 30 → WARN/REJECT)
- Grid detectability (0 lines → Route to FFT)

**Benefit**: Saves processing time, provides actionable feedback

#### 2. Grid RMSE Validation (Unique)
**Purpose**: Validate grid accuracy before signal extraction

**Metrics:**
- RMSE of intersection positions (target: < 2 pixels)
- Spacing jitter (target: < 0.5px)
- Perpendicularity (target: < 2° deviation)

**Benefit**: Catches bad grid detections before they ruin signal extraction

#### 3. Universal Preprocessing (Enhanced)
**Purpose**: Handle ANY image type regardless of color combination

**Methods:**
- LAB color space separation (red grids, black grids, any color)
- CLAHE illumination normalization (aged paper, shadows)
- Multi-scale detection (1mm + 5mm grids)
- FFT reconstruction (partial/missing grids)

**Benefit**: Works on images others can't process

#### 4. Adaptive Method Selection (Intelligent)
**Purpose**: Automatically choose best method based on image characteristics

**Decision Logic:**
```
Image has colored grid?
├─ Yes → LAB separation + FFT
└─ No → Continue

Image has low contrast?
├─ Yes → CLAHE + morphology
└─ No → Continue

Image has heavy smudges?
├─ Yes → Inpainting + FFT
└─ No → Continue

Image is smartphone photo?
├─ Yes → Perspective detection + TPS
└─ No → Continue

Default: Standard pipeline (grayscale + morphology)
```

**Benefit**: Optimal method for each image type

---

### Expected Performance Improvements

#### On Clean Images:
- **Industry**: PCC ~0.95-0.97, SNR ~12-15 dB
- **Ours**: PCC ~0.95, SNR ~20-25 dB
- **Improvement**: Similar PCC, **+10 dB SNR** (competition metric)

#### On Colored Grids:
- **Industry**: Often fails or requires manual intervention
- **Ours**: LAB separation → FFT → Success rate 85%
- **Improvement**: **+45% success rate**

#### On Damaged Images:
- **Industry**: 50% require manual review
- **Ours**: 3-tier fallback → Success rate 70%
- **Improvement**: **+20% success rate**

#### Overall Competition Performance:

| Scenario | Industry Average | Our Target | Improvement |
|----------|------------------|------------|-------------|
| Clean scans | SNR 15 dB | SNR 25 dB | **+10 dB** |
| Colored grids | SNR 8 dB | SNR 20 dB | **+12 dB** |
| Smudged images | SNR 5 dB | SNR 15 dB | **+10 dB** |
| **Competition Average** | **SNR 12 dB** | **SNR 22 dB** | **+10 dB** |

**Competition Impact**: +10 dB SNR → Move from **50th percentile to Top 15-20%**

---

### Stretch Goal Implementation Priority

#### Phase 1: Core Competitive Features (Weeks 3-4)
**Must-have for competition:**
1. ✅ Quality gates system
2. ✅ LAB color separation
3. ✅ CLAHE illumination normalization
4. ✅ Grid RMSE validation
5. ✅ Multi-method transformation selection
6. ✅ Signal extraction ensemble

**Expected**: +5 dB SNR improvement

#### Phase 2: Advanced Features (Weeks 4-5)
**Differentiation features:**
1. ✅ FFT grid reconstruction
2. ✅ Full adaptive pipeline
3. ✅ Comprehensive error recovery
4. ✅ Competition-specific SNR optimization

**Expected**: +3 dB additional SNR

#### Phase 3: Optimization (Weeks 5-6)
**Fine-tuning:**
1. ✅ Hyperparameter tuning
2. ✅ Method selection optimization
3. ✅ Ensemble weight tuning
4. ✅ Competition-specific tweaks

**Expected**: +2 dB additional SNR

**Total Expected**: **+10 dB SNR** → **Top 20% likely**

---

### Competitive Strategy

**Our Focus vs. Industry Focus:**

**Industry Tools Focus:**
- Clinical feature accuracy (P, Q, R, S, T intervals)
- Diagnostic precision (97.2%-99.1%)
- Medical validation
- Signal quality for diagnosis

**Our Competition Focus:**
- **SNR optimization** (competition primary metric)
- Perfect grid alignment (minimizes noise)
- Multi-method ensemble (averages errors)
- Signal completion (handles gaps)

**Why This Works:**
1. **Competition metric = SNR** (we optimize directly for this)
2. **Grid-first = better calibration** (reduces systematic error)
3. **Ensemble = noise reduction** (averages random errors)
4. **Error recovery = higher success** (more images processed)

---

### Integration with Existing Pipeline

**These are enhancements, not replacements:**

```
# Existing Pipeline (still works):
existing_pipeline(image)

# Enhanced Version (adds layers):
quality_gates(image) → 
universal_preprocessing(image) → 
existing_pipeline(image) → 
validation(result) → 
multi_method_ensemble(results) → 
signal_extraction_ensemble(image)
```

**Nothing gets deleted, everything gets better!**

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2026 | Initial specification |
| 1.1 | Jan 2026 | Added Test/Production mode, Universal Preprocessing, Low Contrast Rejection |
| 1.2 | Jan 2026 | Added Stretch Goals: Competitive Performance & Advanced Features |

---

## Notes

- All transformation methods should be reversible or save original state
- Intermediate results should be stored for undo/redo
- Parameters should be serializable for saving/loading presets
- Consider performance optimization for large images
- Mobile-friendly controls and layouts
- **Test Mode:** Allows debugging and manual control
- **Production Mode:** Fully automatic execution
- **Low Contrast Rejection:** Always performed as final step before signal extraction

---

**Document Owner:** Development Team  
**Review Cycle:** Sprint Planning  
**Next Review:** End of Sprint 1
