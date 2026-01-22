"""
Low Contrast Rejection Module
Final quality check - reject images with insufficient contrast

This is the LAST STEP in the pipeline (after all transformations)
"""

import numpy as np
import cv2
from typing import Dict


class LowContrastRejector:
    """
    Low Contrast Rejection for ECG Images
    
    Purpose: Final quality check - reject images with insufficient contrast
    
    Location: LAST STEP in pipeline (after all transformations)
    """
    
    # Rejection threshold
    MIN_CONTRAST_STD = 30  # Minimum histogram standard deviation
    
    def __init__(self, min_contrast_std: int = None):
        """
        Initialize Low Contrast Rejector
        
        Args:
            min_contrast_std: Minimum contrast standard deviation (default: 30)
        """
        self.min_contrast_std = min_contrast_std or LowContrastRejector.MIN_CONTRAST_STD
    
    def check(self, image: np.ndarray) -> Dict:
        """
        Check contrast after all preprocessing/transformation
        
        Args:
            image: Processed image (after all transformations)
            
        Returns:
            Dictionary with rejection status and details
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Calculate histogram standard deviation
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        mean = np.mean(hist)
        std = np.std(hist)
        
        # Rejection decision
        rejected = std < self.min_contrast_std
        
        # Quality assessment
        if std < self.min_contrast_std:
            quality = 'poor'
            quality_message = 'Rejected - insufficient contrast'
        elif std < 35:
            quality = 'fair'
            quality_message = 'Low contrast - acceptable'
        elif std < 50:
            quality = 'good'
            quality_message = 'Good contrast'
        else:
            quality = 'excellent'
            quality_message = 'Excellent contrast'
        
        # Recommendation if rejected
        recommendation = None
        if rejected:
            recommendation = (
                'Please use higher quality scan or adjust preprocessing parameters. '
                'Try applying CLAHE contrast enhancement before processing.'
            )
        
        return {
            'rejected': rejected,
            'contrast_std': float(std),
            'threshold': self.min_contrast_std,
            'quality': quality,
            'quality_message': quality_message,
            'recommendation': recommendation,
            'message': 'Low contrast - insufficient detail after processing' if rejected
                      else f'Contrast check passed (Std: {std:.2f})'
        }
    
    def check_with_recommendations(self, image: np.ndarray) -> Dict:
        """
        Check contrast with detailed recommendations
        
        Args:
            image: Processed image
            
        Returns:
            Dictionary with rejection status and recommendations
        """
        result = self.check(image)
        
        # Add specific recommendations
        if result['rejected']:
            result['action_items'] = [
                'Rescan image with better lighting',
                'Use higher quality scanner/camera',
                'Adjust CLAHE parameters during preprocessing',
                'Try different preprocessing methods',
                'Manual review may be required'
            ]
        else:
            result['action_items'] = ['Proceed with signal extraction']
        
        return result


# Convenience function
def reject_low_contrast(image: np.ndarray, min_contrast_std: int = None) -> Dict:
    """
    Convenience function to check and reject low contrast images
    
    Args:
        image: Processed image
        min_contrast_std: Minimum contrast standard deviation (optional)
        
    Returns:
        Rejection check results
    """
    rejector = LowContrastRejector(min_contrast_std=min_contrast_std)
    return rejector.check(image)
