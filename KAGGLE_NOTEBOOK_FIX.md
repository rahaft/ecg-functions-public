# Fix: ModuleNotFoundError in Kaggle Notebook

## Problem
You're getting: `ModuleNotFoundError: No module named 'digitization_pipeline'`

## Solution: Upload Required Files

You need to upload these files to your Kaggle notebook:

### Required Files:
1. `functions_python/digitization_pipeline.py`
2. `functions_python/grid_detection.py`
3. `functions_python/segmented_processing.py`
4. `functions_python/line_visualization.py`

## Quick Fix: Copy Code Directly (Easiest)

Instead of uploading files, **copy the code directly into your notebook**:

### Cell 1: Upload Files (if you want to use files)

In Kaggle notebook:
1. Click **"Add data"** → **"Upload"**
2. Upload these 4 files:
   - `digitization_pipeline.py`
   - `grid_detection.py`
   - `segmented_processing.py`
   - `line_visualization.py`
3. They'll appear in `/kaggle/working/`

### Cell 2: Add to Python Path and Import

```python
import sys
from pathlib import Path

# Add /kaggle/working to path so we can import uploaded files
sys.path.insert(0, '/kaggle/working')

# Now import
from digitization_pipeline import ECGDigitizer
```

### Cell 3: Your Submission Code

```python
import csv
import numpy as np
from pathlib import Path

TEST_DIR = Path('/kaggle/input/physionet-ecg-image-digitization/test')
OUTPUT_DIR = Path('/kaggle/working')

LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SAMPLES_PER_LEAD = 5000

# Find test images
test_images = sorted(TEST_DIR.glob('*.jpg')) + sorted(TEST_DIR.glob('*.png'))
print(f"Found {len(test_images)} test image(s)")

# Process images
results = []
for image_path in test_images:
    import re
    record_id = re.search(r'(\d+)', image_path.stem).group(1)
    print(f"\nProcessing: {image_path.name} (Record ID: {record_id})")
    
    digitizer = ECGDigitizer(use_segmented_processing=True, enable_visualization=False)
    result = digitizer.process_image(str(image_path))
    
    signals = {}
    for lead_data in result.get('leads', []):
        lead_name = lead_data['name']
        if lead_name not in LEAD_NAMES:
            continue
        signal = np.array(lead_data['values'])
        if len(signal) < SAMPLES_PER_LEAD:
            padded = np.zeros(SAMPLES_PER_LEAD)
            padded[:len(signal)] = signal
            signals[lead_name] = padded
        else:
            signals[lead_name] = signal[:SAMPLES_PER_LEAD]
    
    for lead_name in LEAD_NAMES:
        if lead_name not in signals:
            signals[lead_name] = np.zeros(SAMPLES_PER_LEAD)
    
    results.append({'record_id': record_id, 'signals': signals})

# Generate submission.csv
submission_path = OUTPUT_DIR / 'submission.csv'
print(f"\nGenerating: {submission_path}")

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
                writer.writerow([row_id, f"{float(signal[sample_idx]):.6f}"])

print(f"\n✓ Submission file: {submission_path}")
print(f"✓ Records: {len(results)}")
```

## Alternative: Import from File Path

If files are uploaded, import directly:

```python
import sys
import importlib.util

# Load digitization_pipeline.py from file
spec = importlib.util.spec_from_file_location(
    "digitization_pipeline",
    "/kaggle/working/digitization_pipeline.py"
)
digitization_pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(digitization_pipeline)

ECGDigitizer = digitization_pipeline.ECGDigitizer
```

## Checklist

Before running:
- [ ] Upload `digitization_pipeline.py` to `/kaggle/working/`
- [ ] Upload `grid_detection.py` to `/kaggle/working/`
- [ ] Upload `segmented_processing.py` to `/kaggle/working/`
- [ ] Upload `line_visualization.py` to `/kaggle/working/`
- [ ] Add `/kaggle/working` to `sys.path` before importing
- [ ] Verify competition data is attached

## Verify Files Are Uploaded

Run this in a cell to check:

```python
import os
from pathlib import Path

working_dir = Path('/kaggle/working')
required_files = [
    'digitization_pipeline.py',
    'grid_detection.py',
    'segmented_processing.py',
    'line_visualization.py'
]

print("Checking for required files:")
for file in required_files:
    file_path = working_dir / file
    exists = file_path.exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {file}")
    
if all((working_dir / f).exists() for f in required_files):
    print("\n✓ All files found! You can now import.")
else:
    print("\n✗ Some files missing. Upload them first.")
```
