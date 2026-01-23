# How to Test Expected Score for Your Project

## Overview

The competition uses **Signal-to-Noise Ratio (SNR)** as the evaluation metric. To test your expected score, you need to:

1. **Process train images** (they have ground truth)
2. **Calculate SNR** using the competition's method
3. **Compare** your results to ground truth

## Quick Answer

**To test expected score:**

```python
# In Kaggle notebook or locally
!python test_kaggle_with_snr.py --limit 10
```

This will:
- Process 10 train images
- Calculate actual SNR vs ground truth
- Show mean/min/max SNR (your expected score range)

## Method 1: Using Test Script (Recommended)

### Step 1: Run Test Script

```bash
# Test on 10 train images
python test_kaggle_with_snr.py --limit 10

# Test on specific record
python test_kaggle_with_snr.py --record-id 62

# Test on all train images (takes longer)
python test_kaggle_with_snr.py
```

### Step 2: Review Results

The script outputs:
```
SNR calculated for: 10 images
Mean SNR: 14.56 dB    ← This is your expected score
Min SNR: 12.34 dB
Max SNR: 16.78 dB
```

**Interpretation:**
- **Mean SNR** = Your expected competition score
- **Min SNR** = Worst case scenario
- **Max SNR** = Best case scenario

### Step 3: Check CSV Output

Results are saved to `test_results.csv`:
```csv
record_id,image_path,snr_db,leads_extracted
62,/path/to/62.jpg,15.23,12
63,/path/to/63.jpg,14.45,12
...
```

## Method 2: Manual Calculation in Notebook

### Step 1: Process Train Image

```python
# In your Kaggle notebook
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.signal import correlate

# Process a train image
image_path = '/kaggle/input/physionet-ecg-image-digitization/train/62.jpg'
digitizer = ECGDigitizer()
result = digitizer.process_image(image_path)

# Extract signals
predicted_signals = {}
for lead_data in result['leads']:
    lead_name = lead_data['name']
    predicted_signals[lead_name] = np.array(lead_data['values'])[:5000]  # Ensure 5000 samples
```

### Step 2: Load Ground Truth

```python
# Load ground truth
gt_path = '/kaggle/input/physionet-ecg-image-digitization/train.parquet'
df = pd.read_parquet(gt_path)

# Extract ground truth for record 62
record_id = '62'
record_df = df[df['id'].str.contains(f"'{record_id}_")]

# Organize by lead
ground_truth_signals = {}
for lead_name in ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']:
    lead_data = record_df[record_df['id'].str.contains(f"_{lead_name}'")].sort_values('id')
    if not lead_data.empty:
        ground_truth_signals[lead_name] = lead_data['value'].values[:5000]
    else:
        ground_truth_signals[lead_name] = np.zeros(5000)
```

### Step 3: Calculate SNR (Competition Method)

```python
def align_and_calculate_snr(pred, gt, sampling_rate=500, max_shift_sec=0.2):
    """Align signals and calculate SNR using competition method"""
    # Time alignment (cross-correlation)
    max_shift_samples = int(max_shift_sec * sampling_rate)
    correlation = correlate(gt, pred, mode='full')
    mid = len(correlation) // 2
    search_range = correlation[mid - max_shift_samples:mid + max_shift_samples + 1]
    best_shift = np.argmax(search_range) - max_shift_samples
    
    # Apply shift
    if best_shift > 0:
        aligned_pred = np.concatenate([np.zeros(best_shift), pred[:-best_shift]])
    elif best_shift < 0:
        aligned_pred = np.concatenate([pred[-best_shift:], np.zeros(-best_shift)])
    else:
        aligned_pred = pred.copy()
    
    # Vertical alignment (remove DC offset)
    min_len = min(len(aligned_pred), len(gt))
    aligned_pred = aligned_pred[:min_len]
    gt_aligned = gt[:min_len]
    vertical_offset = np.mean(aligned_pred - gt_aligned)
    aligned_pred = aligned_pred - vertical_offset
    
    # Calculate powers
    signal_power = np.sum(gt_aligned ** 2)
    noise = aligned_pred - gt_aligned
    noise_power = np.sum(noise ** 2)
    
    if noise_power > 0:
        snr_db = 10 * np.log10(signal_power / noise_power)
    else:
        snr_db = 60.0
    
    return snr_db, signal_power, noise_power

# Calculate SNR for all leads
total_signal_power = 0.0
total_noise_power = 0.0

for lead_name in ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']:
    if lead_name in predicted_signals and lead_name in ground_truth_signals:
        pred = predicted_signals[lead_name]
        gt = ground_truth_signals[lead_name]
        
        # Ensure same length
        min_len = min(len(pred), len(gt))
        pred = pred[:min_len]
        gt = gt[:min_len]
        
        snr, sig_power, noise_power = align_and_calculate_snr(pred, gt)
        total_signal_power += sig_power
        total_noise_power += noise_power

# Final SNR (competition method)
if total_noise_power > 0:
    final_snr = 10 * np.log10(total_signal_power / total_noise_power)
else:
    final_snr = 60.0

print(f"Expected Score (SNR): {final_snr:.2f} dB")
```

## Method 3: Batch Testing Multiple Images

```python
# Test multiple images and get average score
import glob

train_images = glob.glob('/kaggle/input/physionet-ecg-image-digitization/train/*.jpg')[:20]  # Test 20 images

snr_values = []
for img_path in train_images:
    # Process image
    result = digitizer.process_image(img_path)
    
    # Extract record ID
    record_id = Path(img_path).stem
    
    # Load ground truth and calculate SNR (use method from above)
    # ... (code from Method 2)
    
    snr_values.append(final_snr)
    print(f"{record_id}: {final_snr:.2f} dB")

print(f"\nExpected Competition Score: {np.mean(snr_values):.2f} dB")
print(f"Score Range: {np.min(snr_values):.2f} - {np.max(snr_values):.2f} dB")
```

## Understanding Your Score

### Score Interpretation

| SNR (dB) | Ranking | Meaning |
|----------|---------|---------|
| < 10 | Bottom 50% | Basic extraction, needs improvement |
| 10-15 | Middle 50% | Good digitization, competitive |
| 15-20 | Top 25% | High quality, strong submission |
| 20-25 | Top 10% | Excellent, near-perfect |
| > 25 | Top 5% | Outstanding, likely leaderboard |

### Target Scores

- **Minimum acceptable:** SNR > 10 dB
- **Competitive:** SNR > 15 dB
- **Top tier:** SNR > 20 dB

## What Affects Your Score

1. **Signal Extraction Quality**
   - Accurate lead detection
   - Proper calibration
   - Clean signal extraction

2. **Alignment**
   - Time shift correction (competition handles this)
   - Vertical offset correction (competition handles this)

3. **Noise Reduction**
   - Filtering artifacts
   - Grid line removal
   - Image preprocessing quality

## Testing Checklist

Before submission, test:

- [ ] **Process 10+ train images** and calculate SNR
- [ ] **Verify mean SNR > 10 dB** (minimum acceptable)
- [ ] **Check consistency** (min/max SNR not too far apart)
- [ ] **Test on different image types** (various qualities)
- [ ] **Verify submission.csv format** matches competition
- [ ] **Check runtime** < 9 hours on full test set

## Expected Score Calculation

The competition calculates score as:

```
Score = Average of all individual ECG SNRs (in dB)
```

Where each ECG SNR is:
```
SNR = 10 × log₁₀(total_signal_power / total_noise_power)
```

- Signal power = sum of squared ground truth values (all 12 leads)
- Noise power = sum of squared errors (all 12 leads)
- Powers are summed across all leads before calculating SNR

## Quick Test Command

```bash
# Fast test (5 images)
python test_kaggle_with_snr.py --limit 5

# Full test (all train images - takes longer)
python test_kaggle_with_snr.py
```

## Files for Testing

1. **`test_kaggle_with_snr.py`** - Automated testing script
2. **`SIMPLE_TEST.py`** - Quick single image test
3. **`TEST_KAGGLE_IMAGES_GUIDE.md`** - Detailed guide

## Next Steps

1. **Run test script** on train images
2. **Review SNR values** - aim for > 15 dB
3. **Optimize if needed** - adjust parameters based on results
4. **Generate submission** once score is acceptable
5. **Submit to Kaggle** and compare with leaderboard

---

**Remember:** Test images have NO ground truth, so you can only test on train images. Your actual competition score will be calculated on test images by Kaggle.
