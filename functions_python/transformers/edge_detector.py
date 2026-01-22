"""
Edge Detection Transformer
Detects image boundaries and edges for ECG image preprocessing

Documentation:
- Purpose: Detect image edges to crop unnecessary borders and improve processing
- Methods: Canny, Sobel, Laplacian, Contour-based detection
- What works: Canny edge detection with adaptive thresholds
- What didn't work: Simple thresholding (too sensitive to noise)
- Changes: Added morphological operations to clean up edge detection
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
from .base_transformer import BaseTransformer


class EdgeDetector(BaseTransformer):
    """
    Detects edges and boundaries in ECG images.
    Useful for cropping unnecessary borders and detecting image boundaries.
    
    Notebook-ready: Yes - all dependencies are standard (numpy, cv2)
    """
    
    def __init__(self, method: str = 'canny', low_threshold: int = 50, 
                 high_threshold: int = 150, kernel_size: int = 3):
        """
        Initialize edge detector.
        
        Args:
            method: Detection method ('canny', 'sobel', 'laplacian', 'contour')
            low_threshold: Lower threshold for Canny edge detection
            high_threshold: Upper threshold for Canny edge detection
            kernel_size: Kernel size for edge detection
        """
        super().__init__(f"edge_detector_{method}")
        self.method = method
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.kernel_size = kernel_size
        
    def detect_grid(self, image: np.ndarray) -> Dict:
        """
        Detect edges in the image.
        
        Args:
            image: Input ECG image (numpy array)
            
        Returns:
            Dictionary with:
            - edges: Edge map (binary image)
            - contours: List of detected contours
            - bounding_box: Bounding box of image content (x, y, w, h)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        edges = self._detect_edges(gray)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find bounding box of content
        if contours:
            # Get largest contour (assumed to be main image content)
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
        else:
            # Fallback to full image
            h, w = gray.shape
            x, y = 0, 0
        
        return {
            'edges': edges,
            'contours': contours,
            'bounding_box': (x, y, w, h),
            'edge_count': len(contours),
            'edge_pixels': int(np.sum(edges > 0))
        }
    
    def _detect_edges(self, gray: np.ndarray) -> np.ndarray:
        """
        Apply edge detection method.
        
        Args:
            gray: Grayscale image
            
        Returns:
            Binary edge map
        """
        if self.method == 'canny':
            # Adaptive threshold calculation
            median_val = np.median(gray)
            low = max(0, int(0.66 * median_val))
            high = min(255, int(1.33 * median_val))
            
            edges = cv2.Canny(gray, low, high, apertureSize=self.kernel_size)
            
            # Morphological operations to clean up
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            edges = cv2.morphologyEx(edges, cv2.MORPH_DILATE, kernel)
            
        elif self.method == 'sobel':
            # Sobel edge detection
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=self.kernel_size)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=self.kernel_size)
            sobel = np.sqrt(sobelx**2 + sobely**2)
            edges = (sobel > np.percentile(sobel, 90)).astype(np.uint8) * 255
            
        elif self.method == 'laplacian':
            # Laplacian edge detection
            laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=self.kernel_size)
            edges = (np.abs(laplacian) > np.percentile(np.abs(laplacian), 90)).astype(np.uint8) * 255
            
        elif self.method == 'contour':
            # Threshold-based contour detection
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            edges = thresh
            
        else:
            raise ValueError(f"Unknown edge detection method: {self.method}")
        
        return edges
    
    def estimate_transformation(self, grid_data: Dict) -> Dict:
        """
        Estimate crop parameters from edge detection.
        
        Args:
            grid_data: Output from detect_grid()
            
        Returns:
            Dictionary with crop parameters
        """
        x, y, w, h = grid_data['bounding_box']
        
        return {
            'crop_x': int(x),
            'crop_y': int(y),
            'crop_width': int(w),
            'crop_height': int(h),
            'method': self.method
        }
    
    def apply_transformation(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """
        Crop image based on detected edges.
        
        Args:
            image: Input image
            params: Crop parameters from estimate_transformation()
            
        Returns:
            Cropped image
        """
        x = params['crop_x']
        y = params['crop_y']
        w = params['crop_width']
        h = params['crop_height']
        
        # Ensure valid crop coordinates
        h_img, w_img = image.shape[:2]
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        w = min(w, w_img - x)
        h = min(h, h_img - y)
        
        if w > 0 and h > 0:
            return image[y:y+h, x:x+w]
        else:
            return image
    
    def calculate_quality(self, original_grid: Dict, transformed_grid: Dict) -> Dict:
        """
        Calculate quality metrics for edge detection.
        
        Args:
            original_grid: Grid data from original image
            transformed_grid: Grid data from transformed image
            
        Returns:
            Dictionary with quality metrics
        """
        original_area = original_grid.get('edge_pixels', 0)
        transformed_area = transformed_grid.get('edge_pixels', 0)
        
        # Calculate reduction ratio (should be lower after cropping)
        reduction_ratio = transformed_area / original_area if original_area > 0 else 0
        
        return {
            'edge_reduction_ratio': float(reduction_ratio),
            'original_edge_pixels': int(original_area),
            'transformed_edge_pixels': int(transformed_area),
            'crop_effectiveness': float(1.0 - reduction_ratio) if reduction_ratio < 1.0 else 0.0
        }
    
    def detect_image_boundaries(self, image: np.ndarray, padding: int = 10) -> Tuple[int, int, int, int]:
        """
        Detect image content boundaries with padding.
        
        Args:
            image: Input ECG image
            padding: Padding to add around detected content (pixels)
            
        Returns:
            Tuple of (x, y, width, height) for crop region
        """
        grid_data = self.detect_grid(image)
        x, y, w, h = grid_data['bounding_box']
        
        # Add padding
        h_img, w_img = image.shape[:2]
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(w_img - x, w + 2 * padding)
        h = min(h_img - y, h + 2 * padding)
        
        return (x, y, w, h)


def detect_edges(image: np.ndarray, method: str = 'canny') -> Dict:
    """
    Convenience function for edge detection.
    
    Args:
        image: Input ECG image
        method: Detection method ('canny', 'sobel', 'laplacian', 'contour')
        
    Returns:
        Dictionary with edges, contours, and bounding box
    """
    detector = EdgeDetector(method=method)
    return detector.detect_grid(image)


def crop_to_content(image: np.ndarray, padding: int = 10) -> np.ndarray:
    """
    Crop image to content boundaries.
    
    Args:
        image: Input ECG image
        padding: Padding around content (pixels)
        
    Returns:
        Cropped image
    """
    detector = EdgeDetector()
    x, y, w, h = detector.detect_image_boundaries(image, padding=padding)
    
    h_img, w_img = image.shape[:2]
    x = max(0, min(x, w_img - 1))
    y = max(0, min(y, h_img - 1))
    w = min(w, w_img - x)
    h = min(h, h_img - y)
    
    if w > 0 and h > 0:
        return image[y:y+h, x:x+w]
    else:
        return image
