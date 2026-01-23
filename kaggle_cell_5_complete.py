"""
STEP 5: Submission Code for Kaggle Notebook

Copy this ENTIRE file into Cell 5 of your Kaggle notebook.
IMPORTANT: Make sure Cells 1-4 have been run successfully first!
"""

print("=" * 70)
print("STEP 5: Loading submission code")
print("=" * 70)
print("File: kaggle_notebook_complete.py")
print("Status: Starting...")

import sys
import csv
import numpy as np
from pathlib import Path

# Import ECGDigitizer from previous cells (it's in global namespace, not a module)
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

# STEP 5: kaggle_cell_5_complete.py

# ============================================================================
# Configuration
# ============================================================================

COMPETITION_NAME = "physionet-ecg-image-digitization"
INPUT_DIR = Path('/kaggle/input') / COMPETITION_NAME
TEST_DIR = INPUT_DIR / 'test'
OUTPUT_DIR = Path('/kaggle/working')

# IMPORTANT: submission.csv MUST be created in /kaggle/working/
# This is the only writable directory in Kaggle notebooks

LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SAMPLES_PER_LEAD = 5000

# ============================================================================
# Helper Functions
# ============================================================================

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

# STEP 5: kaggle_cell_5_complete.py

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
            
            # Ensure signal is 1D (flatten if 2D)
            if signal.ndim > 1:
                # If 2D, take the first row or flatten
                if signal.shape[0] == 1:
                    signal = signal[0]
                elif signal.shape[1] == 1:
                    signal = signal[:, 0]
                else:
                    # Multiple rows - take mean or first row
                    signal = signal[0] if signal.shape[0] < signal.shape[1] else signal[:, 0]
            
            # Ensure it's 1D
            signal = signal.flatten()
            
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

# STEP 5: kaggle_cell_5_complete.py

# ============================================================================
# Main Execution
# ============================================================================

print("\n" + "=" * 70)
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
    print("\n⚠️  WARNING: No submission.csv will be created without test images!")
    print("   The notebook must process at least one test image to generate submission.csv")
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
    
    # STEP 5: kaggle_cell_5_complete.py
    
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
    
    # STEP 5: kaggle_cell_5_complete.py
    
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
    
    # STEP 5: kaggle_cell_5_complete.py
    
    # Final verification that submission.csv exists
    submission_path = OUTPUT_DIR / 'submission.csv'
    print(f"\n" + "=" * 70)
    if submission_path.exists():
        file_size_kb = submission_path.stat().st_size / 1024
        print("✅ READY FOR SUBMISSION!")
        print(f"✅ submission.csv verified at: {submission_path}")
        print(f"✅ File size: {file_size_kb:.2f} KB")
    else:
        print("⚠️  WARNING: submission.csv not found!")
        print(f"   The file should be at: {submission_path}")
    print("=" * 70)
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Verify submission.csv format is correct")
    print(f"   2. Check that all test images were processed")
    print(f"   3. Commit this notebook")
    print(f"   4. Click 'Submit' button in Kaggle")

# ============================================================================
# FILE IDENTIFICATION
# ============================================================================
# This file: kaggle_cell_5_complete.py
# Purpose: Complete Cell 5 code for Kaggle notebook (submission code)
# Usage: Copy entire file into Cell 5 of Kaggle notebook
# ============================================================================
