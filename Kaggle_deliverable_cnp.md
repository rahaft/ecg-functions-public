# Kaggle Deliverable Requirements - ECG Image Digitization

**Competition:** PhysioNet - Digitization of ECG Images  
**URL:** https://kaggle.com/competitions/physionet-ecg-image-digitization  
**Type:** Code Competition (Notebook submission)




<!--We want to create a document to track what the deliverable to Kaggle is. 

Make a new document with al of the requirements and call it Kaggle_deliverable_cnp.md 

At the bottom make an outline of the summary outline and checklist of what should be there. 

Overview
You will build models to extract time series data from Electrocardiogram (ECG) images. ECGs are used to diagnose and guide treatment for heart disease. They exist as physical printouts, scanned images, photographs, or time series. Medical-grade ECG software currently works best on time series. Tools for extracting time series from ECG images can help convert billions of ECG images collected globally over decades into data for training better diagnostic models to improve clinical outcomes.

Description
ECGs have been used for decades to diagnose and guide treatment for heart diseases. While modern machines store ECGs as time-series data, hard copy printouts, scans, and photos remain very common in clinical use. ECG images, even in electronic format, are not compatible or suitable for machine learning and the current medical-grade software, which only operate on time series.

Billions of hard copies, image-only electronic copies, scanned images, or photographs are estimated to exist globally. Clinical ECGs have specific subtleties that make their interpretation difficult for generic computer vision tools. Hence, electronic images are not enough. Having tools to digitize these ECG images into time series can help convert decades of data collected globally to train better models and improve cardiovascular diagnosis and treatment.

This is not a trivial task, however. Physical printouts, scanning, and photography introduce imaging artifacts (misalignments, rotations, reflections, aspect ratio issues, blurring, scanning resolution, etc.). ECG specifications such as multi-lead interrelationships corresponding to the physical placement of electrodes on the body, variability in ECG data collection methods, varied sampling frequencies, signal lengths, locations of leads on ECG images from different vendors, and noisiness of the original time-series data add to the challenges of the problem.

This competition is a rerun of the 2024 PhysioNet Competition on ECG digitization with fresh data. In this competition, you will build a model that extracts the original ECG time-series data from images of paper ECGs. The idea is to bring older or image-only ECGs into the AI age, allowing today's tools to utilize them effectively.

Your work could help unlock billions of historical ECG images, support improved cardiovascular care, and expand access to critical health insights, particularly in areas where digital records are limited.

Evaluation
The evaluation metric for this competition is a modified signal-to-noise ratio (SNR), designed to assess the quality of time series ECG reconstructed from ECG images against the ground-truth ECG time series.

To ensure that submissions are not unfairly penalized for minor alignment issues that are irrelevant for ECG interpretation, the metric first aligns the predicted signal with the ground-truth signal. This alignment procedure corrects for two types of discrepancies:

Time Shifts: It finds the optimal horizontal shift (up to a maximum of 0.2 seconds) that maximizes the cross-correlation between your prediction and the ground truth.

Vertical Shifts: It calculates and removes any constant vertical (amplitude) offset between the two signals after they are time-aligned.

The final score is calculated by comparing the power of the true signal to the power of the reconstruction error (noise). The signal powers and noise powers are first summed across all 12 leads before a single SNR is computed for that entire ECG record. The competition score is the average of these individual ECG SNRs, converted to decibel scale. A higher SNR value indicates a more accurate reconstruction with less noise.

Submission File
For each ID in the test set, you must predict a value for the value variable. The file should contain a header and have the following format:

id,value
'62_0_I',0.0
'62_1_II',0.3
'62_2_I',0.4
etc.

Code Requirements


Submissions to this competition must be made through Notebooks. In order for the "Submit" button to be active after a commit, the following conditions must be met:

CPU Notebook <= 9 hours run-time
GPU Notebook <= 9 hours run-time
Internet access disabled
Freely & publicly available external data is allowed, including pre-trained models
Submission file must be named submission.parquet or submission.csv
Please see the Code Competition FAQ for more information on how to submit. And review the code debugging doc if you are encountering submission errors.

Citation
Matthew A. Reyna, Deepanshi, James Weigle, Zuzana Koscova, Kiersten Campbell, Salman Seyedi, Andoni Elola, Ali Bahrami Rad, Amit J Shah, Neal K. Bhatia, Yao Yan, Sohier Dane, Addison Howard, Gari D. Clifford, and Reza Sameni. PhysioNet - Digitization of ECG Images. https://kaggle.com/competitions/physionet-ecg-image-digitization, 2025. Kaggle. We want to create a document to track what the deliverable to Kaggle is. 

Make a new document with al of the requirements and call it Kaggle_deliverable_cnp.md 

At the bottom make an outline of the summary outline and checklist of what should be there. 

Overview
You will build models to extract time series data from Electrocardiogram (ECG) images. ECGs are used to diagnose and guide treatment for heart disease. They exist as physical printouts, scanned images, photographs, or time series. Medical-grade ECG software currently works best on time series. Tools for extracting time series from ECG images can help convert billions of ECG images collected globally over decades into data for training better diagnostic models to improve clinical outcomes.

Description
ECGs have been used for decades to diagnose and guide treatment for heart diseases. While modern machines store ECGs as time-series data, hard copy printouts, scans, and photos remain very common in clinical use. ECG images, even in electronic format, are not compatible or suitable for machine learning and the current medical-grade software, which only operate on time series.

Billions of hard copies, image-only electronic copies, scanned images, or photographs are estimated to exist globally. Clinical ECGs have specific subtleties that make their interpretation difficult for generic computer vision tools. Hence, electronic images are not enough. Having tools to digitize these ECG images into time series can help convert decades of data collected globally to train better models and improve cardiovascular diagnosis and treatment.

This is not a trivial task, however. Physical printouts, scanning, and photography introduce imaging artifacts (misalignments, rotations, reflections, aspect ratio issues, blurring, scanning resolution, etc.). ECG specifications such as multi-lead interrelationships corresponding to the physical placement of electrodes on the body, variability in ECG data collection methods, varied sampling frequencies, signal lengths, locations of leads on ECG images from different vendors, and noisiness of the original time-series data add to the challenges of the problem.

This competition is a rerun of the 2024 PhysioNet Competition on ECG digitization with fresh data. In this competition, you will build a model that extracts the original ECG time-series data from images of paper ECGs. The idea is to bring older or image-only ECGs into the AI age, allowing today's tools to utilize them effectively.

Your work could help unlock billions of historical ECG images, support improved cardiovascular care, and expand access to critical health insights, particularly in areas where digital records are limited.

Evaluation
The evaluation metric for this competition is a modified signal-to-noise ratio (SNR), designed to assess the quality of time series ECG reconstructed from ECG images against the ground-truth ECG time series.

To ensure that submissions are not unfairly penalized for minor alignment issues that are irrelevant for ECG interpretation, the metric first aligns the predicted signal with the ground-truth signal. This alignment procedure corrects for two types of discrepancies:

Time Shifts: It finds the optimal horizontal shift (up to a maximum of 0.2 seconds) that maximizes the cross-correlation between your prediction and the ground truth.

Vertical Shifts: It calculates and removes any constant vertical (amplitude) offset between the two signals after they are time-aligned.

The final score is calculated by comparing the power of the true signal to the power of the reconstruction error (noise). The signal powers and noise powers are first summed across all 12 leads before a single SNR is computed for that entire ECG record. The competition score is the average of these individual ECG SNRs, converted to decibel scale. A higher SNR value indicates a more accurate reconstruction with less noise.

Submission File
For each ID in the test set, you must predict a value for the value variable. The file should contain a header and have the following format:

id,value
'62_0_I',0.0
'62_1_II',0.3
'62_2_I',0.4
etc.

Code Requirements


Submissions to this competition must be made through Notebooks. In order for the "Submit" button to be active after a commit, the following conditions must be met:

CPU Notebook <= 9 hours run-time
GPU Notebook <= 9 hours run-time
Internet access disabled
Freely & publicly available external data is allowed, including pre-trained models
Submission file must be named submission.parquet or submission.csv
Please see the Code Competition FAQ for more information on how to submit. And review the code debugging doc if you are encountering submission errors.

Citation
Matthew A. Reyna, Deepanshi, James Weigle, Zuzana Koscova, Kiersten Campbell, Salman Seyedi, Andoni Elola, Ali Bahrami Rad, Amit J Shah, Neal K. Bhatia, Yao Yan, Sohier Dane, Addison Howard, Gari D. Clifford, and Reza Sameni. PhysioNet - Digitization of ECG Images. https://kaggle.com/competitions/physionet-ecg-image-digitization, 2025. Kaggle. -->

## Competition Goal

**Build a model that extracts ECG time-series data from ECG images.**

Input: ECG images (scans, photos, printouts)  
Output: Time-series signal values for all 12 leads

---

## 1. Submission File Requirements

### File Format
| Requirement | Specification |
|-------------|---------------|
| **Filename** | `submission.parquet` OR `submission.csv` |
| **Columns** | `id`, `value` |
| **Header** | Required |

### File Structure
```csv
id,value
'62_0_I',0.0
'62_1_II',0.3
'62_2_I',0.4
...
```

### ID Field Format
Pattern: `{record}_{sample}_{lead}`

| Component | Description | Example |
|-----------|-------------|---------|
| `record` | ECG record number | `62` |
| `sample` | Sample index (time point) | `0`, `1`, `2`, ... |
| `lead` | Lead identifier | `I`, `II`, `III`, `aVR`, `aVL`, `aVF`, `V1`-`V6` |

### Value Field
| Property | Requirement |
|----------|-------------|
| Type | Float |
| Unit | millivolts (mV) |
| Range | Typically ±5 mV for ECG signals |

### 12 Standard ECG Leads
```
Limb Leads:     I, II, III
Augmented:      aVR, aVL, aVF
Precordial:     V1, V2, V3, V4, V5, V6
```

---

## 2. Notebook Requirements

### Runtime Limits
| Environment | Maximum Runtime |
|-------------|-----------------|
| CPU Notebook | ≤ 9 hours |
| GPU Notebook | ≤ 9 hours |

### Access Restrictions
| Resource | Allowed? |
|----------|----------|
| Internet | **NO** - Disabled during submission |
| External Data | YES - If freely & publicly available |
| Pre-trained Models | YES - If publicly available |

### Submission Activation
The "Submit" button is only active when:
1. Notebook commits successfully
2. Runtime ≤ 9 hours
3. Output file named `submission.parquet` or `submission.csv`
4. No internet calls during execution

---

## 3. Evaluation Metric

### Modified Signal-to-Noise Ratio (SNR)

**Formula:**
```
SNR (dB) = 10 × log₁₀(signal_power / noise_power)
```

### Pre-Scoring Alignment

Before calculating SNR, the metric aligns predicted and ground-truth signals:

| Alignment | Description | Limit |
|-----------|-------------|-------|
| **Time Shift** | Horizontal alignment via cross-correlation | ±0.2 seconds max |
| **Vertical Shift** | DC offset removal | No limit |

### Scoring Process
1. Align prediction to ground truth (time + vertical)
2. Calculate signal power (sum of squared ground truth)
3. Calculate noise power (sum of squared errors)
4. Sum powers across all 12 leads per record
5. Compute SNR for each ECG record
6. Average SNR across all test records (in dB)

### Score Interpretation
| SNR (dB) | Quality |
|----------|---------|
| < 0 | Very poor |
| 0-10 | Poor |
| 10-20 | Moderate |
| 20-30 | Good |
| > 30 | Excellent |

**Higher SNR = Better = Higher leaderboard rank**

---

## 4. Technical Challenges

### Image Artifacts
- Misalignments and rotations
- Reflections and aspect ratio issues
- Blurring and varied scanning resolutions
- Paper creases and fold marks

### ECG-Specific Challenges
- Multi-lead interrelationships (12-lead layout)
- Different ECG machine vendors = different formats
- Varied sampling frequencies
- Different paper speeds (25mm/s, 50mm/s)
- Different amplitude scales (5, 10, 20 mm/mV)
- Grid line interference
- Overlapping traces

### Data Variability
- Physical printouts vs. scans vs. photos
- Color variations (grid: red/pink/brown/blue)
- Trace colors (black/blue)
- Text and annotations on images

---

## 5. Required Pipeline Components

### Input Processing
- [ ] Load ECG images from test set
- [ ] Handle various image formats

### Image Preprocessing
- [ ] Color space conversion
- [ ] Noise reduction
- [ ] Contrast enhancement
- [ ] Grid detection/removal

### Geometric Correction
- [ ] Rotation/deskew correction
- [ ] Perspective correction
- [ ] Scale normalization

### Lead Extraction
- [ ] Detect lead boundaries
- [ ] Identify lead labels
- [ ] Segment individual leads
- [ ] Map to standard 12-lead layout

### Signal Digitization
- [ ] Trace detection
- [ ] Sub-pixel interpolation
- [ ] Handle multi-trace disambiguation

### Calibration
- [ ] Detect calibration pulse (1mV reference)
- [ ] Measure grid spacing
- [ ] Convert pixels to mV (amplitude)
- [ ] Convert pixels to time/samples

### Output Generation
- [ ] Resample to required frequency
- [ ] Format as submission file
- [ ] Validate output format

---

## 6. Offline Requirements

Since internet is disabled during submission:

### Must Be Self-Contained
- [ ] All model weights included in notebook/dataset
- [ ] All dependencies installed offline
- [ ] No API calls to external services
- [ ] No downloading during execution

### Pre-loaded Resources
- [ ] Pre-trained models (if used)
- [ ] Lookup tables (if needed)
- [ ] Configuration files

---

## 7. Citation

```
Matthew A. Reyna, Deepanshi, James Weigle, Zuzana Koscova, Kiersten Campbell, 
Salman Seyedi, Andoni Elola, Ali Bahrami Rad, Amit J Shah, Neal K. Bhatia, 
Yao Yan, Sohier Dane, Addison Howard, Gari D. Clifford, and Reza Sameni. 
PhysioNet - Digitization of ECG Images. 
https://kaggle.com/competitions/physionet-ecg-image-digitization, 2025. Kaggle.
```

---

---

# SUMMARY OUTLINE & CHECKLIST

## What Must Be Delivered

```
┌────────────────────────────────────────────────────────────────┐
│                    KAGGLE SUBMISSION                            │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   NOTEBOOK (.ipynb)                                            │
│   ├── Runs in ≤ 9 hours (CPU or GPU)                          │
│   ├── No internet access required                              │
│   ├── All dependencies self-contained                          │
│   └── Produces valid output file                               │
│                                                                 │
│   OUTPUT FILE                                                   │
│   ├── Named: submission.csv OR submission.parquet              │
│   ├── Columns: id, value                                       │
│   ├── All test IDs included                                    │
│   └── Values in millivolts (float)                             │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Pre-Submission Checklist

### File Requirements
- [ ] Output file exists
- [ ] Named `submission.csv` or `submission.parquet`
- [ ] Has header row
- [ ] Contains columns: `id`, `value`
- [ ] All test record IDs present
- [ ] All 12 leads per record included
- [ ] All sample indices included
- [ ] No missing/NaN values

### Notebook Requirements
- [ ] Runs without errors
- [ ] Total runtime ≤ 9 hours
- [ ] No internet calls
- [ ] No missing dependencies
- [ ] Deterministic/reproducible

### Data Quality
- [ ] Values are floats
- [ ] Amplitudes in reasonable range (±5 mV typical)
- [ ] ID format correct: `{record}_{sample}_{lead}`
- [ ] Lead names match expected: I, II, III, aVR, aVL, aVF, V1-V6

### Before Submit
- [ ] Commit notebook successfully
- [ ] Verify "Submit" button is active
- [ ] Review commit output for errors

---

## Quick Reference Card

| Item | Requirement |
|------|-------------|
| **Filename** | `submission.csv` or `submission.parquet` |
| **Columns** | `id`, `value` |
| **ID Format** | `{record}_{sample}_{lead}` |
| **Value Unit** | millivolts (mV) |
| **Leads** | I, II, III, aVR, aVL, aVF, V1-V6 |
| **Runtime** | ≤ 9 hours |
| **Internet** | Disabled |
| **Metric** | SNR (dB) - higher is better |
| **Alignment** | ±0.2s time, any vertical offset |

---

## Output File Example

```csv
id,value
'62_0_I',0.0
'62_1_I',0.02
'62_2_I',0.05
'62_0_II',0.1
'62_1_II',0.15
'62_2_II',0.18
'62_0_III',0.08
...
'62_0_V6',0.12
'62_1_V6',0.14
...
```

---

*Document Version: 1.0*  
*Last Updated: January 21, 2026*
