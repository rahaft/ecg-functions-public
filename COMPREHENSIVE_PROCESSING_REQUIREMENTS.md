# Comprehensive Processing Requirements

## Overview
Complete image processing pipeline with SNR calculation, comparison UI, and temporary file management.

---

## Processing Steps

### 1. Image Type Detection
- **Black & White**: Grayscale only
- **Red & Black & White**: Contains red grid lines
- Detection method: Color space analysis (HSV/LAB)

### 2. Edge Detection
- Detect image boundaries
- Methods: Canny, Sobel, Laplacian, Contour
- Return bounding box and edge metrics

### 3. Contrast Analysis
- Calculate current contrast (std dev of pixel values)
- Determine if contrast can be improved
- Suggest enhancement methods (CLAHE, histogram equalization)

### 4. Smudge Detection
- Use multiple models/methods
- **Quantitative**: Number of smudges, area covered, density
- **Qualitative**: "No smudges", "Some smudges", "Many smudges", "Heavy smudges"

### 5. Color Separation (Conditional)
- **Only if both black AND red present**
- Three methods: OpenCV, Pillow, scikit-image
- Separate black (signal + text) from red (grid)
- Remove handwritten/typed text from black channel
- Result: Red grid only, Black signal only

### 6. Red Grid Analysis
- Count black dots on red grid for each method
- Calculate average distance to nearest pixel (diagonal allowed) × 100000
- Select method with smallest nearest neighbor sum
- Mark with `-keep-` in filename

---

## File Naming Convention

Format: `{original_name}-{type}-{metrics}.{ext}`

- `-a-`: All (original image)
- `-s-`: Split (red/black separation)
- `-e-`: Edge detection
- `-keep-`: Best method (smallest nearest neighbor)
- Metrics: `-{black_dot_count}-{nearest_neighbor_value}-`

Example:
- `image-0001-a-.png` (original)
- `image-0001-s-opencv-1234-56789000-.png` (opencv method, 1234 dots, 56789000 nearest neighbor)
- `image-0001-s-opencv-1234-56789000-keep-.png` (best method)
- `image-0001-e-canny-.png` (edge detection)

---

## SNR Calculation

Compare transformed images to base image (ending in `-0001`):

```
SNR = 10 * log10(signal_power / noise_power)

Where:
- signal_power = variance of base image signal
- noise_power = variance of difference (transformed - base)
```

Display:
- SNR value (dB)
- Visual comparison
- Per-method SNR comparison

---

## UI Components

### Gallery Header
- **Batch Transform Button**: Process all images in group
- Shows image set number/prefix
- Progress indicator

### Comparison Screen
- **Left Panel**: Original image
- **Right Panel**: Transformed image(s)
- **Metrics Panel**: 
  - SNR value
  - Image type (B&W vs Red/Black/White)
  - Contrast score
  - Smudge count (quantitative + qualitative)
  - Black dot count (for red grid)
  - Nearest neighbor distance
- **Toggle Checkboxes**:
  - ☑ Show edges
  - ☑ Show smudges
  - ☑ Show grid lines
- **Navigation**:
  - ← Previous image
  - → Next image
  - Thumbnail strip at top (with preview)
- **Save Button**: Make temporary files permanent

---

## Temporary File Management

- Files saved with 1-hour TTL
- Auto-delete after 1 hour unless saved
- Save button marks files as permanent
- Store in GCS with metadata:
  - `temporary: true`
  - `expires_at: timestamp + 1 hour`
  - `saved: false`

---

## Kaggle Compliance

- ✅ No internet access
- ✅ All processing local
- ✅ No external API calls
- ✅ Use only allowed packages

---

## Version Auto-Increment

Deploy script automatically increments version:
- Current: `2.3.4`
- After deploy: `2.3.5`
- Format: `MAJOR.MINOR.PATCH`
