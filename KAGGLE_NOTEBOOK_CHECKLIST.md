# Kaggle Notebook Setup - Copy-Paste Checklist

## ✅ Copy-Paste Order (Do This Exactly)

### 📋 Cell 1: grid_detection.py
```
File: functions_python/grid_detection.py
Action: Copy ENTIRE file → Paste in Cell 1 → Run
```

### 📋 Cell 2: segmented_processing.py
```
File: functions_python/segmented_processing.py
Action: Copy ENTIRE file → Paste in Cell 2 → Run
```

### 📋 Cell 3: line_visualization.py
```
File: functions_python/line_visualization.py
Action: Copy ENTIRE file → Paste in Cell 3 → Run
```

### 📋 Cell 4: digitization_pipeline.py
```
File: functions_python/digitization_pipeline.py
Action: Copy ENTIRE file → Paste in Cell 4 → Run
```

### 📋 Cell 5: Submission Code
```
File: Copy the code below (or from kaggle_notebook_complete.py STEP 4)
Action: Paste in Cell 5 → Run
```

---

## 📝 Cell 5 Code (Copy This):

```python
import sys
import csv
import numpy as np
from pathlib import Path

sys.path.insert(0, '/kaggle/working')
from digitization_pipeline import ECGDigitizer

COMPETITION_NAME = "physionet-ecg-image-digitization"
INPUT_DIR = Path('/kaggle/input') / COMPETITION_NAME
TEST_DIR = INPUT_DIR / 'test'
OUTPUT_DIR = Path('/kaggle/working')

LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SAMPLES_PER_LEAD = 5000

def extract_record_id(image_path: Path) -> str:
    import re
    match = re.search(r'(\d+)', image_path.stem)
    return match.group(1) if match else image_path.stem

def find_test_images() -> list:
    images = []
    if not TEST_DIR.exists():
        print(f"✗ Test directory not found: {TEST_DIR}")
        return images
    for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.JPG', '.JPEG', '.PNG']:
        images.extend(TEST_DIR.glob(f'*{ext}'))
    return sorted(images)

def process_image(image_path: Path) -> dict:
    record_id = extract_record_id(image_path)
    print(f"\nProcessing: {image_path.name}")
    print(f"  Record ID: {record_id}")
    
    try:
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
            elif len(signal) > SAMPLES_PER_LEAD:
                signals[lead_name] = signal[:SAMPLES_PER_LEAD]
            else:
                signals[lead_name] = signal
        
        for lead_name in LEAD_NAMES:
            if lead_name not in signals:
                signals[lead_name] = np.zeros(SAMPLES_PER_LEAD)
        
        print(f"  ✓ Extracted {len([s for s in signals.values() if np.any(s != 0)])} leads")
        return {'record_id': record_id, 'signals': signals, 'success': True}
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        signals = {lead: np.zeros(SAMPLES_PER_LEAD) for lead in LEAD_NAMES}
        return {'record_id': record_id, 'signals': signals, 'success': False}

print("=" * 70)
print("Kaggle ECG Digitization Submission")
print("=" * 70)

test_images = find_test_images()

if not test_images:
    print("\n✗ No test images found!")
    print(f"Expected location: {TEST_DIR}")
else:
    print(f"\n✓ Found {len(test_images)} test image(s):")
    for img in test_images:
        print(f"  - {img.name}")
    
    print(f"\nProcessing {len(test_images)} image(s)...")
    results = []
    for image_path in test_images:
        result = process_image(image_path)
        results.append(result)
    
    submission_path = OUTPUT_DIR / 'submission.csv'
    print(f"\nGenerating submission file: {submission_path}")
    
    rows_written = 0
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
                    rows_written += 1
    
    print("\n" + "=" * 70)
    print("Submission Complete!")
    print("=" * 70)
    print(f"✓ Submission file: {submission_path}")
    print(f"✓ Records processed: {len(results)}")
    print(f"✓ Total rows: {rows_written}")
    
    for result in results:
        status = "✓" if result.get('success') else "✗"
        print(f"  {status} Record {result['record_id']}")
```

---

## ✅ Verification Checklist

After running all cells:
- [ ] Cell 1 ran without errors
- [ ] Cell 2 ran without errors
- [ ] Cell 3 ran without errors
- [ ] Cell 4 ran without errors
- [ ] Cell 5 found test images
- [ ] Cell 5 processed images
- [ ] `submission.csv` created in `/kaggle/working/`
- [ ] File has 120,000 rows (2 records × 12 leads × 5000 samples)

---

## 🎯 Quick Reference

**Files to copy (in order):**
1. `functions_python/grid_detection.py`
2. `functions_python/segmented_processing.py`
3. `functions_python/line_visualization.py`
4. `functions_python/digitization_pipeline.py`
5. Submission code (from above)

**Each cell:** Copy entire file → Paste → Run → Check for errors
