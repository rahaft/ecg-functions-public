"""
Kaggle CSV Generator
Generates competition-ready CSV files from extracted ECG signals

Output Format:
- Header: id,value
- Rows: record_{recordId}_{leadName},{value}
- Total: 60,001 rows (1 header + 12 leads × 5000 points)

Lead Order: I, II, III, aVR, aVL, aVF, V1, V2, V3, V4, V5, V6
"""

import csv
import os
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime


# Standard lead names in Kaggle submission order
LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
EXPECTED_POINTS_PER_LEAD = 5000
EXPECTED_TOTAL_ROWS = 12 * EXPECTED_POINTS_PER_LEAD  # 60,000
VALUE_MIN = -5.0  # mV
VALUE_MAX = 5.0   # mV


class KaggleCSVGenerator:
    """
    Robust Kaggle CSV generator with validation and error handling
    
    Features:
    - Validates input data before generation
    - Handles missing or incomplete leads
    - Generates partial output if some data is missing
    - Provides detailed validation reports
    """
    
    def __init__(self, 
                 points_per_lead: int = EXPECTED_POINTS_PER_LEAD,
                 value_min: float = VALUE_MIN,
                 value_max: float = VALUE_MAX,
                 allow_partial: bool = True):
        """
        Initialize the Kaggle CSV generator
        
        Args:
            points_per_lead: Expected number of points per lead (default: 5000)
            value_min: Minimum valid value in mV (default: -5.0)
            value_max: Maximum valid value in mV (default: 5.0)
            allow_partial: Allow generation with missing/incomplete data (default: True)
        """
        self.points_per_lead = points_per_lead
        self.value_min = value_min
        self.value_max = value_max
        self.allow_partial = allow_partial
        self.lead_names = LEAD_NAMES.copy()
    
    def validate_signals(self, signals: Dict[str, List[float]]) -> Dict:
        """
        Validate input signals before CSV generation
        
        Args:
            signals: Dictionary mapping lead names to signal arrays
            
        Returns:
            Validation report with pass/fail status and details
        """
        report = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'lead_status': {},
            'total_leads': 0,
            'total_points': 0,
            'missing_leads': [],
            'incomplete_leads': [],
            'out_of_range_leads': []
        }
        
        # Check for missing leads
        for lead_name in self.lead_names:
            if lead_name not in signals:
                report['missing_leads'].append(lead_name)
                report['lead_status'][lead_name] = {
                    'status': 'missing',
                    'points': 0,
                    'valid': False
                }
            else:
                signal = signals[lead_name]
                lead_status = self._validate_lead(lead_name, signal)
                report['lead_status'][lead_name] = lead_status
                
                if lead_status['valid']:
                    report['total_leads'] += 1
                    report['total_points'] += lead_status['points']
                else:
                    if lead_status['status'] == 'incomplete':
                        report['incomplete_leads'].append(lead_name)
                    elif lead_status['status'] == 'out_of_range':
                        report['out_of_range_leads'].append(lead_name)
        
        # Generate errors and warnings
        if report['missing_leads']:
            msg = f"Missing leads: {', '.join(report['missing_leads'])}"
            if not self.allow_partial:
                report['errors'].append(msg)
                report['valid'] = False
            else:
                report['warnings'].append(msg)
        
        if report['incomplete_leads']:
            msg = f"Incomplete leads (< {self.points_per_lead} points): {', '.join(report['incomplete_leads'])}"
            report['warnings'].append(msg)
        
        if report['out_of_range_leads']:
            msg = f"Leads with out-of-range values: {', '.join(report['out_of_range_leads'])}"
            report['warnings'].append(msg)
        
        # Check if we have any valid data
        if report['total_leads'] == 0:
            report['errors'].append("No valid lead data found")
            report['valid'] = False
        
        return report
    
    def _validate_lead(self, lead_name: str, signal: Union[List[float], np.ndarray]) -> Dict:
        """
        Validate a single lead's signal data
        
        Args:
            lead_name: Name of the lead
            signal: Signal data array
            
        Returns:
            Lead validation status dictionary
        """
        status = {
            'lead': lead_name,
            'status': 'valid',
            'valid': True,
            'points': 0,
            'min_value': None,
            'max_value': None,
            'has_nan': False,
            'out_of_range_count': 0
        }
        
        # Convert to numpy array if needed
        if isinstance(signal, list):
            signal = np.array(signal)
        
        # Check for empty signal
        if signal is None or len(signal) == 0:
            status['status'] = 'empty'
            status['valid'] = False
            return status
        
        status['points'] = len(signal)
        
        # Check point count
        if status['points'] < self.points_per_lead:
            status['status'] = 'incomplete'
            # Still valid for partial output
        
        # Check for NaN values
        nan_count = np.isnan(signal).sum()
        if nan_count > 0:
            status['has_nan'] = True
            status['status'] = 'has_nan'
            # Replace NaN with 0 for calculation
            signal = np.nan_to_num(signal, nan=0.0)
        
        # Check value range
        status['min_value'] = float(np.min(signal))
        status['max_value'] = float(np.max(signal))
        
        out_of_range = (signal < self.value_min) | (signal > self.value_max)
        status['out_of_range_count'] = int(np.sum(out_of_range))
        
        if status['out_of_range_count'] > 0:
            status['status'] = 'out_of_range'
        
        return status
    
    def generate(self, 
                 record_id: str, 
                 signals: Dict[str, List[float]], 
                 output_path: str,
                 validate: bool = True) -> Dict:
        """
        Generate Kaggle CSV file from signals
        
        Args:
            record_id: ECG record identifier
            signals: Dictionary mapping lead names to signal arrays
            output_path: Path to save the CSV file
            validate: Whether to validate signals before generation (default: True)
            
        Returns:
            Generation report with success status and details
        """
        report = {
            'success': False,
            'output_path': output_path,
            'record_id': record_id,
            'rows_written': 0,
            'leads_written': 0,
            'validation': None,
            'errors': [],
            'warnings': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Validate signals if requested
            if validate:
                validation = self.validate_signals(signals)
                report['validation'] = validation
                
                if not validation['valid'] and not self.allow_partial:
                    report['errors'] = validation['errors']
                    return report
                
                report['warnings'].extend(validation['warnings'])
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate CSV
            rows_written = 0
            leads_written = 0
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['id', 'value'])
                
                # Write data for each lead in order
                for lead_name in self.lead_names:
                    if lead_name not in signals:
                        if self.allow_partial:
                            # Write zeros for missing lead
                            for i in range(self.points_per_lead):
                                row_id = f"record_{record_id}_{lead_name}"
                                writer.writerow([row_id, 0.0])
                                rows_written += 1
                            report['warnings'].append(f"Lead {lead_name} missing - filled with zeros")
                        continue
                    
                    signal = signals[lead_name]
                    
                    # Convert to numpy array and handle NaN
                    if isinstance(signal, list):
                        signal = np.array(signal)
                    signal = np.nan_to_num(signal, nan=0.0)
                    
                    # Clip values to valid range
                    signal = np.clip(signal, self.value_min, self.value_max)
                    
                    # Pad or truncate to expected length
                    if len(signal) < self.points_per_lead:
                        # Pad with zeros
                        padded = np.zeros(self.points_per_lead)
                        padded[:len(signal)] = signal
                        signal = padded
                        report['warnings'].append(
                            f"Lead {lead_name} padded from {len(signals[lead_name])} to {self.points_per_lead} points"
                        )
                    elif len(signal) > self.points_per_lead:
                        # Truncate
                        signal = signal[:self.points_per_lead]
                        report['warnings'].append(
                            f"Lead {lead_name} truncated from {len(signals[lead_name])} to {self.points_per_lead} points"
                        )
                    
                    # Write lead data
                    for i, value in enumerate(signal):
                        row_id = f"record_{record_id}_{lead_name}"
                        writer.writerow([row_id, f"{float(value):.6f}"])
                        rows_written += 1
                    
                    leads_written += 1
            
            report['success'] = True
            report['rows_written'] = rows_written
            report['leads_written'] = leads_written
            
            # Validate output file
            if validate:
                output_validation = validate_kaggle_csv(output_path)
                if not output_validation['valid']:
                    report['warnings'].append("Output validation warning: " + str(output_validation['errors']))
            
        except Exception as e:
            report['errors'].append(f"Generation failed: {str(e)}")
            report['success'] = False
        
        return report
    
    def generate_from_array(self,
                           record_id: str,
                           signal_array: np.ndarray,
                           output_path: str) -> Dict:
        """
        Generate Kaggle CSV from a 2D numpy array
        
        Args:
            record_id: ECG record identifier
            signal_array: 2D array of shape (12, 5000) - leads × points
            output_path: Path to save the CSV file
            
        Returns:
            Generation report
        """
        if signal_array.shape[0] != 12:
            return {
                'success': False,
                'errors': [f"Expected 12 leads, got {signal_array.shape[0]}"]
            }
        
        signals = {}
        for i, lead_name in enumerate(self.lead_names):
            signals[lead_name] = signal_array[i].tolist()
        
        return self.generate(record_id, signals, output_path)


def generate_kaggle_csv(record_id: str, 
                       signals: Dict[str, List[float]], 
                       output_path: str,
                       allow_partial: bool = True) -> Dict:
    """
    Convenience function to generate Kaggle CSV
    
    Args:
        record_id: ECG record identifier
        signals: Dictionary mapping lead names to signal arrays
        output_path: Path to save the CSV file
        allow_partial: Allow generation with incomplete data
        
    Returns:
        Generation report dictionary
    """
    generator = KaggleCSVGenerator(allow_partial=allow_partial)
    return generator.generate(record_id, signals, output_path)


def validate_kaggle_csv(csv_path: str) -> Dict:
    """
    Validate an existing Kaggle CSV file
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        Validation report dictionary
    """
    report = {
        'valid': True,
        'path': csv_path,
        'errors': [],
        'warnings': [],
        'row_count': 0,
        'unique_leads': set(),
        'value_range': {'min': None, 'max': None}
    }
    
    try:
        if not os.path.exists(csv_path):
            report['valid'] = False
            report['errors'].append(f"File not found: {csv_path}")
            return report
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Check header
            header = next(reader, None)
            if header != ['id', 'value']:
                report['errors'].append(f"Invalid header: expected ['id', 'value'], got {header}")
                report['valid'] = False
            
            # Read and validate rows
            values = []
            for row in reader:
                report['row_count'] += 1
                
                if len(row) != 2:
                    report['errors'].append(f"Invalid row {report['row_count']}: expected 2 columns")
                    continue
                
                row_id, value = row
                
                # Extract lead name from ID
                # Format: record_{recordId}_{leadName}
                parts = row_id.split('_')
                if len(parts) >= 3:
                    lead_name = parts[-1]
                    report['unique_leads'].add(lead_name)
                
                # Validate value
                try:
                    val = float(value)
                    values.append(val)
                except ValueError:
                    report['errors'].append(f"Invalid value at row {report['row_count']}: {value}")
            
            # Check row count
            if report['row_count'] != EXPECTED_TOTAL_ROWS:
                report['warnings'].append(
                    f"Row count mismatch: expected {EXPECTED_TOTAL_ROWS}, got {report['row_count']}"
                )
            
            # Check leads
            expected_leads = set(LEAD_NAMES)
            if report['unique_leads'] != expected_leads:
                missing = expected_leads - report['unique_leads']
                extra = report['unique_leads'] - expected_leads
                if missing:
                    report['warnings'].append(f"Missing leads: {missing}")
                if extra:
                    report['warnings'].append(f"Extra leads: {extra}")
            
            # Value statistics
            if values:
                report['value_range']['min'] = min(values)
                report['value_range']['max'] = max(values)
                
                if report['value_range']['min'] < VALUE_MIN or report['value_range']['max'] > VALUE_MAX:
                    report['warnings'].append(
                        f"Values out of expected range [{VALUE_MIN}, {VALUE_MAX}]: "
                        f"[{report['value_range']['min']:.3f}, {report['value_range']['max']:.3f}]"
                    )
        
        # Convert set to list for JSON serialization
        report['unique_leads'] = list(report['unique_leads'])
        
    except Exception as e:
        report['valid'] = False
        report['errors'].append(f"Validation failed: {str(e)}")
    
    return report


# Test function
def test_generator():
    """Test the Kaggle CSV generator with sample data"""
    import tempfile
    
    # Create sample data
    np.random.seed(42)
    signals = {}
    for lead in LEAD_NAMES:
        # Generate realistic-looking ECG signal
        t = np.linspace(0, 10, 5000)
        signal = 0.5 * np.sin(2 * np.pi * 1.2 * t)  # Base heartbeat
        signal += 0.1 * np.random.randn(5000)  # Noise
        signals[lead] = signal.tolist()
    
    # Generate CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        output_path = f.name
    
    generator = KaggleCSVGenerator()
    result = generator.generate('test_001', signals, output_path)
    
    print("Generation Result:")
    print(f"  Success: {result['success']}")
    print(f"  Rows Written: {result['rows_written']}")
    print(f"  Leads Written: {result['leads_written']}")
    print(f"  Warnings: {result['warnings']}")
    print(f"  Errors: {result['errors']}")
    
    # Validate
    validation = validate_kaggle_csv(output_path)
    print("\nValidation Result:")
    print(f"  Valid: {validation['valid']}")
    print(f"  Row Count: {validation['row_count']}")
    print(f"  Leads Found: {validation['unique_leads']}")
    print(f"  Value Range: {validation['value_range']}")
    
    # Cleanup
    os.remove(output_path)
    
    return result['success'] and validation['valid']


if __name__ == '__main__':
    success = test_generator()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
