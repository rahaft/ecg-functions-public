# Step-by-Step: Copy-Paste Code into Kaggle Notebook

## Order Matters! Copy in This Exact Order:

### Cell 1: grid_detection.py
**File to copy:** `functions_python/grid_detection.py`  
**Why first:** No dependencies on other custom files

**Steps:**
1. Open `functions_python/grid_detection.py` in your editor
2. Select ALL the code (Ctrl+A / Cmd+A)
3. Copy (Ctrl+C / Cmd+C)
4. In Kaggle notebook, create a new cell
5. Paste the code
6. Run the cell (Shift+Enter)

---

### Cell 2: segmented_processing.py
**File to copy:** `functions_python/segmented_processing.py`  
**Why second:** No dependencies on other custom files

**Steps:**
1. Open `functions_python/segmented_processing.py` in your editor
2. **Add this at the VERY TOP** (before the docstring):
   ```python
   print("=" * 70)
   print("STEP 2: Loading segmented_processing.py")
   print("=" * 70)
   print("File: functions_python/segmented_processing.py")
   print("Status: Starting...")
   ```
3. **Add this at the VERY END** (after the class definition):
   ```python
   print("\n" + "=" * 70)
   print("STEP 2: segmented_processing.py loaded successfully!")
   print("File: functions_python/segmented_processing.py")
   print("Status: ✓ SUCCESS")
   print("Class: SegmentedProcessor is now available")
   print("=" * 70)
   ```
4. Select ALL the code (Ctrl+A)
5. Copy (Ctrl+C)
6. In Kaggle notebook, create a new cell (below Cell 1)
7. Paste the code
8. Run the cell (Shift+Enter)

**Expected Output:**
```
======================================================================
STEP 2: Loading segmented_processing.py
======================================================================
File: functions_python/segmented_processing.py
Status: Starting...

[... class definition ...]

======================================================================
STEP 2: segmented_processing.py loaded successfully!
File: functions_python/segmented_processing.py
Status: ✓ SUCCESS
Class: SegmentedProcessor is now available
======================================================================
```

---

### Cell 3: line_visualization.py
**File to copy:** `functions_python/line_visualization.py`  
**Why third:** No dependencies on other custom files

**Steps:**
1. Open `functions_python/line_visualization.py` in your editor
2. **Add this at the VERY TOP** (before the docstring):
   ```python
   print("=" * 70)
   print("STEP 3: Loading line_visualization.py")
   print("=" * 70)
   print("File: functions_python/line_visualization.py")
   print("Status: Starting...")
   ```
3. **Add this at the VERY END** (after the class definition):
   ```python
   print("\n" + "=" * 70)
   print("STEP 3: line_visualization.py loaded successfully!")
   print("File: functions_python/line_visualization.py")
   print("Status: ✓ SUCCESS")
   print("Class: LineVisualizer is now available")
   print("=" * 70)
   ```
4. Select ALL the code (Ctrl+A)
5. Copy (Ctrl+C)
6. In Kaggle notebook, create a new cell (below Cell 2)
7. Paste the code
8. Run the cell (Shift+Enter)

**Expected Output:**
```
======================================================================
STEP 3: Loading line_visualization.py
======================================================================
File: functions_python/line_visualization.py
Status: Starting...

[... class definition ...]

======================================================================
STEP 3: line_visualization.py loaded successfully!
File: functions_python/line_visualization.py
Status: ✓ SUCCESS
Class: LineVisualizer is now available
======================================================================
```

---

### Cell 4: digitization_pipeline.py (IMPORTANT: FIXED VERSION)
**File to copy:** `functions_python/digitization_pipeline.py`  
**Why fourth:** Depends on grid_detection, segmented_processing, line_visualization

**⚠️ CRITICAL FIX:** The import statements need to be modified to work in Kaggle notebook cells!

**Steps:**
1. Open `functions_python/digitization_pipeline.py` in your editor
2. Find lines 17-19 (the import statements):
   ```python
   from grid_detection import GridDetector
   from segmented_processing import SegmentedProcessor
   from line_visualization import LineVisualizer
   ```
3. **REPLACE those 3 lines** with the code from `kaggle_cell_4_fixed_imports.py` (the import section)
4. Add the header from `KAGGLE_CELL_4_FIXED_IMPORTS.py` at the very top (before the docstring)
5. Add the success message at the very end (after the class definition)
6. Copy ALL the modified code (Ctrl+A)
7. In Kaggle notebook, create a new cell (below Cell 3)
8. Paste the code
9. Run the cell (Shift+Enter)

**Expected Output:**
```
======================================================================
STEP 4: Loading digitization_pipeline.py
======================================================================
File: functions_python/digitization_pipeline.py
Status: Starting...

[Step 4.1] Loading GridDetector...
  ✓ Success: Loaded GridDetector from Cell 1 (grid_detection.py)

[Step 4.2] Loading SegmentedProcessor...
  ✓ Success: Loaded SegmentedProcessor from Cell 2 (segmented_processing.py)

[Step 4.3] Loading LineVisualizer...
  ✓ Success: Loaded LineVisualizer from Cell 3 (line_visualization.py)

======================================================================
STEP 4: All dependencies loaded successfully!
File: functions_python/digitization_pipeline.py
Status: Loading ECGDigitizer class...
======================================================================

[... class definition ...]

======================================================================
STEP 4: digitization_pipeline.py loaded successfully!
File: functions_python/digitization_pipeline.py
Status: ✓ SUCCESS
Class: ECGDigitizer is now available
======================================================================
```

---

### Cell 5: Submission Code
**File to copy:** `kaggle_notebook_complete.py` (from STEP 2 onwards)  
**Why last:** Depends on digitization_pipeline

**Steps:**
1. Open `kaggle_notebook_complete.py` in your editor
2. Find the section `# STEP 2: Configuration` (skip STEP 1 comments)
3. **Add this at the VERY TOP** (before STEP 2):
   ```python
   print("=" * 70)
   print("STEP 5: Running submission code")
   print("=" * 70)
   print("File: kaggle_notebook_complete.py (STEP 2 section)")
   print("Status: Starting...")
   ```
4. Copy from `# STEP 2: Configuration` to the END of the file
5. In Kaggle notebook, create a new cell (below Cell 4)
6. Paste the code
7. Run the cell (Shift+Enter)

**Expected Output:**
```
======================================================================
STEP 5: Running submission code
======================================================================
File: kaggle_notebook_complete.py (STEP 2 section)
Status: Starting...

[... rest of output with processing and submission generation ...]

======================================================================
✅ READY FOR SUBMISSION!
======================================================================
```

**OR** use the complete ready-to-paste version: `kaggle_cell_4_ready_to_paste.py`

**OR** copy this simplified version:

```python
import sys
import csv
import numpy as np
from pathlib import Path

# Add /kaggle/working to Python path (in case files were uploaded)
sys.path.insert(0, '/kaggle/working')

# Import digitization pipeline (from previous cells)
from digitization_pipeline import ECGDigitizer

# Configuration
COMPETITION_NAME = "physionet-ecg-image-digitization"
INPUT_DIR = Path('/kaggle/input') / COMPETITION_NAME
TEST_DIR = INPUT_DIR / 'test'
OUTPUT_DIR = Path('/kaggle/working')

LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SAMPLES_PER_LEAD = 5000

def extract_record_id(image_path: Path) -> str:
    """Extract record ID from filename"""
    import re
    match = re.search(r'(\d+)', image_path.stem)
    return match.group(1) if match else image_path.stem

def find_test_images() -> list:
    """Find all test images"""
    images = []
    if not TEST_DIR.exists():
        print(f"✗ Test directory not found: {TEST_DIR}")
        return images
    
    for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.JPG', '.JPEG', '.PNG']:
        images.extend(TEST_DIR.glob(f'*{ext}'))
    
    return sorted(images)

def process_image(image_path: Path) -> dict:
    """Process a single ECG image"""
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
        
        # Fill missing leads
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

# Main execution
print("=" * 70)
print("Kaggle ECG Digitization Submission")
print("=" * 70)

# Find test images
test_images = find_test_images()

if not test_images:
    print("\n✗ No test images found!")
    print(f"Expected location: {TEST_DIR}")
    print("\nMake sure:")
    print("1. Competition data is attached to notebook")
    print("2. Test images are in /kaggle/input/physionet-ecg-image-digitization/test/")
else:
    print(f"\n✓ Found {len(test_images)} test image(s):")
    for img in test_images:
        print(f"  - {img.name}")
    
    # Process images
    print(f"\n{'=' * 70}")
    print(f"Processing {len(test_images)} image(s)...")
    print(f"{'=' * 70}")
    results = []
    for i, image_path in enumerate(test_images, 1):
        print(f"\n[{i}/{len(test_images)}] ", end="")
        result = process_image(image_path)
        results.append(result)
    
    successful = sum(1 for r in results if r.get('success', False))
    print(f"\n{'=' * 70}")
    print(f"Processing Complete: {successful}/{len(test_images)} images successful")
    print(f"{'=' * 70}")
    
    # Generate submission.csv
    submission_path = OUTPUT_DIR / 'submission.csv'
    print(f"\n{'=' * 70}")
    print(f"Generating submission file...")
    print(f"{'=' * 70}")
    print(f"Output: {submission_path}")
    
    rows_written = 0
    total_expected = len(results) * len(LEAD_NAMES) * SAMPLES_PER_LEAD
    
    with open(submission_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'value'])
        
        for result_idx, result in enumerate(results, 1):
            record_id = result['record_id']
            signals = result['signals']
            
            print(f"  Writing record {record_id} ({result_idx}/{len(results)})...", end="")
            
            record_rows = 0
            for lead_name in LEAD_NAMES:
                signal = signals[lead_name]
                for sample_idx in range(SAMPLES_PER_LEAD):
                    row_id = f"'{record_id}_{sample_idx}_{lead_name}'"
                    value = float(signal[sample_idx])
                    writer.writerow([row_id, f"{value:.6f}"])
                    rows_written += 1
                    record_rows += 1
            
            print(f" {record_rows:,} rows")
    
    # Validate submission file
    file_size_kb = submission_path.stat().st_size / 1024
    file_size_mb = file_size_kb / 1024
    expected_rows = len(results) * len(LEAD_NAMES) * SAMPLES_PER_LEAD
    
    # Summary
    print("\n" + "=" * 70)
    print("🎉 SUBMISSION COMPLETE! 🎉")
    print("=" * 70)
    print(f"\n📄 Submission File Details:")
    print(f"   File: {submission_path}")
    print(f"   Size: {file_size_mb:.2f} MB ({file_size_kb:.2f} KB)")
    print(f"   Rows: {rows_written:,} (Expected: {expected_rows:,})")
    
    if rows_written == expected_rows:
        print(f"   ✓ Row count: CORRECT")
    else:
        print(f"   ⚠ Row count: MISMATCH")
    
    print(f"\n📊 Processing Summary:")
    print(f"   Records processed: {len(results)}")
    successful = sum(1 for r in results if r.get('success', False))
    print(f"   Successfully processed: {successful}/{len(results)}")
    
    print(f"\n📋 Record Details:")
    for i, result in enumerate(results, 1):
        status = "✓" if result.get('success') else "✗"
        record_id = result['record_id']
        leads_count = len([s for s in result['signals'].values() if np.any(s != 0)])
        print(f"   {i}. {status} Record {record_id}: {leads_count} leads extracted")
    
    print(f"\n✅ Validation:")
    print(f"   ✓ File exists: {submission_path.exists()}")
    print(f"   ✓ File readable: {submission_path.is_file()}")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Verify submission.csv format is correct")
    print(f"   2. Commit this notebook")
    print(f"   3. Click 'Submit' button in Kaggle")
    print(f"\n" + "=" * 70)
    print("✅ READY FOR SUBMISSION!")
    print("=" * 70)
```

---

## Quick Checklist

Copy in this order:
- [ ] **Cell 1:** `grid_detection.py` (entire file)
- [ ] **Cell 2:** `segmented_processing.py` (entire file)
- [ ] **Cell 3:** `line_visualization.py` (entire file)
- [ ] **Cell 4:** `digitization_pipeline.py` (entire file)
- [ ] **Cell 5:** Submission code (from above)

## After Pasting

1. Run each cell in order (Shift+Enter)
2. Check for errors - if Cell 4 fails, make sure Cells 1-3 ran successfully
3. Cell 5 will process images and create `submission.csv`

---

<!-- ============================================================================ -->
<!-- FILE IDENTIFICATION -->
<!-- ============================================================================ -->
<!-- This file: kaggle_copy_paste_steps.md -->
<!-- Purpose: Detailed copy-paste instructions for Kaggle notebook setup -->
<!-- ============================================================================ -->

## Expected Output

After running Cell 5, you should see:
```
======================================================================
Kaggle ECG Digitization Submission
======================================================================

✓ Found 2 test image(s):
  - image1.jpg
  - image2.jpg

Processing 2 image(s)...
[Processing output...]

✓ Submission file: /kaggle/working/submission.csv
✓ Records processed: 2
✓ Total rows: 120000
```

## Troubleshooting

**If Cell 4 fails with "No module named 'grid_detection'":**
- Make sure you ran Cells 1, 2, 3 first
- Check for errors in previous cells

**If Cell 5 fails with "No module named 'digitization_pipeline'":**
- Make sure Cell 4 ran successfully
- Check that all previous cells executed without errors
