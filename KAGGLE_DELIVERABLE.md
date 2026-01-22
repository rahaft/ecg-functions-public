# Kaggle Competition Deliverable Tracker

## Competition: PhysioNet - Digitization of ECG Images

**Competition URL:** https://kaggle.com/competitions/physionet-ecg-image-digitization  
**Host:** PhysioNet  
**Status:** Active Competition (2025 rerun of 2024 PhysioNet Challenge)

---

## 1. Competition Overview

### Objective
Build models to **extract time series data from ECG images**. Convert paper ECG printouts, scans, and photographs back into digital time-series signals that can be used with modern medical-grade ECG analysis software.

### Why This Matters
- **Billions** of hard copy ECGs exist globally (printouts, scans, photos)
- Current medical AI tools only work on time-series data, not images
- Digitizing historical ECGs could unlock decades of cardiovascular data
- Improved diagnosis and treatment, especially in areas with limited digital infrastructure

### Key Challenges
| Challenge | Description |
|-----------|-------------|
| **Imaging Artifacts** | Misalignments, rotations, reflections, aspect ratio issues, blurring, varied scanning resolutions |
| **Multi-lead Complexity** | 12-lead ECGs with specific interrelationships based on electrode placement |
| **Vendor Variability** | Different ECG machine vendors use different layouts, grid sizes, and formatting |
| **Signal Noise** | Original time-series data may have been noisy before printing |
| **Sampling Variations** | Different sampling frequencies and signal lengths across sources |

---

## 2. Deliverable Requirements

### Submission Format

#### File Format
- **Filename:** `submission.parquet` OR `submission.csv`
- **Required columns:** `id`, `value`

#### Structure
```csv
id,value
'62_0_I',0.0
'62_1_II',0.3
'62_2_I',0.4
...
```

#### ID Format
The `id` field follows the pattern: `{record}_{sample}_{lead}`

| Component | Description |
|-----------|-------------|
| `record` | The ECG record number (matches test set) |
| `sample` | The sample index within the time series |
| `lead` | The ECG lead name (I, II, III, aVR, aVL, aVF, V1-V6) |

#### Value Field
- **Type:** Float
- **Unit:** mV (millivolts) - typical ECG amplitude range
- **Precision:** Sufficient decimal places for SNR calculation

### 12-Lead ECG Reference

| Lead | Description | Typical Location |
|------|-------------|------------------|
| I | Lateral | Top row, column 1 |
| II | Inferior | Top row, column 2 |
| III | Inferior | Top row, column 3 |
| aVR | Augmented | Top row, column 4 |
| aVL | Lateral | Middle row, column 1 |
| aVF | Inferior | Middle row, column 2 |
| V1 | Septal | Middle row, column 3 |
| V2 | Septal | Middle row, column 4 |
| V3 | Anterior | Bottom row, column 1 |
| V4 | Anterior | Bottom row, column 2 |
| V5 | Lateral | Bottom row, column 3 |
| V6 | Lateral | Bottom row, column 4 |
| Rhythm | Usually Lead II | Full-width strip at bottom |

---

## 3. Evaluation Metric

### Modified Signal-to-Noise Ratio (SNR)

The metric measures reconstruction quality by comparing predicted signals to ground truth.

#### Alignment Corrections (Applied Before Scoring)

| Correction | Description | Limit |
|------------|-------------|-------|
| **Time Shift** | Horizontal alignment via cross-correlation | ±0.2 seconds maximum |
| **Vertical Shift** | DC offset removal | Unlimited (constant offset) |

#### SNR Calculation

```
SNR = 10 * log10(signal_power / noise_power)
```

Where:
- **Signal Power** = Sum of squared ground truth values (across all 12 leads)
- **Noise Power** = Sum of squared reconstruction errors (across all 12 leads)
- **Final Score** = Average SNR across all test ECGs (in dB)

#### Interpretation
| SNR (dB) | Quality |
|----------|---------|
| < 0 | Very poor - more noise than signal |
| 0-10 | Poor |
| 10-20 | Moderate |
| 20-30 | Good |
| > 30 | Excellent |

**Higher SNR = Better reconstruction = Higher leaderboard position**

---

## 4. Technical Constraints

### Notebook Requirements

| Constraint | Limit |
|------------|-------|
| **CPU Runtime** | ≤ 9 hours |
| **GPU Runtime** | ≤ 9 hours |
| **Internet Access** | DISABLED during submission |
| **External Data** | Allowed if freely & publicly available |
| **Pre-trained Models** | Allowed if publicly available |

### Key Implications

1. **Offline Inference:** Model and all dependencies must be self-contained
2. **Time Management:** Pipeline must process entire test set within 9 hours
3. **Memory Efficiency:** Must handle large batches without OOM errors
4. **Determinism:** Reproducible results across runs

---

## 5. Pipeline Architecture

### Required Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KAGGLE SUBMISSION NOTEBOOK                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │   INPUT      │    │  PROCESSING  │    │   OUTPUT     │           │
│  │              │    │              │    │              │           │
│  │  ECG Images  │───▶│  Digitize    │───▶│ submission   │           │
│  │  (test set)  │    │  Pipeline    │    │ .csv/.parquet│           │
│  │              │    │              │    │              │           │
│  └──────────────┘    └──────────────┘    └──────────────┘           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Processing Pipeline Stages

```
1. IMAGE LOADING
   └── Load ECG image from test set
   
2. PREPROCESSING
   ├── Color space conversion (BGR→Grayscale/HSV)
   ├── Noise reduction (Gaussian blur, bilateral filter)
   ├── Contrast enhancement (CLAHE, histogram equalization)
   └── Grid detection and removal

3. GEOMETRIC CORRECTION
   ├── Rotation correction (deskewing)
   ├── Perspective correction
   ├── Barrel/pincushion distortion correction
   └── Scale normalization

4. LEAD SEGMENTATION
   ├── Detect lead boundaries
   ├── Identify lead labels
   ├── Extract individual lead regions
   └── Map to standard 12-lead layout

5. SIGNAL EXTRACTION
   ├── Trace detection (edge detection, contour finding)
   ├── Sub-pixel interpolation
   ├── Signal continuity enforcement
   └── Multi-trace disambiguation

6. CALIBRATION
   ├── Detect calibration pulse (1mV reference)
   ├── Measure grid spacing (25mm/s, 10mm/mV typical)
   ├── Scale amplitude to mV
   └── Convert x-axis to samples at target frequency

7. POST-PROCESSING
   ├── Baseline wander removal
   ├── Resampling to standard frequency (500Hz typical)
   ├── Interpolation for missing samples
   └── Quality checks

8. OUTPUT GENERATION
   └── Format as submission CSV/Parquet
```

---

## 6. Current Implementation Status

### Infrastructure (from our Firebase/Cloud project)

| Component | Status | Notes |
|-----------|--------|-------|
| Image Upload | ✅ Complete | Firebase Storage |
| Gallery UI | ✅ Complete | View/manage images |
| Grid Detection | ✅ 80% | Color-based, needs refinement |
| Barrel Correction | ✅ Complete | Polynomial distortion fix |
| Multi-method Transform | ✅ Complete | Cloud Run service |
| Polynomial Fitting | ✅ 90% | Analysis ready, needs warp impl |

### Color Isolation Pipeline (ecg_color_processor.py)

| Component | Status | Notes |
|-----------|--------|-------|
| Multi-mode Script | ✅ Complete | KAGGLE / CLOUD / GROUP modes |
| OpenCV Method | ✅ Complete | HSV-based color isolation |
| Pillow Method | ✅ Complete | Channel splitting approach |
| Scikit-image Method | ✅ Complete | LAB color space |
| Text Detection/Removal | ✅ Complete | Morphological + connected components |
| Quality Scoring | ✅ Complete | Black: pixel count, Red: contamination |
| Keeper Selection | ✅ Complete | Auto-selects best method per image |
| GCS Integration | ✅ Complete | Upload/download/delete |
| Group Processing | ✅ Complete | Process by image prefix groups |

### Kaggle Pipeline (to be built)

| Component | Status | Priority |
|-----------|--------|----------|
| Offline Notebook | ⏳ Not Started | HIGH |
| Lead Segmentation | ⏳ Not Started | HIGH |
| Signal Extraction | ⏳ Not Started | HIGH |
| Calibration | ⏳ Not Started | HIGH |
| Submission Generator | ⏳ Not Started | HIGH |
| Pre-trained Model | ⏳ Not Started | MEDIUM |

---

## 6.1 Color Isolation Script (ecg_color_processor.py)

### Three Operating Modes

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ecg_color_processor.py                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  MODE = "KAGGLE"    │  MODE = "CLOUD"      │  MODE = "GROUP"        │
│  ─────────────────  │  ──────────────────  │  ────────────────────  │
│  • No modifications │  • Full dataset      │  • Prefix-based        │
│  • Uses Kaggle      │  • GCS integration   │  • Random/Range/List   │
│    input paths      │  • Upload results    │  • Test specific sets  │
│  • Offline ready    │  • Track all files   │  • Quick iteration     │
│                     │  • Delete options    │                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Configuration Reference

```python
# ========== MODE SELECTION ==========
MODE = "GROUP"  # Options: "KAGGLE", "CLOUD", "GROUP"

# ========== GROUP MODE OPTIONS ==========
IMAGE_GROUP_PREFIXES = [
    "1006427285",  # Each prefix groups related images
    "1006634048",  # e.g., 1006427285-0001.png, 1006427285-0002.png
    ...
]

GROUP_SELECTION_MODE = "RANGE"  # "RANGE", "RANDOM", or "LIST"
GROUP_RANGE_START = 0           # Process groups 0-4 (first 5)
GROUP_RANGE_END = 5
GROUP_RANDOM_COUNT = 3          # Or pick 3 random groups
GROUP_LIST = [0, 2, 4]          # Or specific indices

# ========== PROCESSING OPTIONS ==========
VERSION = "v6"
METHODS = ['opencv', 'pillow']  # Add 'skimage' if needed
TEST_LIMIT = 10                 # Limit images per run (None = all)
```

### Output Naming Convention

```
{original_name}--{prefix}-{version}-{method}-{color}-{score}.png

Prefixes:
  --s-   = Regular processed file (all methods saved)
  --sk-  = Keeper (best quality selected)

Examples:
  1006427285-0001--original.png           # Original for comparison
  1006427285-0001--s-v6-opencv-black-45231.png   # Regular
  1006427285-0001--s-v6-pillow-red-892.png       # Regular
  1006427285-0001--sk-v6-opencv-black-45231.png  # KEEPER (best black)
  1006427285-0001--sk-v6-pillow-red-892.png      # KEEPER (best red)
```

### Quality Scoring

| Output Type | Score Calculation | Better = |
|-------------|-------------------|----------|
| BLACK (ECG) | Total black pixel count | HIGHER (more ECG data) |
| RED (Grid) | % black pixels × 1000 | LOWER (less contamination) |

### Usage

**Local Testing (GROUP mode):**
```powershell
cd "c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"
python ecg_color_processor.py
# Interactive menu appears - select options
```

**Cloud Processing:**
```python
MODE = "CLOUD"
TEST_LIMIT = None  # Process all
# Run script
```

**Kaggle Submission:**
```python
MODE = "KAGGLE"
# Copy to Kaggle notebook and run
```

### Post-Processing Options

After processing, the script offers:
- `k` = Keep all created files
- `d` = Delete all created files (rollback)
- `r` = Delete regular files, keep only keepers and originals

---

## 7. Action Items / Milestones

### Phase 1: Baseline Submission
- [ ] Set up Kaggle notebook environment
- [ ] Download and explore training data
- [ ] Implement basic signal extraction (single lead)
- [ ] Generate first submission
- [ ] Establish baseline SNR score

### Phase 2: Full Pipeline
- [ ] Implement 12-lead segmentation
- [ ] Add geometric correction (rotation, perspective)
- [ ] Implement calibration detection
- [ ] Handle all test images
- [ ] Optimize for 9-hour runtime

### Phase 3: Model Enhancement
- [ ] Train/fine-tune deep learning model
- [ ] Implement ensemble methods
- [ ] Add confidence-based post-processing
- [ ] Cross-validate on training data
- [ ] Submit improved version

### Phase 4: Optimization
- [ ] Profile and optimize bottlenecks
- [ ] Handle edge cases
- [ ] Implement fallback strategies
- [ ] Final submission

---

## 8. Data Specifications

### Expected ECG Image Characteristics

| Property | Typical Values |
|----------|----------------|
| **Resolution** | 300-600 DPI scans, variable for photos |
| **Paper Speed** | 25 mm/s (standard), some 50 mm/s |
| **Amplitude Scale** | 10 mm/mV (standard), some 5 or 20 mm/mV |
| **Grid Color** | Red/pink (most common), brown, blue |
| **Trace Color** | Black, blue |
| **Calibration Pulse** | 1 mV, 200 ms (rectangular pulse) |

### Output Sampling Requirements

| Property | Value |
|----------|-------|
| **Target Frequency** | Match ground truth (likely 500 Hz) |
| **Signal Duration** | Match ground truth samples |
| **Amplitude Unit** | millivolts (mV) |

---

## 9. Testing Strategy

### Local Validation
1. Split training data into train/validation sets
2. Compute SNR on validation set locally
3. Compare with leaderboard score

### Sanity Checks
- [ ] All 12 leads present for each record
- [ ] No NaN or infinite values
- [ ] Sample counts match expected
- [ ] Amplitude range reasonable (typically ±5 mV)
- [ ] Submission file format valid

### Edge Case Testing
- [ ] Rotated images
- [ ] Low resolution images
- [ ] Noisy/artifacts
- [ ] Non-standard layouts
- [ ] Missing leads

---

## 10. Resources

### Competition Links
- [Competition Page](https://kaggle.com/competitions/physionet-ecg-image-digitization)
- [Data Download](https://kaggle.com/competitions/physionet-ecg-image-digitization/data)
- [Discussion Forum](https://kaggle.com/competitions/physionet-ecg-image-digitization/discussion)
- [Code Examples](https://kaggle.com/competitions/physionet-ecg-image-digitization/code)

### Reference Materials
- PhysioNet Challenge documentation
- ECG image digitization literature
- OpenCV documentation
- NeuroKit2 documentation

### Our Project Files
- `ecg_color_processor.py` - **Unified color isolation script (3 modes: KAGGLE/CLOUD/GROUP)**
- `gcs_color_isolation.py` - GCS-only color isolation (simpler)
- `kaggle_color_isolation.py` - Original Kaggle-only version
- `functions_python/transformers/` - Image transformation modules
- `public/gallery.html` - Visualization UI
- `scripts/` - Utility scripts

---

## 11. Submission Checklist

Before each submission:

- [ ] Notebook runs completely without errors
- [ ] Runtime under 9 hours
- [ ] Internet access not required
- [ ] Output file named correctly (`submission.csv` or `submission.parquet`)
- [ ] All required IDs present in submission
- [ ] No missing values
- [ ] File format valid (header row present)
- [ ] Commit and submit via Kaggle UI

---

## 12. Citation

```
Matthew A. Reyna, Deepanshi, James Weigle, Zuzana Koscova, Kiersten Campbell, 
Salman Seyedi, Andoni Elola, Ali Bahrami Rad, Amit J Shah, Neal K. Bhatia, 
Yao Yan, Sohier Dane, Addison Howard, Gari D. Clifford, and Reza Sameni. 
PhysioNet - Digitization of ECG Images. 
https://kaggle.com/competitions/physionet-ecg-image-digitization, 2025. Kaggle.
```

---

*Last Updated: January 21, 2026*
