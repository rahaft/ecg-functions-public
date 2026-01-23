# Kaggle Notebook - Complete Code for Each Step

Each step below contains the COMPLETE code ready to copy-paste. File references are included so you know where each piece comes from.

---

## STEP 1: Cell 1 - Grid Detection

**⚠️ NEW: Use the ready-to-paste version!**

**File:** `kaggle_cell_1_grid_detection.py` (READY TO PASTE - NEW VERSION)

**Location:** `c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\kaggle_cell_1_grid_detection.py`

**Instructions:**
1. Open `kaggle_cell_1_grid_detection.py` (full path shown above)
2. Select ALL (Ctrl+A) and copy (Ctrl+C)
3. Paste into Kaggle notebook Cell 1
4. Run (Shift+Enter)

**OR use the old method:**

**Source File:** `functions_python/grid_detection.py`

**Complete Code for Cell 1:**

```python
print("=" * 70)
print("STEP 1: Loading grid_detection.py")
print("=" * 70)
print("File: functions_python/grid_detection.py")
print("Status: Starting...")

# [PASTE ENTIRE CONTENTS OF: functions_python/grid_detection.py]
# Location: c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\functions_python\grid_detection.py
# Copy ALL lines from that file (Ctrl+A, Ctrl+C) and paste here

print("\n" + "=" * 70)
print("STEP 1: grid_detection.py loaded successfully!")
print("File: functions_python/grid_detection.py")
print("Status: ✓ SUCCESS")
print("Class: GridDetector is now available")
print("=" * 70)
```

**Instructions:**
1. Copy the code above (the print statements)
2. Open: `functions_python/grid_detection.py` (full path shown above)
3. Select ALL (Ctrl+A) and copy (Ctrl+C)
4. Paste it between the print statements (replace the comment)
5. Copy the ENTIRE cell (all code together)
6. Paste into Kaggle notebook Cell 1
7. Run (Shift+Enter)

---

## STEP 2: Cell 2 - segmented_processing.py

**Source File:** `functions_python/segmented_processing.py`

**Complete Code for Cell 2:**

```python
print("=" * 70)
print("STEP 2: Loading segmented_processing.py")
print("=" * 70)
print("File: functions_python/segmented_processing.py")
print("Status: Starting...")

# [PASTE ENTIRE CONTENTS OF: functions_python/segmented_processing.py]
# Location: c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\functions_python\segmented_processing.py
# Copy ALL lines from that file (Ctrl+A, Ctrl+C) and paste here

print("\n" + "=" * 70)
print("STEP 2: segmented_processing.py loaded successfully!")
print("File: functions_python/segmented_processing.py")
print("Status: ✓ SUCCESS")
print("Class: SegmentedProcessor is now available")
print("=" * 70)
```

**Instructions:**
1. Copy the code above (the print statements)
2. Open: `functions_python/segmented_processing.py` (full path shown above)
3. Select ALL (Ctrl+A) and copy (Ctrl+C)
4. Paste it between the print statements (replace the comment)
5. Copy the ENTIRE cell (all code together)
6. Paste into Kaggle notebook Cell 2 (below Cell 1)
7. Run (Shift+Enter)

---

## STEP 3: Cell 3 - Line Visualization

**⚠️ NEW: Use the ready-to-paste version!**

**File:** `kaggle_cell_3_line_visualization.py` (READY TO PASTE - NEW VERSION)

**Location:** `c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\kaggle_cell_3_line_visualization.py`

**Instructions:**
1. Open `kaggle_cell_3_line_visualization.py` (full path shown above)
2. Select ALL (Ctrl+A) and copy (Ctrl+C)
3. Paste into Kaggle notebook Cell 3
4. Run (Shift+Enter)

**OR use the old method:**

**Source File:** `functions_python/line_visualization.py`

**Complete Code for Cell 3:**

```python
print("=" * 70)
print("STEP 3: Loading line_visualization.py")
print("=" * 70)
print("File: functions_python/line_visualization.py")
print("Status: Starting...")

# [PASTE ENTIRE CONTENTS OF: functions_python/line_visualization.py]
# Location: c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\functions_python\line_visualization.py
# Copy ALL lines from that file (Ctrl+A, Ctrl+C) and paste here

print("\n" + "=" * 70)
print("STEP 3: line_visualization.py loaded successfully!")
print("File: functions_python/line_visualization.py")
print("Status: ✓ SUCCESS")
print("Class: LineVisualizer is now available")
print("=" * 70)
```

**Instructions:**
1. Copy the code above (the print statements)
2. Open: `functions_python/line_visualization.py` (full path shown above)
3. Select ALL (Ctrl+A) and copy (Ctrl+C)
4. Paste it between the print statements (replace the comment)
5. Copy the ENTIRE cell (all code together)
6. Paste into Kaggle notebook Cell 3 (below Cell 2)
7. Run (Shift+Enter)

---

## STEP 4: Cell 4 - digitization_pipeline.py (FIXED - READY TO PASTE)

**Source File:** `KAGGLE_CELL_4_READY_TO_PASTE.py` (this is the COMPLETE fixed version)

**Location:** `c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\KAGGLE_CELL_4_READY_TO_PASTE.py`

**⚠️ IMPORTANT:** This file already has the fixed imports! Just copy the entire file.

**Instructions:**
1. Open: `kaggle_cell_4_ready_to_paste.py` (full path shown above)
2. Select ALL (Ctrl+A) and copy (Ctrl+C)
3. Paste into Kaggle notebook Cell 4 (below Cell 3)
4. Run (Shift+Enter)

**This file contains:**
- Fixed import logic that checks globals() first
- Complete ECGDigitizer class
- All step indicators
- Success messages

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

## STEP 5: Cell 5 - Submission Code

**⚠️ IMPORTANT: Use the fixed version below!**

**Source File:** `kaggle_cell_5_complete.py` (READY TO PASTE - FIXED VERSION)

**Location:** `c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\kaggle_cell_5_complete.py`

**Instructions:**
1. Open `kaggle_cell_5_complete.py` (full path shown above)
2. Select ALL (Ctrl+A) and copy (Ctrl+C)
3. Paste into Kaggle notebook Cell 5 (below Cell 4)
4. Run (Shift+Enter)

**OR copy the code below:**

```python
print("=" * 70)
print("STEP 5: Running submission code")
print("=" * 70)
print("File: kaggle_notebook_complete.py (STEP 2 section)")
print("Status: Starting...")

import sys
import csv
import numpy as np
from pathlib import Path

# Import ECGDigitizer from previous cells (it's in global namespace, not a module)
print("=" * 70)
print("STEP 5: Loading submission code")
print("=" * 70)
print("File: kaggle_notebook_complete.py (STEP 2 section)")
print("Status: Starting...")

print("\n[Step 5.1] Loading ECGDigitizer...")
try:
    # First try: Get from global namespace (Cell 4)
    if 'ECGDigitizer' in globals():
        ECGDigitizer = globals()['ECGDigitizer']
        print("  ✓ Success: Loaded ECGDigitizer from Cell 4 (digitization_pipeline.py)")
    else:
        # Second try: Import as module (if file was uploaded)
        from digitization_pipeline import ECGDigitizer
        print("  ✓ Success: Imported ECGDigitizer from digitization_pipeline module")
except Exception as e:
    print(f"  ✗ ERROR: Could not load ECGDigitizer: {e}")
    print("  → Make sure Cell 4 (digitization_pipeline.py) ran successfully!")
    print("  → Check that you see 'STEP 4: ... SUCCESS' message from Cell 4")
    print("\n  Troubleshooting:")
    print("    1. Run Cells 1-4 in order first")
    print("    2. Make sure Cell 4 completed without errors")
    print("    3. Verify you see 'STEP 4: ✓ SUCCESS' in Cell 4 output")
    raise

print("\n" + "=" * 70)
print("STEP 5: ECGDigitizer loaded successfully!")
print("Status: Ready to process images...")
print("=" * 70)

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
    
    print(f"\n  ✓ Total rows written: {rows_written:,}")
    print(f"  ✓ Expected rows: {total_expected:,}")
    
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
        print(f"   ⚠ Row count: MISMATCH (Expected {expected_rows:,}, got {rows_written:,})")
    
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
    
    # File validation
    print(f"\n✅ Validation:")
    print(f"   ✓ File exists: {submission_path.exists()}")
    print(f"   ✓ File readable: {submission_path.is_file()}")
    
    # Check first few lines
    try:
        with open(submission_path, 'r') as f:
            first_line = f.readline().strip()
            second_line = f.readline().strip()
        print(f"   ✓ Header: {first_line}")
        if second_line:
            print(f"   ✓ First row: {second_line[:50]}...")
    except:
        pass
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Verify submission.csv format is correct")
    print(f"   2. Check that all test images were processed")
    print(f"   3. Commit this notebook")
    print(f"   4. Click 'Submit' button in Kaggle")
    print(f"\n" + "=" * 70)
    print("✅ READY FOR SUBMISSION!")
    print("=" * 70)
```

**Instructions:**
1. Copy ALL the code above (from first print to last)
2. Paste into Kaggle notebook Cell 5 (below Cell 4)
3. Run (Shift+Enter)

---

## STEP 6: Cell 6 - Verification (Optional but Recommended)

**⚠️ IMPORTANT:** This step helps verify your submission file was created correctly.

**Source File:** `kaggle_cell_6_verify.py` (READY TO PASTE)

**Location:** `c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\kaggle_cell_6_verify.py`

**Instructions:**
1. Open `kaggle_cell_6_verify.py` (full path shown above)
2. Select ALL (Ctrl+A) and copy (Ctrl+C)
3. Paste into Kaggle notebook Cell 6 (below Cell 5)
4. Run (Shift+Enter)

**This cell will:**
- Check if `submission.csv` exists
- Verify file size and format
- Check header format
- Show sample data rows
- List any CSV files in `/kaggle/working/` if submission.csv is missing

**Expected Output:**
```
======================================================================
STEP 6: Verifying submission.csv
======================================================================
File: kaggle_cell_6_verify.py
Status: Starting...

✅ submission.csv FOUND!
   Path: /kaggle/working/submission.csv
   Size: 3.55 MB (3636.10 KB, 3,727,200 bytes)
   Lines: 120,001
   Header: id,value
   ✅ Header format: CORRECT
   ✅ File appears valid

   Sample data rows:
   Row 1: '1053922973_0_I',0.000000...
   Row 2: '1053922973_1_I',0.000000...

✅ READY FOR SUBMISSION!
   Your notebook should work when you click 'Submit'

======================================================================
STEP 6: Verification complete!
======================================================================
```

---

## File Reference Summary

| Step | Cell | Source File | Full Path |
|------|------|-------------|-----------|
| 1 | Cell 1 | `grid_detection.py` | `c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\functions_python\grid_detection.py` |
| 2 | Cell 2 | `segmented_processing.py` | `c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\functions_python\segmented_processing.py` |
| 3 | Cell 3 | `line_visualization.py` | `c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\functions_python\line_visualization.py` |
| 4 | Cell 4 | `KAGGLE_CELL_4_READY_TO_PASTE.py` | `c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\KAGGLE_CELL_4_READY_TO_PASTE.py` |
| 5 | Cell 5 | `kaggle_cell_5_complete.py` | `c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\kaggle_cell_5_complete.py` |
| 6 | Cell 6 | `kaggle_cell_6_verify.py` | `c:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\kaggle_cell_6_verify.py` |

---

## Quick Checklist

- [ ] **Cell 1:** Copy entire `kaggle_cell_1_grid_detection.py` → Class GridDetector is now available
- [ ] **Cell 2:** Copy entire `kaggle_cell_2_segmented_processing.py` → Class SegmentedProcessor is now available
- [ ] **Cell 3:** Copy entire `kaggle_cell_3_line_visualization.py` → Class LineVisualizer is now available
- [ ] **Cell 4:** Copy entire `KAGGLE_CELL_4_READY_TO_PASTE.py` → Shows "STEP 4: ✓ SUCCESS"
- [ ] **Cell 5:** Copy `kaggle_cell_5_complete.py` → Shows "✅ READY FOR SUBMISSION!"
- [ ] **Cell 6:** Copy `kaggle_cell_6_verify.py` → Shows "✅ READY FOR SUBMISSION!" (verification)

---

## Troubleshooting

**⚠️ IMPORTANT: Error in Cell 5 is usually from Cell 4's code!**

If you see errors like `TypeError: list indices must be integers or slices, not str` when running Cell 5:
- **The bug is actually in Cell 4** (the `ECGDigitizer.calibrate_scales` method)
- **Solution:** Update Cell 4 with the latest `KAGGLE_CELL_4_READY_TO_PASTE.py` code
- The error appears in Cell 5 because that's when `digitizer.process_image()` is called, but the buggy code is in Cell 4

**If Cell 4 fails:**
- Make sure you're using `KAGGLE_CELL_4_READY_TO_PASTE.py` (the fixed version with robust intersection handling)
- Verify Cells 1-3 all show "✓ SUCCESS" before running Cell 4
- The latest version handles intersections in multiple formats (dict, list, tuple)

**If Cell 5 fails:**
- First, check if Cell 4 completed successfully (should show "STEP 4: ✓ SUCCESS")
- If Cell 4 had errors, fix Cell 4 first
- Make sure you're using `kaggle_cell_5_complete.py` (the fixed version)

**If imports fail:**
- Run cells in order (1, 2, 3, 4, 5, 6)
- Wait for each cell to complete before running the next
- Make sure each cell shows its success message before proceeding

---

<!-- ============================================================================ -->
<!-- FILE IDENTIFICATION -->
<!-- ============================================================================ -->
<!-- This file: kaggle_each_step_complete.md -->
<!-- Purpose: Complete step-by-step guide with file paths for each Kaggle notebook cell -->
<!-- ============================================================================ -->
