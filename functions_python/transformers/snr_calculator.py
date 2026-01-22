"""
Signal-to-Noise Ratio Calculator
Compares transformed images to base image (-0001)
"""

import numpy as np
import cv2
from typing import Dict, Optional


class SNRCalculator:
    """Calculate SNR by comparing to base image"""
    
    def calculate_snr(self, base_image: np.ndarray, transformed_image: np.ndarray) -> Dict:
        """
        Calculate SNR comparing transformed to base image
        
        Args:
            base_image: Reference image (ending in -0001)
            transformed_image: Processed/transformed image
            
        Returns:
            {
                'snr_db': float,
                'signal_power': float,
                'noise_power': float,
                'snr_linear': float
            }
        """
        # Ensure same size
        if base_image.shape != transformed_image.shape:
            transformed_image = cv2.resize(transformed_image, 
                                          (base_image.shape[1], base_image.shape[0]))
        
        # Convert to grayscale if needed
        if len(base_image.shape) == 3:
            base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
        else:
            base_gray = base_image.copy()
            
        if len(transformed_image.shape) == 3:
            trans_gray = cv2.cvtColor(transformed_image, cv2.COLOR_BGR2GRAY)
        else:
            trans_gray = transformed_image.copy()
        
        # Convert to float for calculations
        base_float = base_gray.astype(np.float64)
        trans_float = trans_gray.astype(np.float64)
        
        # Calculate noise (difference)
        noise = trans_float - base_float
        
        # Signal power (variance of base image)
        signal_power = float(np.var(base_float))
        
        # Noise power (variance of difference)
        noise_power = float(np.var(noise))
        
        # Avoid division by zero
        if noise_power < 1e-10:
            snr_linear = 1000.0  # Very high SNR
            snr_db = 60.0
        else:
            snr_linear = signal_power / noise_power
            snr_db = 10.0 * np.log10(snr_linear)
            # Cap at 60 dB
            snr_db = min(60.0, max(0.0, snr_db))
        
        return {
            'snr_db': float(snr_db),
            'signal_power': signal_power,
            'noise_power': noise_power,
            'snr_linear': float(snr_linear)
        }
    
    def calculate_snr_for_methods(self, base_image: np.ndarray, 
                                 transformed_images: Dict[str, np.ndarray]) -> Dict:
        """
        Calculate SNR for multiple transformation methods
        
        Args:
            base_image: Reference image
            transformed_images: Dict of {method_name: image}
            
        Returns:
            Dict of {method_name: snr_result}
        """
        results = {}
        for method_name, transformed in transformed_images.items():
            results[method_name] = self.calculate_snr(base_image, transformed)
        
        # Find best method (highest SNR)
        best_method = max(results.keys(), key=lambda k: results[k]['snr_db'])
        
        return {
            'methods': results,
            'best_method': best_method,
            'best_snr': results[best_method]['snr_db']
        }
