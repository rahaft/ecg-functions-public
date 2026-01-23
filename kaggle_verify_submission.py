"""
Kaggle Submission Verification Cell

Add this as a final cell in your Kaggle notebook to verify submission.csv exists.
This helps diagnose why Kaggle says the file is missing.
"""

from pathlib import Path
import os

print("=" * 70)
print("Verifying submission.csv")
print("=" * 70)

submission_path = Path('/kaggle/working/submission.csv')

# Check if file exists
if submission_path.exists():
    size_bytes = submission_path.stat().st_size
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024
    
    print(f"✅ submission.csv FOUND!")
    print(f"   Path: {submission_path}")
    print(f"   Size: {size_mb:.2f} MB ({size_kb:.2f} KB, {size_bytes:,} bytes)")
    
    # Count lines
    try:
        with open(submission_path, 'r', encoding='utf-8') as f:
            lines = sum(1 for _ in f)
        print(f"   Lines: {lines:,}")
        
        # Check header
        with open(submission_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        print(f"   Header: {first_line}")
        
        if first_line == 'id,value':
            print(f"   ✅ Header format: CORRECT")
        else:
            print(f"   ⚠️  Header format: UNEXPECTED (expected 'id,value')")
        
        # Check if file is empty
        if size_bytes == 0:
            print(f"   ⚠️  WARNING: File is EMPTY!")
        elif lines < 2:
            print(f"   ⚠️  WARNING: File has only {lines} line(s) (expected > 1)")
        else:
            print(f"   ✅ File appears valid")
            
    except Exception as e:
        print(f"   ⚠️  Error reading file: {e}")
    
    print(f"\n✅ READY FOR SUBMISSION!")
    print(f"   Your notebook should work when you click 'Submit'")
    
else:
    print(f"❌ submission.csv NOT FOUND!")
    print(f"   Expected location: {submission_path}")
    print(f"\n   Possible reasons:")
    print(f"   1. Cell 5 (submission code) didn't run")
    print(f"   2. Cell 5 had an error before creating the file")
    print(f"   3. No test images were found")
    print(f"   4. File was created in wrong location")
    
    # Check for files in working directory
    print(f"\n   Checking /kaggle/working/ for CSV files...")
    working_dir = Path('/kaggle/working')
    csv_files = list(working_dir.glob('*.csv'))
    if csv_files:
        print(f"   Found {len(csv_files)} CSV file(s):")
        for csv_file in csv_files:
            size = csv_file.stat().st_size
            print(f"     - {csv_file.name} ({size / 1024:.2f} KB)")
    else:
        print(f"   No CSV files found in /kaggle/working/")
    
    print(f"\n   ❌ CANNOT SUBMIT - Fix the issue above first")

print("=" * 70)

# ============================================================================
# FILE IDENTIFICATION
# ============================================================================
# This file: kaggle_verify_submission.py
# Purpose: Verification cell to check if submission.csv exists in Kaggle notebook
# Usage: Add as final cell in Kaggle notebook to verify submission file
# ============================================================================
