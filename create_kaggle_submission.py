"""
Create Kaggle Submission from Test Images

This script processes the two test images and creates submission.csv
Works locally or in Kaggle notebook.

Usage:
    python create_kaggle_submission.py [--test-dir PATH] [--output submission.csv]
"""

import os
import sys
import csv
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, List

# Add functions_python to path
sys.path.insert(0, str(Path(__file__).parent / 'functions_python'))

try:
    from digitization_pipeline import ECGDigitizer
    PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"Error: Could not import digitization_pipeline: {e}")
    print("Make sure functions_python/digitization_pipeline.py exists")
    PIPELINE_AVAILABLE = False

# Standard 12-lead ECG leads
LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SAMPLES_PER_LEAD = 5000  # 10 seconds at 500 Hz


def extract_record_id(image_path: Path) -> str:
    """
    Extract record ID from image filename
    
    Handles formats like:
    - "16640_hr.jpg" -> "16640"
    - "17459 hr.jpg" -> "17459"
    - "62.jpg" -> "62"
    
    Args:
        image_path: Path to image file
        
    Returns:
        Record ID string (numeric part only)
    """
    filename = image_path.stem  # Get filename without extension
    
    # Extract first sequence of digits (the record number)
    import re
    match = re.search(r'(\d+)', filename)
    if match:
        return match.group(1)
    else:
        # Fallback: use filename as-is (remove spaces, underscores)
        return filename.replace(' ', '_').replace('-', '_')


def find_test_images(test_dir: Path) -> List[Path]:
    """
    Find all test images in directory
    
    Args:
        test_dir: Directory containing test images
        
    Returns:
        List of image file paths
    """
    images = []
    
    if not test_dir.exists():
        print(f"Warning: Test directory not found: {test_dir}")
        return images
    
    # Find all image files
    for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.JPG', '.JPEG', '.PNG', '.TIF', '.TIFF']:
        images.extend(test_dir.glob(f'*{ext}'))
    
    return sorted(images)


def process_image(image_path: Path) -> Dict:
    """
    Process a single ECG image and extract signals
    
    Args:
        image_path: Path to ECG image
        
    Returns:
        Dictionary with record_id and signals
    """
    record_id = extract_record_id(image_path)
    
    print(f"\nProcessing: {image_path.name}")
    print(f"  Record ID: {record_id}")
    
    if not PIPELINE_AVAILABLE:
        print("  ERROR: Pipeline not available!")
        return {
            'record_id': record_id,
            'signals': {lead: np.zeros(SAMPLES_PER_LEAD) for lead in LEAD_NAMES},
            'success': False,
            'error': 'Pipeline not available'
        }
    
    try:
        # Initialize digitizer
        digitizer = ECGDigitizer(
            use_segmented_processing=True,
            enable_visualization=False
        )
        
        # Process image
        print("  Running digitization pipeline...")
        result = digitizer.process_image(str(image_path))
        
        # Extract signals
        signals = {}
        leads_found = 0
        
        for lead_data in result.get('leads', []):
            lead_name = lead_data['name']
            if lead_name not in LEAD_NAMES:
                continue
                
            signal_values = np.array(lead_data['values'])
            leads_found += 1
            
            # Ensure correct length (pad or truncate to 5000)
            if len(signal_values) < SAMPLES_PER_LEAD:
                padded = np.zeros(SAMPLES_PER_LEAD)
                padded[:len(signal_values)] = signal_values
                signals[lead_name] = padded
                print(f"  Lead {lead_name}: {len(signal_values)} samples (padded to {SAMPLES_PER_LEAD})")
            elif len(signal_values) > SAMPLES_PER_LEAD:
                signals[lead_name] = signal_values[:SAMPLES_PER_LEAD]
                print(f"  Lead {lead_name}: {len(signal_values)} samples (truncated to {SAMPLES_PER_LEAD})")
            else:
                signals[lead_name] = signal_values
                print(f"  Lead {lead_name}: {len(signal_values)} samples")
        
        # Fill missing leads with zeros
        for lead_name in LEAD_NAMES:
            if lead_name not in signals:
                signals[lead_name] = np.zeros(SAMPLES_PER_LEAD)
        
        print(f"  Successfully extracted {leads_found} leads")
        
        return {
            'record_id': record_id,
            'signals': signals,
            'success': True,
            'leads_found': leads_found
        }
        
    except Exception as e:
        print(f"  ERROR processing image: {e}")
        import traceback
        traceback.print_exc()
        
        # Return zeros for failed image
        signals = {lead: np.zeros(SAMPLES_PER_LEAD) for lead in LEAD_NAMES}
        return {
            'record_id': record_id,
            'signals': signals,
            'success': False,
            'error': str(e)
        }


def generate_submission_csv(results: List[Dict], output_path: Path) -> Path:
    """
    Generate Kaggle submission CSV file
    
    Args:
        results: List of processing results (each with record_id and signals)
        output_path: Path to save submission file
        
    Returns:
        Path to generated submission file
    """
    print(f"\n{'=' * 70}")
    print(f"Generating submission file...")
    print(f"{'=' * 70}")
    print(f"Output: {output_path}")
    
    rows_written = 0
    total_expected = len(results) * len(LEAD_NAMES) * SAMPLES_PER_LEAD
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['id', 'value'])
        
        # Write data for each record
        for result_idx, result in enumerate(results, 1):
            record_id = result['record_id']
            signals = result['signals']
            
            print(f"  Writing record {record_id} ({result_idx}/{len(results)})...", end="")
            
            record_rows = 0
            for lead_name in LEAD_NAMES:
                signal = signals[lead_name]
                
                for sample_idx in range(SAMPLES_PER_LEAD):
                    # ID format: '{record}_{sample}_{lead}'
                    row_id = f"'{record_id}_{sample_idx}_{lead_name}'"
                    value = float(signal[sample_idx])
                    
                    writer.writerow([row_id, f"{value:.6f}"])
                    rows_written += 1
                    record_rows += 1
            
            print(f" {record_rows:,} rows")
    
    file_size_kb = output_path.stat().st_size / 1024
    file_size_mb = file_size_kb / 1024
    
    print(f"\n  ✓ Total rows written: {rows_written:,}")
    print(f"  ✓ Expected rows: {total_expected:,}")
    print(f"  ✓ File size: {file_size_mb:.2f} MB ({file_size_kb:.2f} KB)")
    
    if rows_written != total_expected:
        print(f"  ⚠ WARNING: Row count mismatch!")
    else:
        print(f"  ✓ Row count: CORRECT")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Create Kaggle submission from test images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process images in ./test_images/ directory
  python create_kaggle_submission.py --test-dir ./test_images
  
  # Process images in Kaggle test directory
  python create_kaggle_submission.py --test-dir /kaggle/input/physionet-ecg-image-digitization/test
  
  # Custom output file
  python create_kaggle_submission.py --test-dir ./test_images --output my_submission.csv
        """
    )
    parser.add_argument('--test-dir', type=str, 
                       default='./test_images',
                       help='Directory containing test images (default: ./test_images)')
    parser.add_argument('--output', type=str, 
                       default='submission.csv',
                       help='Output submission file (default: submission.csv)')
    args = parser.parse_args()
    
    print("=" * 70)
    print("Kaggle ECG Digitization Submission Generator")
    print("=" * 70)
    
    if not PIPELINE_AVAILABLE:
        print("\nERROR: Digitization pipeline not available!")
        print("Make sure functions_python/digitization_pipeline.py exists and is importable.")
        return 1
    
    # Find test images
    test_dir = Path(args.test_dir)
    print(f"\n1. Looking for test images in: {test_dir}")
    
    test_images = find_test_images(test_dir)
    
    if not test_images:
        print(f"\nERROR: No test images found in {test_dir}")
        print("\nPlease provide test images in one of these locations:")
        print("  - ./test_images/")
        print("  - /kaggle/input/physionet-ecg-image-digitization/test/")
        print("  - Or specify with --test-dir PATH")
        return 1
    
    print(f"Found {len(test_images)} test image(s):")
    for img in test_images:
        print(f"  - {img.name}")
    
    # Process all images
    print(f"\n{'=' * 70}")
    print(f"2. Processing {len(test_images)} image(s)...")
    print(f"{'=' * 70}")
    results = []
    for i, image_path in enumerate(test_images, 1):
        print(f"\n[{i}/{len(test_images)}] ", end="")
        result = process_image(image_path)
        results.append(result)
    
    # Check for errors
    successful = sum(1 for r in results if r.get('success', False))
    print(f"\n{'=' * 70}")
    print(f"Processing Complete: {successful}/{len(results)} images successful")
    print(f"{'=' * 70}")
    
    if successful == 0:
        print("\nERROR: No images processed successfully!")
        print("Check the error messages above.")
        return 1
    
    # Generate submission file
    output_path = Path(args.output)
    print(f"\n3. Generating submission file...")
    submission_path = generate_submission_csv(results, output_path)
    
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
    
    # Get row count from file
    with open(submission_path, 'r') as f:
        row_count = sum(1 for line in f) - 1  # Subtract header
    print(f"   Rows: {row_count:,} (Expected: {expected_rows:,})")
    
    if row_count == expected_rows:
        print(f"   ✓ Row count: CORRECT")
    else:
        print(f"   ⚠ Row count: MISMATCH")
    
    print(f"\n📊 Processing Summary:")
    print(f"   Total records: {len(results)}")
    successful = sum(1 for r in results if r.get('success', False))
    print(f"   Successfully processed: {successful}/{len(results)}")
    
    print(f"\n📋 Record Details:")
    for i, result in enumerate(results, 1):
        status = "✓" if result.get('success') else "✗"
        record_id = result['record_id']
        leads = result.get('leads_found', 0)
        print(f"   {i}. {status} Record {record_id}: {leads} leads extracted")
    
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
            print(f"   ✓ First row: {second_line[:60]}...")
    except Exception as e:
        print(f"   ⚠ Could not read file: {e}")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Verify the submission file format")
    print(f"   2. Check file size and row count")
    print(f"   3. Upload to Kaggle or commit notebook")
    print(f"   4. Click 'Submit' button in Kaggle")
    
    print(f"\n" + "=" * 70)
    print("✅ READY FOR SUBMISSION!")
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    exit(main())

# ============================================================================
# FILE IDENTIFICATION
# ============================================================================
# This file: create_kaggle_submission.py
# Purpose: Create Kaggle submission CSV from test images (local or Kaggle)
# Usage: python create_kaggle_submission.py [--test-dir PATH] [--output FILE]
# ============================================================================
