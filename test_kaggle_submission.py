"""
Test script to generate Kaggle submission CSV for testing

This script creates a sample submission file in the correct format:
- Format: id,value
- ID format: '{record}_{sample}_{lead}' (e.g., '62_0_I')
- 12 leads × 5000 samples = 60,000 rows per record
- Values in millivolts (mV)
"""

import csv
import numpy as np
from pathlib import Path

# Standard 12-lead ECG leads
LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SAMPLES_PER_LEAD = 5000  # 10 seconds at 500 Hz sampling rate


def generate_test_submission(record_id: str, output_path: str = 'submission.csv'):
    """
    Generate a test Kaggle submission CSV file
    
    Args:
        record_id: ECG record identifier (e.g., '62')
        output_path: Path to save the CSV file
    """
    print(f"Generating submission for record {record_id}...")
    
    # Generate sample ECG signals (sine waves with noise for testing)
    np.random.seed(42)
    signals = {}
    
    for lead in LEAD_NAMES:
        # Create a simple test signal (sine wave + noise)
        t = np.linspace(0, 10, SAMPLES_PER_LEAD)  # 10 seconds
        # Different frequency for each lead to make them distinguishable
        freq = 1.0 + np.random.uniform(-0.2, 0.2)
        signal = 0.5 * np.sin(2 * np.pi * freq * t)
        signal += 0.1 * np.random.randn(SAMPLES_PER_LEAD)  # Add noise
        signals[lead] = signal
    
    # Write CSV file
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['id', 'value'])
        
        # Write data: for each lead, for each sample
        rows_written = 0
        for lead_name in LEAD_NAMES:
            signal = signals[lead_name]
            
            for sample_idx in range(SAMPLES_PER_LEAD):
                # ID format: '{record}_{sample}_{lead}'
                row_id = f"'{record_id}_{sample_idx}_{lead_name}'"
                value = float(signal[sample_idx])
                
                writer.writerow([row_id, f"{value:.6f}"])
                rows_written += 1
    
    print(f"[OK] Submission file created: {output_path}")
    print(f"[OK] Total rows written: {rows_written}")
    print(f"[OK] Expected rows: {len(LEAD_NAMES) * SAMPLES_PER_LEAD}")
    print(f"[OK] File size: {Path(output_path).stat().st_size / 1024:.2f} KB")
    
    return output_path


def generate_from_signals(record_id: str, signals: dict, output_path: str = 'submission.csv'):
    """
    Generate submission CSV from actual signal data
    
    Args:
        record_id: ECG record identifier
        signals: Dictionary mapping lead names to signal arrays
                 Example: {'I': [0.1, 0.2, ...], 'II': [...], ...}
        output_path: Path to save the CSV file
    """
    print(f"Generating submission from signals for record {record_id}...")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'value'])
        
        rows_written = 0
        for lead_name in LEAD_NAMES:
            if lead_name not in signals:
                print(f"[WARNING] Lead {lead_name} not found, filling with zeros")
                signal = np.zeros(SAMPLES_PER_LEAD)
            else:
                signal = np.array(signals[lead_name])
                
                # Pad or truncate to expected length
                if len(signal) < SAMPLES_PER_LEAD:
                    padded = np.zeros(SAMPLES_PER_LEAD)
                    padded[:len(signal)] = signal
                    signal = padded
                elif len(signal) > SAMPLES_PER_LEAD:
                    signal = signal[:SAMPLES_PER_LEAD]
            
            for sample_idx in range(SAMPLES_PER_LEAD):
                row_id = f"'{record_id}_{sample_idx}_{lead_name}'"
                value = float(signal[sample_idx])
                writer.writerow([row_id, f"{value:.6f}"])
                rows_written += 1
    
    print(f"[OK] Submission file created: {output_path}")
    print(f"[OK] Total rows written: {rows_written}")
    return output_path


def validate_submission(csv_path: str):
    """
    Validate a submission CSV file
    
    Args:
        csv_path: Path to the CSV file
    """
    print(f"\nValidating {csv_path}...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Check header
        header = next(reader)
        if header != ['id', 'value']:
            print(f"[ERROR] Invalid header: {header}")
            return False
        print("[OK] Header is correct")
        
        # Count rows and check format
        row_count = 0
        unique_leads = set()
        value_min = float('inf')
        value_max = float('-inf')
        
        for row in reader:
            if len(row) != 2:
                print(f"[ERROR] Invalid row {row_count + 1}: {row}")
                return False
            
            row_id, value = row
            
            # Check ID format: '{record}_{sample}_{lead}'
            if not (row_id.startswith("'") and row_id.endswith("'")):
                print(f"[WARNING] ID not quoted: {row_id}")
            
            # Extract lead name
            parts = row_id.strip("'").split('_')
            if len(parts) >= 3:
                lead_name = parts[-1]
                unique_leads.add(lead_name)
            
            # Check value
            try:
                val = float(value)
                value_min = min(value_min, val)
                value_max = max(value_max, val)
            except ValueError:
                print(f"[ERROR] Invalid value at row {row_count + 1}: {value}")
                return False
            
            row_count += 1
        
        print(f"[OK] Total rows: {row_count}")
        print(f"[OK] Expected rows: {len(LEAD_NAMES) * SAMPLES_PER_LEAD}")
        print(f"[OK] Unique leads found: {sorted(unique_leads)}")
        print(f"[OK] Value range: [{value_min:.6f}, {value_max:.6f}]")
        
        if row_count != len(LEAD_NAMES) * SAMPLES_PER_LEAD:
            print(f"[WARNING] Row count mismatch!")
            return False
        
        if set(unique_leads) != set(LEAD_NAMES):
            missing = set(LEAD_NAMES) - unique_leads
            print(f"[WARNING] Missing leads: {missing}")
            return False
        
        print("[OK] Validation passed!")
        return True


if __name__ == '__main__':
    # Example 1: Generate test submission with synthetic data
    print("=" * 60)
    print("Example 1: Generate test submission")
    print("=" * 60)
    generate_test_submission('62', 'submission.csv')
    validate_submission('submission.csv')
    
    # Example 2: Generate from actual signals (if you have them)
    print("\n" + "=" * 60)
    print("Example 2: Generate from actual signals")
    print("=" * 60)
    print("To use this, provide your signal data:")
    print("""
    signals = {
        'I': [0.1, 0.2, 0.3, ...],  # 5000 values
        'II': [0.15, 0.25, 0.35, ...],
        # ... all 12 leads
    }
    generate_from_signals('62', signals, 'submission.csv')
    """)
    
    print("\n" + "=" * 60)
    print("Submission file ready for Kaggle!")
    print("=" * 60)
    print("\nTo submit to Kaggle:")
    print("1. Upload this file to your Kaggle notebook")
    print("2. Make sure it's named 'submission.csv' or 'submission.parquet'")
    print("3. The notebook should output this file to /kaggle/working/")
    print("4. Commit the notebook to enable the Submit button")
