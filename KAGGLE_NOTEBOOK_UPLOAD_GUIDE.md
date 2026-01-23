# What to Upload to Kaggle Notebook

## Quick Answer

**You need to upload:**
1. ✅ `create_kaggle_submission.py` (or use the code directly in notebook)
2. ✅ `functions_python/digitization_pipeline.py` (and all its dependencies)
3. ✅ All files that `digitization_pipeline.py` imports

## Option 1: Use create_kaggle_submission.py (Recommended)

### Step 1: Upload Required Files

Upload these files to your Kaggle notebook:

```
/kaggle/working/
├── create_kaggle_submission.py          ← Your submission script
├── digitization_pipeline.py             ← From functions_python/
└── [all other files digitization_pipeline.py needs]
```

**What files does `digitization_pipeline.py` need?**
Check what it imports - you'll likely need:
- `functions_python/digitization_pipeline.py`
- `functions_python/transformers/` directory (if used)
- Any other modules it imports

### Step 2: Run in Kaggle Notebook

```python
# In a Kaggle notebook cell:
!python create_kaggle_submission.py --test-dir /kaggle/input/physionet-ecg-image-digitization/test --output /kaggle/working/submission.csv
```

## Option 2: Copy Code Directly into Notebook (Easier)

Instead of uploading files, copy the code directly into your Kaggle notebook:

### Cell 1: Copy digitization_pipeline.py
```python
# Paste the entire contents of functions_python/digitization_pipeline.py here
# (or import it if you upload it)
```

### Cell 2: Copy create_kaggle_submission.py (Modified for Kaggle)
```python
# Modified version for Kaggle notebook
import os
import sys
import csv
import numpy as np
from pathlib import Path
from typing import Dict, List

# Import digitization pipeline (adjust path if needed)
from digitization_pipeline import ECGDigitizer

# Competition configuration
COMPETITION_NAME = "physionet-ecg-image-digitization"
INPUT_DIR = Path('/kaggle/input') / COMPETITION_NAME
TEST_DIR = INPUT_DIR / 'test'
OUTPUT_DIR = Path('/kaggle/working')

LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SAMPLES_PER_LEAD = 5000

def extract_record_id(image_path: Path) -> str:
    filename = image_path.stem
    import re
    match = re.search(r'(\d+)', filename)
    if match:
        return match.group(1)
    return filename.replace(' ', '_').replace('-', '_')

def find_test_images() -> List[Path]:
    images = []
    if not TEST_DIR.exists():
        print(f"Warning: Test directory not found: {TEST_DIR}")
        return images
    for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.JPG', '.JPEG', '.PNG']:
        images.extend(TEST_DIR.glob(f'*{ext}'))
    return sorted(images)

def process_image(image_path: Path) -> Dict:
    record_id = extract_record_id(image_path)
    print(f"\nProcessing: {image_path.name} (Record ID: {record_id})")
    
    try:
        digitizer = ECGDigitizer(use_segmented_processing=True, enable_visualization=False)
        result = digitizer.process_image(str(image_path))
        
        signals = {}
        for lead_data in result.get('leads', []):
            lead_name = lead_data['name']
            if lead_name not in LEAD_NAMES:
                continue
            signal_values = np.array(lead_data['values'])
            if len(signal_values) < SAMPLES_PER_LEAD:
                padded = np.zeros(SAMPLES_PER_LEAD)
                padded[:len(signal_values)] = signal_values
                signals[lead_name] = padded
            elif len(signal_values) > SAMPLES_PER_LEAD:
                signals[lead_name] = signal_values[:SAMPLES_PER_LEAD]
            else:
                signals[lead_name] = signal_values
        
        for lead_name in LEAD_NAMES:
            if lead_name not in signals:
                signals[lead_name] = np.zeros(SAMPLES_PER_LEAD)
        
        return {'record_id': record_id, 'signals': signals, 'success': True}
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        signals = {lead: np.zeros(SAMPLES_PER_LEAD) for lead in LEAD_NAMES}
        return {'record_id': record_id, 'signals': signals, 'success': False}

# Main execution
print("=" * 70)
print("Kaggle ECG Digitization Submission")
print("=" * 70)

test_images = find_test_images()
print(f"\nFound {len(test_images)} test image(s)")

results = []
for image_path in test_images:
    result = process_image(image_path)
    results.append(result)

# Generate submission.csv
submission_path = OUTPUT_DIR / 'submission.csv'
print(f"\nGenerating: {submission_path}")

with open(submission_path, 'w', newline='', encoding='utf-8') as f:
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

print(f"\n✓ Submission file created: {submission_path}")
print(f"✓ Records processed: {len(results)}")
```

## Option 3: Use kaggle_submission_notebook.py

This file is already optimized for Kaggle. Just upload it and run:

```python
exec(open('/kaggle/working/kaggle_submission_notebook.py').read())
```

## Checklist: What You Need

### Required Files:
- [ ] `digitization_pipeline.py` (from `functions_python/`)
- [ ] All files that `digitization_pipeline.py` imports
- [ ] `create_kaggle_submission.py` OR copy code into notebook

### Dependencies (usually pre-installed in Kaggle):
- [x] numpy
- [x] opencv-python (cv2)
- [x] scipy
- [x] pandas (if used)

### If you use transformers:
- [ ] `functions_python/transformers/` directory
- [ ] All transformer files your pipeline uses

## How to Upload Files to Kaggle

1. **In Kaggle Notebook:**
   - Click "Add data" → "Upload"
   - Upload your `.py` files
   - They'll appear in `/kaggle/working/`

2. **Or use Kaggle API:**
   ```bash
   kaggle kernels push -p /path/to/your/notebook
   ```

3. **Or copy-paste code:**
   - Just paste the code directly into notebook cells
   - No file upload needed

## Recommended Approach

**Easiest: Copy code directly into notebook cells**

1. **Cell 1:** Paste `digitization_pipeline.py` code
2. **Cell 2:** Paste the submission code (from Option 2 above)
3. **Run both cells**

This avoids file upload issues and works immediately.

## Verify It Works

After running, check:
- [ ] `submission.csv` exists in `/kaggle/working/`
- [ ] File has correct format (header: `id,value`)
- [ ] Row count: 120,000 (2 records × 12 leads × 5000 samples)
- [ ] IDs are quoted: `'16640_0_I'`
- [ ] No errors in output

## Troubleshooting

### "Module not found"
- Make sure you uploaded all required files
- Check import paths match your file structure
- Use absolute paths: `/kaggle/working/digitization_pipeline.py`

### "Test directory not found"
- Verify competition data is attached
- Check path: `/kaggle/input/physionet-ecg-image-digitization/test/`
- Use `!ls /kaggle/input/` to see what's available

### "Pipeline not available"
- Check that `digitization_pipeline.py` is uploaded/copied
- Verify all its dependencies are available
- Check for import errors in the output
