# ECG Image Processing Stages and Calculations

This document lists all processing stages, calculations, and outputs that should be generated during ECG image processing.

## Processing Pipeline Overview

The ECG image processing pipeline consists of multiple stages, each producing specific outputs and metrics.

---

## Stage 1: Image Loading and Validation

**Purpose**: Load image from GCS and validate it can be processed

**Outputs**:
- `image_loaded`: boolean - Whether image was successfully loaded
- `image_dimensions`: {width, height} - Image size in pixels
- `image_format`: string - Image format (PNG, JPEG, etc.)
- `file_size_bytes`: number - Original file size
- `load_error`: string | null - Error message if loading failed

---

## Stage 2: Quality Gates

**Purpose**: Check if image meets minimum quality requirements

**Outputs**:
- `quality_passed`: boolean - Whether all quality checks passed
- `blur_score`: number - Blur detection score (higher = less blur)
- `dpi`: number - Estimated DPI/resolution
- `contrast_std`: number - Standard deviation of contrast (higher = better contrast)
- `grid_lines_count`: number - Number of grid lines detected
- `warnings`: array<string> - List of quality warnings
- `quality_failed_reason`: string | null - Reason if quality check failed

---

## Stage 3: Color Analysis

**Purpose**: Detect and analyze colors in the image (red, black, etc.)

**Outputs**:
- `has_red`: boolean - Whether red/pink colors are detected
- `has_black`: boolean - Whether black colors are detected
- `has_both_colors`: boolean - Whether BOTH red AND black are present
- `dominant_color`: string - 'red', 'black', 'both', or 'unknown'
- `color_separation_required`: boolean - Whether color separation will be performed
- `split_image_will_be_generated`: boolean - Whether a split image will be created
- `red_pixel_count`: number - Number of red pixels detected
- `black_pixel_count`: number - Number of black pixels detected
- `color_distribution`: object - Detailed color analysis

**Special Case**: When `has_both_colors === true`:
- `split_image_will_be_generated` should be `true`
- Output should indicate that color separation will create separate images for red and black components

---

## Stage 4: Edge Detection

**Purpose**: Detect edges and find content boundaries

**Outputs**:
- `edges_detected`: boolean - Whether edges were found
- `bounding_box`: {x, y, width, height} - Bounding box of content
- `edge_pixels`: number - Number of edge pixels detected
- `edge_detection_method`: string - Method used ('canny', 'sobel', etc.)
- `content_area_percentage`: number - Percentage of image containing content

---

## Stage 5: Color Separation

**Purpose**: Separate grid from ECG trace based on color

**Outputs**:
- `separation_method`: string - Method used ('lab', 'hsv')
- `grid_color_detected`: string - 'red', 'black', or 'both'
- `trace_pixels`: number - Number of pixels identified as ECG trace
- `grid_pixels`: number - Number of pixels identified as grid
- `separation_quality`: number - Quality score (0-1) of separation
- `channel_contrast`: number - Contrast in separated channel
- `grid_isolation`: number - How well grid was isolated (0-1)
- `trace_image_generated`: boolean - Whether trace-only image was created
- `grid_image_generated`: boolean - Whether grid-only image was created
- `split_images_generated`: boolean - Whether split images were created (when red AND black detected)

**When Red AND Black Detected**:
- `split_images_generated` = `true`
- Output should include:
  - `red_component_image`: URL or base64 - Image with red components
  - `black_component_image`: URL or base64 - Image with black components
  - `combined_processed_image`: URL or base64 - Combined processed image

---

## Stage 6: Illumination Normalization

**Purpose**: Normalize brightness and illumination across image

**Outputs**:
- `normalization_method`: string - Method used ('clahe', 'background_subtract', 'morphological')
- `brightness_variance`: number - Variance in brightness after normalization
- `normalized_range`: number - Range of pixel values after normalization
- `uniformity_score`: number - How uniform illumination is (0-1, higher = more uniform)
- `normalization_applied`: boolean - Whether normalization was performed

---

## Stage 7: Grid Detection

**Purpose**: Detect and analyze ECG grid lines

**Outputs**:
- `grid_detected`: boolean - Whether grid was detected
- `fine_lines`: number - Number of 1mm grid lines detected
- `bold_lines`: number - Number of 5mm grid lines detected
- `detection_quality`: number - Quality score of grid detection (0-1)
- `grid_spacing_mm`: number - Detected grid spacing in mm
- `grid_angle`: number - Rotation angle of grid (degrees)
- `grid_lines`: object - Detailed line information

---

## Stage 8: Smudge Detection and Removal

**Purpose**: Detect and remove smudges, artifacts, and noise

**Outputs**:
- `smudges_detected`: boolean - Whether smudges were found
- `smudge_count`: number - Number of smudge regions detected
- `area_cleaned`: number - Percentage of image area cleaned
- `grid_preserved`: boolean - Whether grid was preserved during cleaning
- `smudge_mask_generated`: boolean - Whether smudge mask was created
- `cleaning_method`: string - Method used ('inpainting', 'morphological')

---

## Stage 9: Rotation Correction

**Purpose**: Correct image rotation and alignment

**Outputs**:
- `rotation_detected`: boolean - Whether rotation was detected
- `rotation_angle`: number - Detected rotation angle (degrees)
- `correction_applied`: boolean - Whether correction was applied
- `alignment_score`: number - Alignment quality after correction (0-1)

---

## Stage 10: Signal Extraction

**Purpose**: Extract ECG signal waveforms from image

**Outputs**:
- `signals_extracted`: boolean - Whether signals were extracted
- `lead_count`: number - Number of ECG leads detected
- `leads_detected`: array<string> - List of lead names (I, II, III, aVR, etc.)
- `sampling_rate`: number - Extracted sampling rate (Hz)
- `duration_seconds`: number - Duration of signal in seconds
- `signal_quality`: number - Overall signal quality (0-1)

---

## Stage 11: Quality Metrics Calculation

**Purpose**: Calculate final quality metrics

**Outputs**:
- `snr_db`: number - Signal-to-Noise Ratio in dB
- `image_type`: string - Type of image ('standard', 'colored', 'scanned', etc.)
- `contrast`: number - Overall contrast score
- `smudges`: object - Smudge analysis
  - `smudge_count`: number
  - `qualitative`: string - 'none', 'low', 'medium', 'high'
- `overall_quality`: number - Overall quality score (0-1)

---

## Complete Processing Result Structure

Each processed image should return a result object with this structure:

```json
{
  "success": true,
  "name": "1006427285-0003.png",
  "original_name": "1006427285-0003.png",
  "original_url": "https://storage.googleapis.com/...",
  "processed_url": "https://storage.googleapis.com/...",
  "path": "kaggle-data/physionet-ecg/train/1006427285-0003.png",
  "bucket": "ecg-competition-data-4",
  "steps": {
    "image_loading": {
      "image_loaded": true,
      "image_dimensions": {"width": 1920, "height": 1080},
      "image_format": "PNG",
      "file_size_bytes": 245678
    },
    "quality_gates": {
      "quality_passed": true,
      "blur_score": 85.3,
      "dpi": 300,
      "contrast_std": 45.2,
      "grid_lines_count": 120
    },
    "color_analysis": {
      "has_red": true,
      "has_black": true,
      "has_both_colors": true,
      "dominant_color": "both",
      "color_separation_required": true,
      "split_image_will_be_generated": true,
      "red_pixel_count": 125000,
      "black_pixel_count": 98000
    },
    "edge_detection": {
      "edges_detected": true,
      "bounding_box": {"x": 50, "y": 30, "width": 1800, "height": 1000},
      "edge_pixels": 45000,
      "edge_detection_method": "canny"
    },
    "color_separation": {
      "separation_method": "lab",
      "grid_color_detected": "both",
      "trace_pixels": 98000,
      "grid_pixels": 125000,
      "separation_quality": 0.92,
      "split_images_generated": true,
      "red_component_image": "https://...",
      "black_component_image": "https://...",
      "combined_processed_image": "https://..."
    },
    "grid_detection": {
      "grid_detected": true,
      "fine_lines": 100,
      "bold_lines": 20,
      "detection_quality": 0.88
    },
    "smudge_removal": {
      "smudges_detected": true,
      "smudge_count": 5,
      "area_cleaned": 2.3,
      "grid_preserved": true
    }
  },
  "metrics": {
    "snr_db": 25.4,
    "image_type": "colored",
    "contrast": 0.75,
    "smudges": {
      "smudge_count": 5,
      "qualitative": "low"
    },
    "overall_quality": 0.85
  },
  "analysis": {
    "processing_time_ms": 1250,
    "stages_completed": 11,
    "warnings": [],
    "errors": []
  }
}
```

---

## Important Notes

1. **Red AND Black Detection**: When both red and black are detected, the system MUST:
   - Set `has_both_colors = true`
   - Set `split_image_will_be_generated = true`
   - Generate separate images for red and black components
   - Include URLs for both split images in the output

2. **All Stages Must Output**: Every stage should produce output, even if:
   - The stage was skipped (output `skipped: true`)
   - The stage failed (output `success: false` with error message)
   - No relevant data was found (output with `detected: false`)

3. **Error Handling**: Each stage should handle errors gracefully and include:
   - `success`: boolean
   - `error`: string | null
   - `error_type`: string | null

4. **Missing Data**: If a calculation cannot be performed, output `null` or `undefined` rather than omitting the field.

---

## Backend Implementation Requirements

The backend processing function (`/process-gcs-batch`) should:

1. Execute all stages in sequence
2. Capture outputs from each stage
3. Return complete results with all stage outputs
4. Handle errors at each stage without stopping the pipeline
5. Generate split images when red AND black are detected
6. Include all URLs for generated images (original, processed, split images)
