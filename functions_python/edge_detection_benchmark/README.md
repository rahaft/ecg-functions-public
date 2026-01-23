# Edge Detection Benchmarking Suite

## Overview

A comprehensive Python benchmarking system to evaluate three edge detection methods (Canny, Sobel, Laplacian) for two distinct tasks:
1. **Document Boundary Detection** - Finding 4-corner document boundaries
2. **ECG Signal Extraction** - Extracting clean, digitized 1D signals from ECG images

## Structure

### Core Modules

- **`preprocessor.py`** - `PreProcessor` class: Image loading, HSV masking, noise reduction
- **`edge_benchmarker.py`** - `EdgeBenchmarker` class: Canny, Sobel, Laplacian implementations
- **`metrics_calculator.py`** - `MetricsCalculator` class: Quantitative comparison metrics
- **`extraction_engine.py`** - `ExtractionEngine` class: Document and ECG signal extraction
- **`visualizer.py`** - `Visualizer` class: Matplotlib visualization utilities

### Individual Scripts (6 Total)

#### Document Boundary Detection (3 scripts)
1. **`document_canny.py`** - Canny method for document boundaries
2. **`document_sobel.py`** - Sobel method for document boundaries
3. **`document_laplacian.py`** - Laplacian method for document boundaries

#### ECG Signal Extraction (3 scripts)
4. **`ecg_signal_canny.py`** - Canny method for ECG signal (optimized for continuity)
5. **`ecg_signal_sobel.py`** - Sobel method for ECG signal
6. **`ecg_signal_laplacian.py`** - Laplacian method for ECG signal

### Benchmarking Script

- **`benchmark_all.py`** - Runs all 6 methods and compares results

## Usage

### Run Individual Method

```bash
# Document detection with Canny
python functions_python/edge_detection_benchmark/document_canny.py image.png output_dir/

# ECG signal extraction with Canny
python functions_python/edge_detection_benchmark/ecg_signal_canny.py image.png output_dir/
```

### Run Complete Benchmark

```bash
# Compare all methods for both tasks
python functions_python/edge_detection_benchmark/benchmark_all.py image.png output_dir/
```

## Processing Pipeline

### Document Boundary Detection

```
1. Load Image
   ↓
2. Preprocess (Grayscale + Gaussian Blur)
   ↓
3. Edge Detection (Canny/Sobel/Laplacian)
   ↓
4. Find Largest 4-Vertex Contour
   ↓
5. Extract Corner Points
   ↓
6. Calculate Metrics & Visualize
```

### ECG Signal Extraction

```
1. Load Image
   ↓
2. Preprocess (Grayscale + Gaussian Blur + HSV Masking)
   ↓
3. Isolate Signal (Remove Red/Pink Grid)
   ↓
4. Edge Detection (Canny/Sobel/Laplacian)
   ↓
5. Skeletonization (1-pixel-wide lines)
   ↓
6. Extract (x, y) Coordinates
   ↓
7. Optional: Geometric Correction (TPS/Affine)
   ↓
8. Calculate Metrics & Visualize
```

## Methods Comparison

### Canny Edge Detection
- **Best for**: ECG Signal Extraction (produces continuous lines)
- **Optimization**: Adaptive thresholds, morphological cleanup
- **Output**: Binary edge map with bounding box

### Sobel Operator
- **Best for**: Document Boundary Detection (better at finding paper edges)
- **Optimization**: Directional gradients (X and Y)
- **Output**: Combined gradient magnitude

### Laplacian Operator
- **Best for**: Detecting sharp transitions and fine details
- **Optimization**: Second derivative for rapid intensity changes
- **Output**: Binary edge map

## Metrics Calculated

1. **Edge Density**: Percentage of edge pixels (0-100%)
2. **Connectivity Score**: Number of continuous contours
3. **Salt-Pepper Noise**: Percentage of isolated edge pixels (lower is better)
4. **Line Continuity**: Measure of line continuity (higher is better)

## Output Files

When run with output directory:

### Document Detection
- `document_{method}_edges.png` - Edge detection result
- `document_{method}_visualization.png` - Visualization with corners

### ECG Signal Extraction
- `ecg_signal_{method}_edges.png` - Edge detection result
- `ecg_signal_{method}_skeleton.png` - Skeletonized signal
- `ecg_signal_{method}_visualization.png` - Complete visualization

### Comparison
- `document_comparison.png` - 2x2 grid comparing all methods for document
- `ecg_signal_comparison.png` - 2x2 grid comparing all methods for ECG signal

## Dependencies

```python
numpy>=1.23.0
opencv-python>=4.8.0
matplotlib>=3.7.0
scikit-image>=0.20.0  # For skeletonization
scipy>=1.10.0  # For TPS correction (optional)
```

## Integration with Main Pipeline

These scripts can be integrated into the main processing pipeline by:

1. Importing the functions in `main.py`
2. Adding API endpoints for each method
3. Storing results in the response structure
4. Updating the gallery UI to show method comparisons

## Example Output

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
