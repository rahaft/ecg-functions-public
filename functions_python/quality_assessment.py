"""
Quality Assessment Module
Calculates SNR and other quality metrics for ECG digitization
"""

import numpy as np
from scipy import signal
from typing import Dict, List, Optional


class QualityAssessor:
    """Assess quality of digitized ECG signals"""
    
    def __init__(self, sampling_rate: int = 500):
        """
        Initialize quality assessor
        
        Args:
            sampling_rate: Sampling rate in Hz
        """
        self.sampling_rate = sampling_rate
    
    def assess_quality(self, processed_signals: List[Dict], 
                      grid_info: Optional[Dict] = None) -> Dict:
        """
        Assess overall quality of digitized ECG
        
        Args:
            processed_signals: List of lead signal dictionaries
            grid_info: Optional grid detection information
            
        Returns:
            Dictionary with quality metrics
        """
        # Calculate SNR for each lead
        snr_results = self.calculate_snr(processed_signals)
        
        # Assess grid quality if available
        grid_quality = None
        if grid_info:
            grid_quality = self.assess_grid_quality(grid_info)
        
        # Assess signal clarity
        signal_clarity = self.assess_signal_clarity(processed_signals)
        
        # Calculate completeness
        completeness = self.calculate_completeness(processed_signals)
        
        # Overall quality score
        overall_score = self._calculate_overall_score(
            snr_results, grid_quality, signal_clarity, completeness
        )
        
        return {
            'snr': snr_results,
            'grid_quality': grid_quality,
            'signal_clarity': signal_clarity,
            'completeness': completeness,
            'overall_score': overall_score
        }
    
    def calculate_snr(self, processed_signals: List[Dict]) -> Dict:
        """
        Calculate Signal-to-Noise Ratio for each lead
        
        Args:
            processed_signals: List of lead signal dictionaries
            
        Returns:
            Dictionary with SNR metrics
        """
        snr_values = []
        lead_snrs = {}
        
        for lead_data in processed_signals:
            sig = np.array(lead_data['values'])
            
            if len(sig) < 10:
                snr = 0.0
            else:
                # Estimate signal power
                signal_power = np.mean(sig ** 2)
                
                # Estimate noise from high-frequency components (40-100 Hz band)
                sos = signal.butter(3, [40, 100], btype='band', 
                                  fs=self.sampling_rate, output='sos')
                noise = signal.sosfilt(sos, sig)
                noise_power = np.mean(noise ** 2)
                
                # Calculate SNR in dB
                if noise_power > 0:
                    snr = 10 * np.log10(signal_power / noise_power)
                else:
                    snr = 60.0  # Very high SNR
                
                # Clamp to reasonable range
                snr = max(0.0, min(60.0, snr))
            
            snr_values.append(snr)
            lead_snrs[lead_data['name']] = float(snr)
        
        return {
            'mean_snr': float(np.mean(snr_values)) if snr_values else 0.0,
            'min_snr': float(np.min(snr_values)) if snr_values else 0.0,
            'max_snr': float(np.max(snr_values)) if snr_values else 0.0,
            'std_snr': float(np.std(snr_values)) if snr_values else 0.0,
            'lead_snrs': lead_snrs
        }
    
    def assess_grid_quality(self, grid_info: Dict) -> Dict:
        """
        Assess quality of detected grid
        
        Args:
            grid_info: Grid detection results
            
        Returns:
            Dictionary with grid quality metrics
        """
        # Check spacing consistency
        h_spacing = grid_info.get('horizontal_spacing', 0)
        v_spacing = grid_info.get('vertical_spacing', 0)
        
        spacing_consistency = 1.0
        if h_spacing > 0 and v_spacing > 0:
            # Check if spacings are similar (within 20%)
            ratio = min(h_spacing, v_spacing) / max(h_spacing, v_spacing)
            spacing_consistency = ratio
        
        # Count detected lines
        num_h_lines = len(grid_info.get('horizontal_lines', []))
        num_v_lines = len(grid_info.get('vertical_lines', []))
        
        # Count intersections
        num_intersections = len(grid_info.get('intersections', []))
        
        # Line clarity score (based on R-squared of fits)
        h_line_quality = []
        for line in grid_info.get('horizontal_lines', []):
            h_line_quality.append(line.get('r_squared', 0.0))
        
        v_line_quality = []
        for line in grid_info.get('vertical_lines', []):
            v_line_quality.append(line.get('r_squared', 0.0))
        
        avg_h_quality = np.mean(h_line_quality) if h_line_quality else 0.0
        avg_v_quality = np.mean(v_line_quality) if v_line_quality else 0.0
        
        # Overall grid quality score (0-1)
        grid_score = (
            0.3 * spacing_consistency +
            0.2 * min(1.0, num_h_lines / 20.0) +  # Normalize to expected ~20 lines
            0.2 * min(1.0, num_v_lines / 20.0) +
            0.15 * min(1.0, num_intersections / 100.0) +  # Normalize to expected intersections
            0.15 * (avg_h_quality + avg_v_quality) / 2.0
        )
        
        return {
            'spacing_consistency': float(spacing_consistency),
            'num_horizontal_lines': num_h_lines,
            'num_vertical_lines': num_v_lines,
            'num_intersections': num_intersections,
            'avg_horizontal_line_quality': float(avg_h_quality),
            'avg_vertical_line_quality': float(avg_v_quality),
            'grid_score': float(grid_score)
        }
    
    def assess_signal_clarity(self, processed_signals: List[Dict]) -> Dict:
        """
        Assess clarity of extracted signals
        
        Args:
            processed_signals: List of lead signal dictionaries
            
        Returns:
            Dictionary with signal clarity metrics
        """
        contrast_scores = []
        edge_sharpness_scores = []
        
        for lead_data in processed_signals:
            sig = np.array(lead_data['values'])
            
            if len(sig) < 10:
                continue
            
            # Contrast: measure of signal variation
            signal_range = np.max(sig) - np.min(sig)
            signal_std = np.std(sig)
            contrast = signal_std / (signal_range + 1e-6)  # Normalized contrast
            
            # Edge sharpness: measure of signal transitions
            # Use gradient magnitude as proxy
            gradient = np.gradient(sig)
            edge_sharpness = np.mean(np.abs(gradient))
            
            contrast_scores.append(contrast)
            edge_sharpness_scores.append(edge_sharpness)
        
        avg_contrast = np.mean(contrast_scores) if contrast_scores else 0.0
        avg_edge_sharpness = np.mean(edge_sharpness_scores) if edge_sharpness_scores else 0.0
        
        # Normalize edge sharpness (typical ECG signals have gradients ~0.1-1.0)
        normalized_sharpness = min(1.0, avg_edge_sharpness / 1.0)
        
        clarity_score = (avg_contrast + normalized_sharpness) / 2.0
        
        return {
            'avg_contrast': float(avg_contrast),
            'avg_edge_sharpness': float(avg_edge_sharpness),
            'clarity_score': float(clarity_score)
        }
    
    def calculate_completeness(self, processed_signals: List[Dict]) -> Dict:
        """
        Calculate completeness of signal extraction
        
        Args:
            processed_signals: List of lead signal dictionaries
            
        Returns:
            Dictionary with completeness metrics
        """
        expected_leads = 12
        num_leads = len(processed_signals)
        
        # Check for valid signals (non-zero, non-constant)
        valid_leads = 0
        for lead_data in processed_signals:
            sig = np.array(lead_data['values'])
            if len(sig) > 0:
                # Check if signal has variation
                if np.std(sig) > 1e-6:
                    valid_leads += 1
        
        lead_completeness = num_leads / expected_leads
        valid_completeness = valid_leads / expected_leads
        
        # Check signal duration (should be ~2.5 seconds per lead)
        expected_duration = 2.5  # seconds
        durations = []
        for lead_data in processed_signals:
            duration = lead_data.get('duration', 0)
            durations.append(duration)
        
        avg_duration = np.mean(durations) if durations else 0.0
        duration_completeness = min(1.0, avg_duration / expected_duration)
        
        overall_completeness = (
            0.4 * lead_completeness +
            0.4 * valid_completeness +
            0.2 * duration_completeness
        )
        
        return {
            'num_leads': num_leads,
            'valid_leads': valid_leads,
            'lead_completeness': float(lead_completeness),
            'valid_completeness': float(valid_completeness),
            'avg_duration': float(avg_duration),
            'duration_completeness': float(duration_completeness),
            'overall_completeness': float(overall_completeness)
        }
    
    def _calculate_overall_score(self, snr_results: Dict, 
                                 grid_quality: Optional[Dict],
                                 signal_clarity: Dict,
                                 completeness: Dict) -> float:
        """Calculate overall quality score (0-1)"""
        # SNR component (0-1, normalized from 0-60 dB)
        snr_score = min(1.0, snr_results['mean_snr'] / 40.0)
        
        # Grid quality component
        grid_score = grid_quality['grid_score'] if grid_quality else 0.5
        
        # Signal clarity component
        clarity_score = signal_clarity['clarity_score']
        
        # Completeness component
        completeness_score = completeness['overall_completeness']
        
        # Weighted combination
        overall_score = (
            0.4 * snr_score +
            0.2 * grid_score +
            0.2 * clarity_score +
            0.2 * completeness_score
        )
        
        return float(overall_score)
