"""
Illumination Normalization Module
Removes lighting artifacts (shadows, yellowing, uneven illumination)

Methods:
1. CLAHE (Contrast Limited Adaptive Histogram Equalization) - Default
2. Background Subtraction
3. Morphological Background Division
"""

import numpy as np
import cv2
from typing import Dict, Tuple, Optional


class IlluminationNormalizer:
    """
    Illumination Normalization for ECG Images
    
    Purpose: Remove lighting artifacts (shadows, yellowing, uneven illumination)
    """
    
    def __init__(self, method: str = 'clahe'):
        """
        Initialize Illumination Normalizer
        
        Args:
            method: 'clahe' (default), 'background_subtract', or 'morphological'
        """
        self.method = method.lower()
        if self.method not in ['clahe', 'background_subtract', 'morphological']:
            raise ValueError(f"Method must be 'clahe', 'background_subtract', or 'morphological', got '{method}'")
    
    def normalize(self, image: np.ndarray, **kwargs) -> Dict:
        """
        Normalize illumination
        
        Args:
            image: Input image
            **kwargs: Method-specific parameters
            
        Returns:
            Dictionary with normalized image and metadata
        """
        if self.method == 'clahe':
            return self._normalize_clahe(image, **kwargs)
        elif self.method == 'background_subtract':
            return self._normalize_background_subtract(image, **kwargs)
        else:
            return self._normalize_morphological(image, **kwargs)
    
    def _normalize_clahe(self, image: np.ndarray, clip_limit: float = 2.0, 
                        tile_grid_size: Tuple[int, int] = (8, 8)) -> Dict:
        """
        Normalize using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        
        CLAHE:
        - Boosts local contrast
        - Makes faint grids visible
        - Handles uneven illumination
        
        Args:
            image: Input image (grayscale)
            clip_limit: CLAHE clip limit (default: 2.0)
            tile_grid_size: Tile grid size for CLAHE (default: (8, 8))
            
        Returns:
            Dictionary with normalized image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        normalized = clahe.apply(gray)
        
        return {
            'method': 'clahe',
            'normalized_image': normalized,
            'original_image': gray,
            'parameters': {
                'clip_limit': clip_limit,
                'tile_grid_size': tile_grid_size
            }
        }
    
    def _normalize_background_subtract(self, image: np.ndarray, 
                                      kernel_size: int = 21) -> Dict:
        """
        Normalize using background subtraction
        
        Background Subtraction:
        - Create background model using median blur
        - Divide original by background
        - Flattens lighting, whitens paper
        
        Args:
            image: Input image
            kernel_size: Kernel size for median blur (default: 21)
            
        Returns:
            Dictionary with normalized image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Create background model using median blur
        background = cv2.medianBlur(gray, kernel_size)
        
        # Avoid division by zero
        background = np.maximum(background, 1)
        
        # Normalize: divide original by background and scale
        normalized = cv2.divide(gray, background, scale=255)
        
        # Ensure values are in valid range
        normalized = np.clip(normalized, 0, 255).astype(np.uint8)
        
        return {
            'method': 'background_subtract',
            'normalized_image': normalized,
            'original_image': gray,
            'background_model': background,
            'parameters': {
                'kernel_size': kernel_size
            }
        }
    
    def _normalize_morphological(self, image: np.ndarray, 
                                kernel_size: int = 21) -> Dict:
        """
        Normalize using morphological background division
        
        Morphological Background Division:
        - Dilate image to remove lines (creates background model)
        - Use as illumination map
        - Divide original by illumination map
        
        Args:
            image: Input image
            kernel_size: Kernel size for morphological operations (default: 21)
            
        Returns:
            Dictionary with normalized image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Create kernel for morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        
        # Dilate to remove lines and get background
        background = cv2.morphologyEx(gray, cv2.MORPH_DILATE, kernel)
        
        # Avoid division by zero
        background = np.maximum(background, 1)
        
        # Normalize: divide original by background and scale
        normalized = cv2.divide(gray, background, scale=255)
        
        # Ensure values are in valid range
        normalized = np.clip(normalized, 0, 255).astype(np.uint8)
        
        return {
            'method': 'morphological',
            'normalized_image': normalized,
            'original_image': gray,
            'background_model': background,
            'parameters': {
                'kernel_size': kernel_size
            }
        }


# Convenience functions
def normalize_clahe(image: np.ndarray, **kwargs) -> Dict:
    """Normalize using CLAHE"""
    normalizer = IlluminationNormalizer(method='clahe')
    return normalizer.normalize(image, **kwargs)


def normalize_background_subtract(image: np.ndarray, **kwargs) -> Dict:
    """Normalize using background subtraction"""
    normalizer = IlluminationNormalizer(method='background_subtract')
    return normalizer.normalize(image, **kwargs)


def normalize_morphological(image: np.ndarray, **kwargs) -> Dict:
    """Normalize using morphological background division"""
    normalizer = IlluminationNormalizer(method='morphological')
    return normalizer.normalize(image, **kwargs)
