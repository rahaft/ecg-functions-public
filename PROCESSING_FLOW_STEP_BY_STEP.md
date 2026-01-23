# ECG Image Processing Flow - Step by Step

## Complete Processing Pipeline with Outputs

This document shows the exact step-by-step flow of the ECG image processing pipeline, with outputs and metrics at each stage.

---

## Main Execution Flow

### 1. Environment Initialization
**Purpose**: Load libraries and define global parameters

**Actions**:
- Load libraries: `cv2`, `numpy`, `skimage`, `scipy`, `matplotlib`
- Define HSV color bounds for ECG grid removal
- Set Canny thresholds (low, high)
- Define Gaussian kernel sizes
- Initialize configuration parameters

**Output**:
```python
{
    'status': 'initialized',
    'libraries_loaded': ['cv2', 'numpy', 'skimage', 'scipy', 'matplotlib'],
    'config': {
        'hsv_lower': [0, 0, 0],
        'hsv_upper': [180, 255, 100],
        'canny_low': 50,
        'canny_high': 150,
        'gaussian_kernel': (3, 3),
        'gaussian_sigma': 0
    }
}
```

**Metrics**: None (initialization only)

---

### 2. Image Loading & Input Validation
**Purpose**: Ingest raw scan and validate format

**Actions**:
- Load image from file path or array
- Check file format (PNG, JPG, etc.)
- Validate image dimensions (width, height)
- Check color channels (BGR/RGB/Grayscale)
- Verify image is not empty

**Output**:
```python
{
    'status': 'loaded',
    'image_shape': (height, width, channels),
    'image_dtype': 'uint8',
    'file_format': 'PNG',
    'file_size_bytes': 1234567,
    'dimensions_valid': True,
    'format_valid': True
}
```

**Metrics**:
- Image dimensions (width, height)
- File size
- Color channels count
- Validation status

---

### 3. Pre-processing Pipeline (Universal)
**Purpose**: Prepare image for edge detection

#### 3.1 Color Masking (HSV Segmentation)
**Actions**:
- Convert BGR to HSV color space
- Apply HSV mask to isolate signal (black/blue) from red background grid
- Remove red/pink grid lines
- Keep only ECG trace signal

**Output**:
```python
{
    'step': 'color_masking',
    'masked_image': np.ndarray,  # Image with grid removed
    'mask': np.ndarray,  # Binary mask
    'signal_pixels': 12345,  # Count of signal pixels
    'grid_pixels_removed': 5678,  # Count of removed grid pixels
    'mask_effectiveness': 0.68  # Ratio of signal to total
}
```

**Metrics**:
- Signal pixel count
- Grid pixels removed
- Mask effectiveness ratio
- Color space conversion time

#### 3.2 Grayscale Conversion
**Actions**:
- Convert masked color image to grayscale
- Preserve signal intensity

**Output**:
```python
{
    'step': 'grayscale_conversion',
    'grayscale_image': np.ndarray,
    'mean_intensity': 127.5,
    'std_intensity': 45.2
}
```

**Metrics**:
- Mean intensity
- Standard deviation of intensity
- Conversion time

#### 3.3 Denoising (Gaussian Blur)
**Actions**:
- Apply Gaussian blur to eliminate high-frequency scanning artifacts
- Reduce noise while preserving edges

**Output**:
```python
{
    'step': 'denoising',
    'blurred_image': np.ndarray,
    'kernel_size': (3, 3),
    'sigma': 0,
    'noise_reduction': 0.15  # Estimated noise reduction
}
```

**Metrics**:
- Noise reduction percentage
- Blur parameters used
- Processing time

#### 3.4 Normalization (Adaptive Thresholding)
**Actions**:
- Apply adaptive thresholding to correct for uneven scanner lighting
- Normalize intensity across image

**Output**:
```python
{
    'step': 'normalization',
    'normalized_image': np.ndarray,
    'adaptive_method': 'GAUSSIAN_C',
    'block_size': 11,
    'C': 2,
    'illumination_corrected': True
}
```

**Metrics**:
- Illumination correction effectiveness
- Threshold parameters
- Processing time

**Final Pre-processing Output**:
```python
{
    'preprocessing_complete': True,
    'clean_image': np.ndarray,  # Final preprocessed image
    'steps': {
        'color_masking': {...},
        'grayscale': {...},
        'denoising': {...},
        'normalization': {...}
    },
    'total_preprocessing_time': 0.234  # seconds
}
```

---

### 4. Parallel Edge Detection Benchmarking
**Purpose**: Generate three edge maps using different methods

#### 4.1 Branch A: Canny Edge Detection
**Optimization**: Line continuity

**Actions**:
- Apply Canny edge detection with adaptive thresholds
- Optimize for continuous ECG signal lines
- Apply morphological operations for cleanup

**Output**:
```python
{
    'method': 'canny',
    'edge_map': np.ndarray,  # Binary edge map
    'params': {
        'low_threshold': 50,
        'high_threshold': 150,
        'aperture_size': 3,
        'l2_gradient': False
    },
    'edge_pixels': 12345,
    'processing_time': 0.045
}
```

**Metrics**:
- Edge pixel count
- Processing time
- Threshold values used

#### 4.2 Branch B: Sobel Edge Detection
**Optimization**: Vertical/horizontal document boundaries

**Actions**:
- Calculate Sobel gradients (X and Y directions)
- Combine gradients
- Apply percentile-based thresholding

**Output**:
```python
{
    'method': 'sobel',
    'edge_map': np.ndarray,
    'sobel_x': np.ndarray,  # X-direction gradient
    'sobel_y': np.ndarray,  # Y-direction gradient
    'params': {
        'ksize': 3,
        'dx': 1,
        'dy': 1
    },
    'edge_pixels': 15678,
    'processing_time': 0.038
}
```

**Metrics**:
- Edge pixel count
- Gradient magnitudes
- Processing time

#### 4.3 Branch C: Laplacian Edge Detection
**Optimization**: Fine details and rapid intensity changes

**Actions**:
- Apply Laplacian operator
- Calculate second derivative
- Apply percentile-based thresholding

**Output**:
```python
{
    'method': 'laplacian',
    'edge_map': np.ndarray,
    'params': {
        'ksize': 3,
        'scale': 1,
        'delta': 0
    },
    'edge_pixels': 18923,
    'processing_time': 0.042
}
```

**Metrics**:
- Edge pixel count
- Processing time
- Kernel size used

**Parallel Benchmarking Output**:
```python
{
    'benchmarking_complete': True,
    'methods': {
        'canny': {...},
        'sobel': {...},
        'laplacian': {...}
    },
    'total_benchmark_time': 0.125  # seconds (parallel execution)
}
```

---

### 5. Quantitative Evaluation (The Benchmark)
**Purpose**: Calculate metrics to identify the best method

**Actions**:
- Calculate Edge Density for each method
- Calculate Connectivity Scores (number and length of continuous contours)
- Calculate Salt-Pepper Noise
- Calculate Line Continuity
- Compare all three methods

**Output**:
```python
{
    'evaluation_complete': True,
    'metrics': {
        'canny': {
            'edge_density': 12.45,  # Percentage
            'connectivity': {
                'num_contours': 45,
                'largest_contour_area': 1234,
                'total_contour_area': 5678
            },
            'salt_pepper_noise': 8.23,  # Percentage (lower is better)
            'line_continuity': 85.67  # Percentage (higher is better)
        },
        'sobel': {
            'edge_density': 15.32,
            'connectivity': {...},
            'salt_pepper_noise': 12.45,
            'line_continuity': 72.34
        },
        'laplacian': {
            'edge_density': 18.76,
            'connectivity': {...},
            'salt_pepper_noise': 15.67,
            'line_continuity': 68.23
        }
    },
    'recommendations': {
        'document_detection': 'sobel',  # Lowest noise
        'ecg_signal_extraction': 'canny'  # Highest continuity
    }
}
```

**Metrics Table** (Printed):
```
================================================================================
EDGE DETECTION METHOD COMPARISON
================================================================================
Method          Density %    Contours    Noise %      Continuity %    
--------------------------------------------------------------------------------
canny           12.45        45          8.23          85.67
sobel           15.32        38          12.45         72.34
laplacian       18.76        52          15.67         68.23
================================================================================

RECOMMENDATIONS:
  Document Boundaries: sobel (lowest noise: 8.23%)
  ECG Signal Extraction: canny (highest continuity: 85.67%)
```

---

### 6. Task-Specific Extraction (Using the Best Method)

#### 6.1 Document Extraction
**Method Used**: Sobel or Canny (based on evaluation)

**Actions**:
- Find largest 4-vertex contour from edge map
- Extract corner points
- Apply Perspective Transform to "flatten" the page
- Correct for paper warping

**Output**:
```python
{
    'task': 'document_extraction',
    'method_used': 'sobel',
    'document_found': True,
    'corners': [
        [x1, y1],  # Top-left
        [x2, y2],  # Top-right
        [x3, y3],  # Bottom-right
        [x4, y4]   # Bottom-left
    ],
    'document_area': 1234567,  # pixels
    'perspective_transform': np.ndarray,  # 3x3 transformation matrix
    'warping_corrected': True
}
```

**Metrics**:
- Document area
- Corner coordinates
- Transform matrix
- Warping correction status

#### 6.2 Signal Extraction
**Method Used**: Canny (based on evaluation)

**Actions**:
- Take the Canny edge map
- Apply `skimage.morphology.skeletonize` for 1-pixel-wide lines
- Extract (x, y) coordinates
- Run Thin Plate Spline (TPS) correction to fix paper warping
- Convert to time-series data

**Output**:
```python
{
    'task': 'signal_extraction',
    'method_used': 'canny',
    'skeletonized': np.ndarray,  # 1-pixel-wide skeleton
    'coordinates': [
        (x1, y1),
        (x2, y2),
        ...
    ],
    'num_points': 12345,
    'tps_correction_applied': True,
    'corrected_coordinates': [
        (x1_corrected, y1_corrected),
        ...
    ],
    'time_series': {
        'x': np.ndarray,  # Time values
        'y': np.ndarray,  # Voltage values
        'sampling_rate': 500  # Hz (estimated)
    }
}
```

**Metrics**:
- Number of extracted points
- Signal length
- Sampling rate (estimated)
- TPS correction effectiveness

---

### 7. Output & Visualization
**Purpose**: Generate visualizations and save results

#### 7.1 Plot 2x2 Comparison Grid
**Actions**:
- Create Matplotlib figure with 2x2 grid
- Show: Original | Canny | Sobel | Laplacian
- Add titles and labels

**Output**:
- Saved image: `edge_detection_comparison.png`
- Figure object for display

#### 7.2 Print Performance Summary Table
**Actions**:
- Format and print metrics table
- Show recommendations

**Output**:
- Console output (see Section 5)

#### 7.3 Save Digitized Signal
**Actions**:
- Save as CSV file
- Save as NumPy array (.npy)
- Include metadata

**Output**:
```python
{
    'files_saved': {
        'csv': 'ecg_signal.csv',
        'numpy': 'ecg_signal.npy',
        'visualization': 'edge_detection_comparison.png',
        'document_corners': 'document_corners.json'
    },
    'signal_data': {
        'num_points': 12345,
        'duration_seconds': 24.69,
        'sampling_rate': 500
    }
}
```

---

## Complete Pipeline Summary

### Input
- Raw ECG scan image (PNG/JPG)

### Processing Steps
1. ✅ Environment Initialization
2. ✅ Image Loading & Validation
3. ✅ Pre-processing (Color Masking → Grayscale → Denoising → Normalization)
4. ✅ Parallel Edge Detection (Canny, Sobel, Laplacian)
5. ✅ Quantitative Evaluation
6. ✅ Task-Specific Extraction (Document + Signal)
7. ✅ Output & Visualization

### Output
- Edge detection comparison visualization
- Document corner coordinates
- Digitized ECG signal (CSV + NumPy)
- Performance metrics table
- Recommendations for best method

### Total Processing Time
- Typical: 0.5 - 2.0 seconds per image
- Breakdown:
  - Pre-processing: ~0.2s
  - Edge Detection (parallel): ~0.1s
  - Evaluation: ~0.05s
  - Extraction: ~0.1s
  - Visualization: ~0.05s

---

## Data Flow Diagram

```
Raw Image
    ↓
[1. Initialization]
    ↓
[2. Load & Validate]
    ↓
[3. Pre-processing]
    ├─→ Color Masking (HSV)
    ├─→ Grayscale
    ├─→ Denoising (Gaussian Blur)
    └─→ Normalization (Adaptive Threshold)
    ↓
[4. Parallel Edge Detection]
    ├─→ Canny (continuity)
    ├─→ Sobel (boundaries)
    └─→ Laplacian (details)
    ↓
[5. Evaluation]
    ├─→ Edge Density
    ├─→ Connectivity
    ├─→ Noise Analysis
    └─→ Continuity Score
    ↓
[6. Extraction]
    ├─→ Document (Sobel/Canny)
    └─→ Signal (Canny + Skeletonize + TPS)
    ↓
[7. Output]
    ├─→ Visualization (2x2 grid)
    ├─→ CSV file
    └─→ NumPy array
```

---

## Key Metrics at Each Stage

| Stage | Key Metrics | Purpose |
|-------|-------------|---------|
| **Initialization** | Config parameters | Setup |
| **Loading** | Dimensions, format | Validation |
| **Pre-processing** | Signal pixels, noise reduction | Quality |
| **Edge Detection** | Edge pixels, processing time | Performance |
| **Evaluation** | Density, connectivity, noise, continuity | Comparison |
| **Extraction** | Points extracted, correction status | Results |
| **Output** | Files saved, data size | Completion |

---

## Next Steps

1. Run the main processing script
2. Review metrics at each stage
3. Compare method performance
4. Use recommended method for final extraction
5. Export digitized signal for analysis
