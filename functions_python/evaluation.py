"""
Evaluation Module
Competition scoring and submission file generation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json


class CompetitionEvaluator:
    """Evaluate digitization results for competition"""
    
    def __init__(self, sampling_rate: int = 500):
        """
        Initialize evaluator
        
        Args:
            sampling_rate: Sampling rate in Hz
        """
        self.sampling_rate = sampling_rate
    
    def calculate_snr(self, predicted: np.ndarray, 
                     ground_truth: Optional[np.ndarray] = None) -> float:
        """
        Calculate Signal-to-Noise Ratio
        
        For competition: SNR of reconstructed signal
        If ground truth available, compare against it.
        Otherwise, estimate from signal characteristics.
        
        Args:
            predicted: Predicted/reconstructed signal
            ground_truth: Optional ground truth signal
            
        Returns:
            SNR in dB
        """
        if ground_truth is not None:
            # Calculate SNR against ground truth
            signal_power = np.mean(ground_truth ** 2)
            noise = predicted - ground_truth
            noise_power = np.mean(noise ** 2)
            
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
            else:
                snr = 60.0  # Perfect match
        else:
            # Estimate SNR from signal characteristics
            signal_power = np.mean(predicted ** 2)
            
            # Estimate noise from high-frequency components
            from scipy import signal as sp_signal
            sos = sp_signal.butter(3, [40, 100], btype='band',
                                  fs=self.sampling_rate, output='sos')
            noise = sp_signal.sosfilt(sos, predicted)
            noise_power = np.mean(noise ** 2)
            
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
            else:
                snr = 60.0
        
        return float(snr)
    
    def evaluate_digitization(self, results: Dict, 
                            ground_truth: Optional[Dict] = None) -> Dict:
        """
        Evaluate digitization results
        
        Args:
            results: Digitization results with leads
            ground_truth: Optional ground truth signals
            
        Returns:
            Evaluation metrics
        """
        leads = results.get('leads', [])
        
        snr_values = []
        lead_evaluations = {}
        
        for lead_data in leads:
            lead_name = lead_data['name']
            predicted = np.array(lead_data['values'])
            
            if ground_truth and lead_name in ground_truth:
                gt_signal = np.array(ground_truth[lead_name])
                # Resample to match if needed
                if len(gt_signal) != len(predicted):
                    from scipy import signal as sp_signal
                    gt_signal = sp_signal.resample(gt_signal, len(predicted))
                
                snr = self.calculate_snr(predicted, gt_signal)
            else:
                snr = self.calculate_snr(predicted)
            
            snr_values.append(snr)
            lead_evaluations[lead_name] = {
                'snr': snr,
                'signal_length': len(predicted)
            }
        
        return {
            'mean_snr': float(np.mean(snr_values)) if snr_values else 0.0,
            'min_snr': float(np.min(snr_values)) if snr_values else 0.0,
            'max_snr': float(np.max(snr_values)) if snr_values else 0.0,
            'lead_evaluations': lead_evaluations
        }
    
    def generate_submission_file(self, results_list: List[Dict],
                                output_path: str,
                                competition_format: str = 'physionet') -> str:
        """
        Generate competition submission file
        
        Args:
            results_list: List of digitization results
            output_path: Path to save submission file
            competition_format: Format type ('physionet' or 'kaggle')
            
        Returns:
            Path to saved submission file
        """
        if competition_format == 'physionet':
            return self._generate_physionet_submission(results_list, output_path)
        elif competition_format == 'kaggle':
            return self._generate_kaggle_submission(results_list, output_path)
        else:
            raise ValueError(f"Unknown competition format: {competition_format}")
    
    def _generate_physionet_submission(self, results_list: List[Dict],
                                      output_path: str) -> str:
        """Generate PhysioNet format submission"""
        # PhysioNet format typically uses WFDB or similar
        # For now, create a CSV with signal data
        submission_data = []
        
        for result in results_list:
            image_id = result.get('image_id', result.get('image_name', 'unknown'))
            leads = result.get('leads', [])
            
            for lead in leads:
                lead_name = lead['name']
                values = lead['values']
                
                # Create time series data
                for i, value in enumerate(values):
                    time_point = i / self.sampling_rate
                    submission_data.append({
                        'image_id': image_id,
                        'lead': lead_name,
                        'time': time_point,
                        'value': value
                    })
        
        df = pd.DataFrame(submission_data)
        df.to_csv(output_path, index=False)
        
        return output_path
    
    def _generate_kaggle_submission(self, results_list: List[Dict],
                                   output_path: str) -> str:
        """Generate Kaggle format submission"""
        # Kaggle format: typically requires specific column structure
        # Adjust based on actual competition requirements
        submission_data = []
        
        for result in results_list:
            image_id = result.get('image_id', result.get('image_name', 'unknown'))
            leads = result.get('leads', [])
            
            # Flatten signal data
            signal_data = {}
            for lead in leads:
                lead_name = lead['name']
                values = lead['values']
                
                # Convert to string representation (adjust format as needed)
                signal_str = ','.join([f"{v:.6f}" for v in values])
                signal_data[f'{lead_name}_signal'] = signal_str
            
            submission_data.append({
                'image_id': image_id,
                **signal_data
            })
        
        df = pd.DataFrame(submission_data)
        df.to_csv(output_path, index=False)
        
        return output_path
    
    def create_evaluation_report(self, evaluations: List[Dict],
                                output_path: str) -> pd.DataFrame:
        """
        Create evaluation report
        
        Args:
            evaluations: List of evaluation results
            output_path: Path to save report
            
        Returns:
            DataFrame with report
        """
        report_data = []
        
        for eval_result in evaluations:
            report_data.append({
                'image_id': eval_result.get('image_id', 'unknown'),
                'mean_snr': eval_result.get('mean_snr', 0.0),
                'min_snr': eval_result.get('min_snr', 0.0),
                'max_snr': eval_result.get('max_snr', 0.0),
                'num_leads': len(eval_result.get('lead_evaluations', {}))
            })
        
        df = pd.DataFrame(report_data)
        df = df.sort_values('mean_snr', ascending=False)
        df.to_csv(output_path, index=False)
        
        return df
