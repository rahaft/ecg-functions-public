"""
PreProcessor Module
Handles image loading, HSV masking, and noise reduction
"""

import numpy as np
import cv2
from typing import Dict, Tuple, Optional


class PreProcessor:
    """
    Pre-processing class for ECG images.
    Handles grayscale conversion, HSV masking, and noise reduction.
    """
    
    def __init__(self, blur_kernel_size: Tuple[int, int] = (3, 3), 
                 blur_sigma: float = 0):
        """
        Initialize PreProcessor.
        
        Args:
            blur_kernel_size: Gaussian blur kernel size (default: (3, 3))
            blur_sigma: Gaussian blur sigma (0 = auto-calculate)
        """
        self.blur_kernel_size = blur_kernel_size
        self.blur_sigma = blur_sigma
    
    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load image from file path.
        
        Args:
            image_path: Path to image file
            
        Returns:
            BGR image as numpy array
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        return image
    
    def load_from_array(self, image: np.ndarray) -> np.ndarray:
        """
        Load image from numpy array (for use with existing images).
        
        Args:
            image: Image as numpy array (BGR format)
            
        Returns:
            BGR image as numpy array
        """
        return image.copy()
    
    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert BGR image to grayscale.
        
        Args:
            image: BGR image
            
        Returns:
            Grayscale image
        """
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image.copy()
    
    def apply_gaussian_blur(self, image: np.ndarray) -> np.ndarray:
        """
        Apply Gaussian blur for noise reduction.
        
        Args:
            image: Input image (grayscale or BGR)
            
        Returns:
            Blurred image
        """
        return cv2.GaussianBlur(image, self.blur_kernel_size, self.blur_sigma)
    
    def isolate_hsv_mask(self, image: np.ndarray, 
                         lower_hsv: Tuple[int, int, int] = None,
                         upper_hsv: Tuple[int, int, int] = None,
                         target: str = 'signal') -> Tuple[np.ndarray, np.ndarray]:
        """
        Isolate signal or grid using HSV color masking.
        
        Args:
            image: BGR image
            lower_hsv: Lower HSV bounds (default: auto-detect)
            upper_hsv: Upper HSV bounds (default: auto-detect)
            target: 'signal' (black/blue ECG trace) or 'grid' (red/pink grid)
            
        Returns:
            Tuple of (masked_image, mask)
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        if target == 'signal':
            # Isolate black/blue ECG signal (remove red/pink grid)
            if lower_hsv is None:
                # Black/dark blue range
                lower_hsv = np.array([0, 0, 0])
            if upper_hsv is None:
                # Dark colors (low value)
                upper_hsv = np.array([180, 255, 100])
            
            # Also exclude red/pink grid
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            
            # Create mask for signal (not red)
            mask_signal = cv2.inRange(hsv, lower_hsv, upper_hsv)
            mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask_red = cv2.bitwise_or(mask_red1, mask_red2)
            
            # Signal mask = dark colors AND not red
            mask = cv2.bitwise_and(mask_signal, cv2.bitwise_not(mask_red))
            
        else:  # target == 'grid'
            # Isolate red/pink grid
            if lower_hsv is None:
                lower_red1 = np.array([0, 50, 50])
                upper_red1 = np.array([10, 255, 255])
                lower_red2 = np.array([170, 50, 50])
                upper_red2 = np.array([180, 255, 255])
            else:
                lower_red1 = lower_hsv
                upper_red1 = upper_hsv
                lower_red2 = lower_hsv
                upper_red2 = upper_hsv
            
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = cv2.bitwise_or(mask1, mask2)
        
        # Apply mask to original image
        masked_image = cv2.bitwise_and(image, image, mask=mask)
        
        return masked_image, mask
    
    def apply_adaptive_threshold(self, image: np.ndarray,
                                 max_value: int = 255,
                                 adaptive_method: int = cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 threshold_type: int = cv2.THRESH_BINARY,
                                 block_size: int = 11,
                                 C: float = 2) -> np.ndarray:
        """
        Apply adaptive thresholding to handle uneven lighting.
        
        Args:
            image: Grayscale image
            max_value: Maximum value for thresholding
            adaptive_method: Adaptive method (GAUSSIAN_C or MEAN_C)
            threshold_type: THRESH_BINARY or THRESH_BINARY_INV
            block_size: Size of neighborhood (must be odd)
            C: Constant subtracted from mean
            
        Returns:
            Thresholded binary image
        """
        return cv2.adaptiveThreshold(image, max_value, adaptive_method, 
                                     threshold_type, block_size, C)
    
    def preprocess(self, image: np.ndarray, 
                  apply_hsv_mask: bool = True,
                  target: str = 'signal',
                  apply_adaptive_thresh: bool = False) -> Dict[str, np.ndarray]:
        """
        Complete preprocessing pipeline.
        
        Args:
            image: Input BGR image
            apply_hsv_mask: Whether to apply HSV color masking
            target: 'signal' or 'grid' for HSV masking
            apply_adaptive_thresh: Whether to apply adaptive thresholding
            
        Returns:
            Dictionary with processed images:
            - 'original': Original image
            - 'grayscale': Grayscale image
            - 'blurred': Blurred image
            - 'masked': HSV masked image (if applied)
            - 'mask': HSV mask (if applied)
            - 'thresholded': Adaptive threshold result (if applied)
            - 'final': Final processed image for edge detection
        """
        result = {
            'original': image.copy()
        }
        
        # Convert to grayscale
        gray = self.convert_to_grayscale(image)
        result['grayscale'] = gray
        
        # Apply Gaussian blur
        blurred = self.apply_gaussian_blur(gray)
        result['blurred'] = blurred
        
        # Apply HSV masking if requested
        if apply_hsv_mask and len(image.shape) == 3:
            masked, mask = self.isolate_hsv_mask(image, target=target)
            result['masked'] = masked
            result['mask'] = mask
            # Convert masked image to grayscale for edge detection
            if len(masked.shape) == 3:
                masked_gray = self.convert_to_grayscale(masked)
            else:
                masked_gray = masked
            # Apply blur to masked image
            blurred = self.apply_gaussian_blur(masked_gray)
        
        # Apply adaptive thresholding if requested
        if apply_adaptive_thresh:
            thresholded = self.apply_adaptive_threshold(blurred)
            result['thresholded'] = thresholded
            result['final'] = thresholded
        else:
            result['final'] = blurred
        
        return result
