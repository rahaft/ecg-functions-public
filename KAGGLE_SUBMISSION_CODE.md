# Kaggle Submission Code - Complete Guide

## ⚠️ Important: Test vs Train Images

**Test images** (in `/kaggle/input/.../test/`):
- ❌ **NO ground truth available** - Cannot calculate SNR
- ✅ Use these for **final submission** to Kaggle
- These are the images you need to process for the competition

**Train images** (in `/kaggle/input/.../train/`):
- ✅ **Have ground truth** - Can calculate SNR for validation
- ✅ Use these to **test and improve** your pipeline
- ❌ Not used for final submission

## Your Kaggle Submission Code

The complete submission code is in **`kaggle_submission_notebook.py`**

### Quick Start - Copy This Into Your Kaggle Notebook:

```python
# ============================================
# KAGGLE SUBMISSION NOTEBOOK
# ============================================

import os
import sys
import csv
import numpy as np
from pathlib import Path

# Add your pipeline to path
sys.path.insert(0, '/kaggle/working')

# Import your digitization pipeline
from digitization_pipeline import ECGDigitizer

# Configuration
COMPETITION_NAME = "physionet-ecg-image-digitization"
INPUT_DIR = Path('/kaggle/input') / COMPETITION_NAME
TEST_DIR = INPUT_DIR / 'test'
OUTPUT_DIR = Path('/kaggle/working')

LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SAMPLES_PER_LEAD = 5000

# Find test images
print("Finding test images...")
test_images = sorted(TEST_DIR.glob('*.jpg')) + sorted(TEST_DIR.glob('*.png'))
print(f"Found {len(test_images)} test image(s)")

# Process each image
results = []
for image_path in test_images:
    print(f"\nProcessing: {image_path.name}")
    
    # Extract record ID from filename
    record_id = image_path.stem.split('.')[0]
    
    # Initialize digitizer
    digitizer = ECGDigitizer(use_segmented_processing=True, enable_visualization=False)
    
    # Process image
    result = digitizer.process_image(str(image_path))
    
    # Extract signals
    signals = {}
    for lead_data in result.get('leads', []):
        lead_name = lead_data['name']
        signal_values = np.array(lead_data['values'])
        
        # Pad or truncate to 5000 samples
        if len(signal_values) < SAMPLES_PER_LEAD:
            padded = np.zeros(SAMPLES_PER_LEAD)
            padded[:len(signal_values)] = signal_values
            signals[lead_name] = padded
        elif len(signal_values) > SAMPLES_PER_LEAD:
            signals[lead_name] = signal_values[:SAMPLES_PER_LEAD]
        else:
            signals[lead_name] = signal_values
    
    # Fill missing leads with zeros
    for lead_name in LEAD_NAMES:
        if lead_name not in signals:
            signals[lead_name] = np.zeros(SAMPLES_PER_LEAD)
    
    results.append({
        'record_id': record_id,
        'signals': signals
    })

# Generate submission.csv
print("\nGenerating submission.csv...")
submission_path = OUTPUT_DIR / 'submission.csv'

with open(submission_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'value'])
    
    for result in results:
        record_id = result['record_id']
        signals = result['signals']
        
        for lead_name in LEAD_NAMES:
            signal = signals[lead_name]
            for sample_idx in range(SAMPLES_PER_LEAD):
                row_id = f"'{record_id}_{sample_idx}_{lead_name}'"
                value = float(signal[sample_idx])
                writer.writerow([row_id, f"{value:.6f}"])

print(f"✓ Submission file created: {submission_path}")
print(f"✓ Total records: {len(results)}")
print("\nReady to submit!")
```

## Testing SNR (Use Train Images)

To test SNR, you **must use train images** (they have ground truth):

```python
# Use test_kaggle_with_snr.py with train images
python test_kaggle_with_snr.py --limit 5
```

This will:
1. Process train images (which have ground truth)
2. Calculate SNR using competition's method
3. Show you how well your pipeline performs

**Note**: The two test images you mentioned **cannot** be used for SNR calculation because they don't have ground truth data.

## File Structure

```
/kaggle/input/physionet-ecg-image-digitization/
├── train/              ← Use these for SNR testing (has ground truth)
│   ├── 62.jpg
│   ├── 63.jpg
│   └── ...
├── test/               ← Use these for submission (no ground truth)
│   ├── image1.jpg      ← Your 2 test images
│   └── image2.jpg
└── train.parquet       ← Ground truth for train images
```

## Submission Checklist

Before submitting:

- [ ] Code runs without errors
- [ ] Processes all test images
- [ ] Generates `submission.csv` in `/kaggle/working/`
- [ ] File has correct format: `id,value` header
- [ ] All IDs are quoted: `'62_0_I'`
- [ ] 12 leads × 5000 samples = 60,000 rows per record
- [ ] No internet access required (offline mode)
- [ ] Runtime < 9 hours

## Quick Test Locally

Before submitting to Kaggle, test locally:

```python
# Test with a single image
from test_kaggle_with_snr import quick_test_single_image

result = quick_test_single_image('path/to/test/image.jpg')
```

This will process the image and extract signals (no SNR, since no ground truth).

## Summary

1. **For Submission**: Use `kaggle_submission_notebook.py` with **test images**
2. **For SNR Testing**: Use `test_kaggle_with_snr.py` with **train images**
3. **Test images have NO ground truth** - cannot calculate SNR on them
4. **Train images have ground truth** - use these to validate your pipeline
