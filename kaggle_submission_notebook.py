"""
Kaggle Submission Notebook - Complete Code
Processes test images and generates submission.csv

This is the code you use in your Kaggle notebook to submit.
It processes all test images and generates the submission file.
"""

import os
import sys
import csv
import numpy as np
from pathlib import Path
from typing import Dict, List

# Add functions_python to path (adjust if needed)
NOTEBOOK_DIR = Path('/kaggle/working')
if str(NOTEBOOK_DIR.parent / 'functions_python') not in sys.path:
    sys.path.insert(0, str(NOTEBOOK_DIR.parent / 'functions_python'))

# Import your digitization pipeline
try:
    from digitization_pipeline import ECGDigitizer
    PIPELINE_AVAILABLE = True
except ImportError:
    # If functions_python is in the notebook, try direct import
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "digitization_pipeline",
            "/kaggle/working/digitization_pipeline.py"
        )
        digitization_pipeline = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(digitization_pipeline)
        ECGDigitizer = digitization_pipeline.ECGDigitizer
        PIPELINE_AVAILABLE = True
    except Exception as e:
        print(f"Warning: Could not import pipeline: {e}")
        PIPELINE_AVAILABLE = False

# Competition configuration
COMPETITION_NAME = "physionet-ecg-image-digitization"
INPUT_DIR = Path('/kaggle/input') / COMPETITION_NAME
TEST_DIR = INPUT_DIR / 'test'
OUTPUT_DIR = Path('/kaggle/working')

# Standard 12-lead ECG leads
LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SAMPLES_PER_LEAD = 5000  # 10 seconds at 500 Hz


def find_test_images() -> List[Path]:
    """
    Find all test images
    
    Returns:
        List of image file paths
    """
    images = []
    
    if not TEST_DIR.exists():
        print(f"Warning: Test directory not found: {TEST_DIR}")
        return images
    
    # Find all image files
    for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.JPG', '.JPEG', '.PNG']:
        images.extend(TEST_DIR.glob(f'*{ext}'))
    
    return sorted(images)


def extract_record_id(image_path: Path) -> str:
    """
    Extract record ID from image filename
    
    Args:
        image_path: Path to image file
        
    Returns:
        Record ID string
    """
    filename = image_path.stem
    
    # Try to extract number from filename (e.g., "62.jpg" -> "62")
    import re
    match = re.search(r'(\d+)', filename)
    if match:
        return match.group(1)
    else:
        # Use filename as record ID
        return filename


def process_image(image_path: Path) -> Dict:
    """
    Process a single ECG image and extract signals
    
    Args:
        image_path: Path to ECG image
        
    Returns:
        Dictionary with record_id and signals
    """
    record_id = extract_record_id(image_path)
    
    print(f"Processing: {image_path.name} (Record ID: {record_id})")
    
    try:
        # Initialize digitizer
        digitizer = ECGDigitizer(
            use_segmented_processing=True,
            enable_visualization=False
        )
        
        # Process image
        result = digitizer.process_image(str(image_path))
        
        # Extract signals
        signals = {}
        for lead_data in result.get('leads', []):
            lead_name = lead_data['name']
            signal_values = np.array(lead_data['values'])
            
            # Ensure correct length (pad or truncate to 5000)
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
                print(f"  Warning: Lead {lead_name} not found, filled with zeros")
        
        print(f"  Successfully extracted {len([s for s in signals.values() if np.any(s != 0)])} leads")
        
        return {
            'record_id': record_id,
            'signals': signals,
            'success': True
        }
        
    except Exception as e:
        print(f"  Error processing {image_path.name}: {e}")
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


def generate_submission_csv(results: List[Dict], output_path: Path = None) -> Path:
    """
    Generate Kaggle submission CSV file
    
    Args:
        results: List of processing results (each with record_id and signals)
        output_path: Path to save submission file (default: /kaggle/working/submission.csv)
        
    Returns:
        Path to generated submission file
    """
    if output_path is None:
        output_path = OUTPUT_DIR / 'submission.csv'
    
    print(f"\nGenerating submission file: {output_path}")
    
    rows_written = 0
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['id', 'value'])
        
        # Write data for each record
        for result in results:
            record_id = result['record_id']
            signals = result['signals']
            
            # Write all leads for this record
            for lead_name in LEAD_NAMES:
                signal = signals[lead_name]
                
                for sample_idx in range(SAMPLES_PER_LEAD):
                    # ID format: '{record}_{sample}_{lead}'
                    row_id = f"'{record_id}_{sample_idx}_{lead_name}'"
                    value = float(signal[sample_idx])
                    
                    writer.writerow([row_id, f"{value:.6f}"])
                    rows_written += 1
    
    print(f"  Total rows written: {rows_written}")
    print(f"  Expected rows: {len(results) * len(LEAD_NAMES) * SAMPLES_PER_LEAD}")
    print(f"  File size: {output_path.stat().st_size / 1024:.2f} KB")
    
    return output_path


def main():
    """
    Main submission function - call this in your Kaggle notebook
    """
    print("=" * 60)
    print("Kaggle ECG Digitization Submission")
    print("=" * 60)
    
    if not PIPELINE_AVAILABLE:
        print("ERROR: Digitization pipeline not available!")
        print("Make sure digitization_pipeline.py is in your notebook.")
        return
    
    # Find test images
    print("\n1. Finding test images...")
    test_images = find_test_images()
    
    if not test_images:
        print("ERROR: No test images found!")
        print(f"Expected location: {TEST_DIR}")
        return
    
    print(f"Found {len(test_images)} test image(s)")
    for img in test_images:
        print(f"  - {img.name}")
    
    # Process all images
    print("\n2. Processing images...")
    results = []
    for image_path in test_images:
        result = process_image(image_path)
        results.append(result)
    
    # Check for errors
    successful = sum(1 for r in results if r.get('success', False))
    print(f"\nSuccessfully processed: {successful}/{len(results)} images")
    
    if successful == 0:
        print("ERROR: No images processed successfully!")
        return
    
    # Generate submission file
    print("\n3. Generating submission file...")
    submission_path = generate_submission_csv(results)
    
    print("\n" + "=" * 60)
    print("Submission Complete!")
    print("=" * 60)
    print(f"Submission file: {submission_path}")
    print(f"Records processed: {len(results)}")
    print("\nNext steps:")
    print("1. Verify the submission file format")
    print("2. Commit this notebook")
    print("3. Click 'Submit' button in Kaggle")
    
    return submission_path


# Run main function when executed
if __name__ == '__main__':
    main()
