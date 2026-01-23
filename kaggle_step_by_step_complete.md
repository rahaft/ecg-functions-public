# Kaggle Notebook - Step-by-Step Copy-Paste Guide

Copy each section below into a separate cell in your Kaggle notebook, in order.

---

## STEP 1: Cell 1 - grid_detection.py

**Copy everything below this line into Cell 1:**

```python
print("=" * 70)
print("STEP 1: Loading grid_detection.py")
print("=" * 70)
print("File: functions_python/grid_detection.py")
print("Status: Starting...")

# [PASTE THE ENTIRE CONTENTS OF functions_python/grid_detection.py HERE]
# Open functions_python/grid_detection.py and copy ALL of it (Ctrl+A, Ctrl+C)
# Then paste it here, replacing this comment

print("\n" + "=" * 70)
print("STEP 1: grid_detection.py loaded successfully!")
print("File: functions_python/grid_detection.py")
print("Status: ✓ SUCCESS")
print("Class: GridDetector is now available")
print("=" * 70)
```

**Instructions:**
1. Copy the print statements above
2. Open `functions_python/grid_detection.py` in your editor
3. Select ALL (Ctrl+A) and copy (Ctrl+C)
4. Paste it between the print statements
5. Copy the entire cell (all the code together)
6. Paste into Kaggle notebook Cell 1
7. Run the cell (Shift+Enter)

**Expected Output:**
```
======================================================================
STEP 1: Loading grid_detection.py
======================================================================
File: functions_python/grid_detection.py
Status: Starting...

[... class definition ...]

======================================================================
STEP 1: grid_detection.py loaded successfully!
File: functions_python/grid_detection.py
Status: ✓ SUCCESS
Class: GridDetector is now available
======================================================================
```

---

## STEP 2: Cell 2 - segmented_processing.py

**Copy everything below this line into Cell 2:**

```python
print("=" * 70)
print("STEP 2: Loading segmented_processing.py")
print("=" * 70)
print("File: functions_python/segmented_processing.py")
print("Status: Starting...")

# [PASTE THE ENTIRE CONTENTS OF functions_python/segmented_processing.py HERE]
# Open functions_python/segmented_processing.py and copy ALL of it (Ctrl+A, Ctrl+C)
# Then paste it here, replacing this comment

print("\n" + "=" * 70)
print("STEP 2: segmented_processing.py loaded successfully!")
print("File: functions_python/segmented_processing.py")
print("Status: ✓ SUCCESS")
print("Class: SegmentedProcessor is now available")
print("=" * 70)
```

**Instructions:**
1. Copy the print statements above
2. Open `functions_python/segmented_processing.py` in your editor
3. Select ALL (Ctrl+A) and copy (Ctrl+C)
4. Paste it between the print statements
5. Copy the entire cell (all the code together)
6. Paste into Kaggle notebook Cell 2 (below Cell 1)
7. Run the cell (Shift+Enter)

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

## STEP 3: Cell 3 - line_visualization.py

**Copy everything below this line into Cell 3:**

```python
print("=" * 70)
print("STEP 3: Loading line_visualization.py")
print("=" * 70)
print("File: functions_python/line_visualization.py")
print("Status: Starting...")

# [PASTE THE ENTIRE CONTENTS OF functions_python/line_visualization.py HERE]
# Open functions_python/line_visualization.py and copy ALL of it (Ctrl+A, Ctrl+C)
# Then paste it here, replacing this comment

print("\n" + "=" * 70)
print("STEP 3: line_visualization.py loaded successfully!")
print("File: functions_python/line_visualization.py")
print("Status: ✓ SUCCESS")
print("Class: LineVisualizer is now available")
print("=" * 70)
```

**Instructions:**
1. Copy the print statements above
2. Open `functions_python/line_visualization.py` in your editor
3. Select ALL (Ctrl+A) and copy (Ctrl+C)
4. Paste it between the print statements
5. Copy the entire cell (all the code together)
6. Paste into Kaggle notebook Cell 3 (below Cell 2)
7. Run the cell (Shift+Enter)

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

## STEP 4: Cell 4 - digitization_pipeline.py (FIXED VERSION)

**⚠️ IMPORTANT: This is the fixed version that handles imports correctly!**

**Copy everything below this line into Cell 4:**

```python
"""
ECG Image Digitization Pipeline
Core processing modules for converting ECG images to time-series data

This can be deployed as:
1. Python Cloud Function (using functions-framework)
2. Docker container on Cloud Run
3. Local processing with Firebase Admin SDK
"""

print("=" * 70)
print("STEP 4: Loading digitization_pipeline.py")
print("=" * 70)
print("File: functions_python/digitization_pipeline.py")
print("Status: Starting...")

import numpy as np
import cv2
from scipy import signal
from scipy.ndimage import gaussian_filter1d
from typing import Dict, List, Tuple, Optional
import json

# Import classes from previous cells (they're in global namespace, not modules)
# Try to get from global namespace first (from previous cells)
# Then fall back to module import (if files were uploaded)

print("\n[Step 4.1] Loading GridDetector...")
try:
    # First try: Get from global namespace (Cell 1)
    if 'GridDetector' in globals():
        GridDetector = globals()['GridDetector']
        print("  ✓ Success: Loaded GridDetector from Cell 1 (grid_detection.py)")
    else:
        # Second try: Import as module (if file was uploaded)
        from grid_detection import GridDetector
        print("  ✓ Success: Imported GridDetector from grid_detection module")
except Exception as e:
    print(f"  ✗ ERROR: Could not load GridDetector: {e}")
    print("  → Make sure Cell 1 (grid_detection.py) ran successfully!")
    print("  → Check that you see 'STEP 1: ... SUCCESS' message from Cell 1")
    raise

print("\n[Step 4.2] Loading SegmentedProcessor...")
try:
    if 'SegmentedProcessor' in globals():
        SegmentedProcessor = globals()['SegmentedProcessor']
        print("  ✓ Success: Loaded SegmentedProcessor from Cell 2 (segmented_processing.py)")
    else:
        from segmented_processing import SegmentedProcessor
        print("  ✓ Success: Imported SegmentedProcessor from segmented_processing module")
except Exception as e:
    print(f"  ✗ ERROR: Could not load SegmentedProcessor: {e}")
    print("  → Make sure Cell 2 (segmented_processing.py) ran successfully!")
    print("  → Check that you see 'STEP 2: ... SUCCESS' message from Cell 2")
    raise

print("\n[Step 4.3] Loading LineVisualizer...")
try:
    if 'LineVisualizer' in globals():
        LineVisualizer = globals()['LineVisualizer']
        print("  ✓ Success: Loaded LineVisualizer from Cell 3 (line_visualization.py)")
    else:
        from line_visualization import LineVisualizer
        print("  ✓ Success: Imported LineVisualizer from line_visualization module")
except Exception as e:
    print(f"  ✗ ERROR: Could not load LineVisualizer: {e}")
    print("  → Make sure Cell 3 (line_visualization.py) ran successfully!")
    print("  → Check that you see 'STEP 3: ... SUCCESS' message from Cell 3")
    raise

print("\n" + "=" * 70)
print("STEP 4: All dependencies loaded successfully!")
print("File: functions_python/digitization_pipeline.py")
print("Status: Loading ECGDigitizer class...")
print("=" * 70)

# [NOW PASTE THE REST OF digitization_pipeline.py STARTING FROM LINE 22]
# Open functions_python/digitization_pipeline.py
# Find line 22 (where it says "class ECGDigitizer:")
# Copy from line 22 to the END of the file (Ctrl+Shift+End, then Ctrl+C)
# Paste it here, replacing this comment

print("\n" + "=" * 70)
print("STEP 4: digitization_pipeline.py loaded successfully!")
print("File: functions_python/digitization_pipeline.py")
print("Status: ✓ SUCCESS")
print("Class: ECGDigitizer is now available")
print("=" * 70)
```

**Instructions:**
1. Copy all the code above (from the docstring to the final print statement)
2. Open `functions_python/digitization_pipeline.py` in your editor
3. Find line 22 (where `class ECGDigitizer:` starts)
4. Select from line 22 to the END of the file
5. Copy that section (Ctrl+C)
6. In the code above, find the comment `# [NOW PASTE THE REST...]`
7. Replace that comment with the copied code
8. Copy the ENTIRE modified cell (all code together)
9. Paste into Kaggle notebook Cell 4 (below Cell 3)
10. Run the cell (Shift+Enter)

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

**Copy everything below this line into Cell 5:**

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
1. Copy ALL the code above (from the first print statement to the last)
2. Paste into Kaggle notebook Cell 5 (below Cell 4)
3. Run the cell (Shift+Enter)

**Expected Output:**
```
======================================================================
STEP 5: Running submission code
======================================================================
File: kaggle_notebook_complete.py (STEP 2 section)
Status: Starting...

======================================================================
Kaggle ECG Digitization Submission
======================================================================

✓ Found 2 test image(s):
  - 16640_hr.jpg
  - 17459 hr.jpg

[... processing output ...]

======================================================================
✅ READY FOR SUBMISSION!
======================================================================
```

---

## Summary Checklist

- [ ] **Cell 1:** grid_detection.py - Shows "STEP 1: ... SUCCESS"
- [ ] **Cell 2:** segmented_processing.py - Shows "STEP 2: ... SUCCESS"
- [ ] **Cell 3:** line_visualization.py - Shows "STEP 3: ... SUCCESS"
- [ ] **Cell 4:** digitization_pipeline.py - Shows "STEP 4: ... SUCCESS" (with all 3 dependencies loaded)
- [ ] **Cell 5:** Submission code - Shows "✅ READY FOR SUBMISSION!"

## Troubleshooting

**If Cell 4 fails with "ModuleNotFoundError":**
- Make sure Cells 1, 2, and 3 all ran successfully first
- Check that you see "✓ SUCCESS" messages from each previous cell
- The fixed version in STEP 4 should handle this automatically

**If you see import errors:**
- Run cells in order (1, 2, 3, 4, 5)
- Don't skip any cells
- Make sure each cell completes before running the next one

---

<!-- ============================================================================ -->
<!-- FILE IDENTIFICATION -->
<!-- ============================================================================ -->
<!-- This file: kaggle_step_by_step_complete.md -->
<!-- Purpose: Step-by-step copy-paste guide for Kaggle notebook cells -->
<!-- ============================================================================ -->
