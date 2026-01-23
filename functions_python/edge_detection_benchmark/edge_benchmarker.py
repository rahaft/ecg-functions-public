"""
EdgeBenchmarker Module
Contains three edge detection methods: Canny, Sobel, and Laplacian
"""

import numpy as np
import cv2
from typing import Dict, Tuple, Optional


class EdgeBenchmarker:
    """
    Edge detection benchmarking class.
    Implements Canny, Sobel, and Laplacian methods with optimization for different tasks.
    """
    
    def __init__(self):
        """Initialize EdgeBenchmarker."""
        pass
    
    def get_canny(self, image: np.ndarray,
                  low_threshold: Optional[int] = None,
                  high_threshold: Optional[int] = None,
                  aperture_size: int = 3,
                  l2_gradient: bool = False) -> Dict[str, np.ndarray]:
        """
        Canny edge detection - optimized for continuity.
        
        Best for: ECG signal extraction (produces continuous lines)
        
        Args:
            image: Grayscale input image
            low_threshold: Lower threshold (None = auto-calculate)
            high_threshold: Upper threshold (None = auto-calculate)
            aperture_size: Aperture size for Sobel operator (3, 5, or 7)
            l2_gradient: Use L2 gradient (more accurate but slower)
            
        Returns:
            Dictionary with:
            - 'edges': Binary edge map
            - 'method': 'canny'
            - 'params': Parameters used
        """
        # Auto-calculate thresholds if not provided
        if low_threshold is None or high_threshold is None:
            median_val = np.median(image)
            if low_threshold is None:
                low_threshold = max(0, int(0.66 * median_val))
            if high_threshold is None:
                high_threshold = min(255, int(1.33 * median_val))
        
        # Apply Canny edge detection
        edges = cv2.Canny(image, low_threshold, high_threshold, 
                         apertureSize=aperture_size, L2gradient=l2_gradient)
        
        # Convert to 8-bit unsigned integer
        edges = cv2.convertScaleAbs(edges)
        
        return {
            'edges': edges,
            'method': 'canny',
            'params': {
                'low_threshold': low_threshold,
                'high_threshold': high_threshold,
                'aperture_size': aperture_size,
                'l2_gradient': l2_gradient
            }
        }
    
    def get_sobel(self, image: np.ndarray,
                  ksize: int = 3,
                  dx: int = 1,
                  dy: int = 1,
                  scale: int = 1,
                  delta: int = 0) -> Dict[str, np.ndarray]:
        """
        Sobel operator - optimized for directional gradients.
        
        Best for: Document boundary detection (better at finding paper edges)
        
        Args:
            image: Grayscale input image
            ksize: Kernel size (1, 3, 5, or 7)
            dx: Order of derivative in x direction
            dy: Order of derivative in y direction
            scale: Optional scale factor
            delta: Optional delta value added to result
            
        Returns:
            Dictionary with:
            - 'edges': Combined Sobel edge map
            - 'sobel_x': X-direction gradient
            - 'sobel_y': Y-direction gradient
            - 'method': 'sobel'
            - 'params': Parameters used
        """
        # Calculate Sobel gradients
        sobel_x = cv2.Sobel(image, cv2.CV_64F, dx, 0, ksize=ksize, scale=scale, delta=delta)
        sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, dy, ksize=ksize, scale=scale, delta=delta)
        
        # Combine X and Y gradients
        sobel_combined = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # Convert to 8-bit unsigned integer
        edges = cv2.convertScaleAbs(sobel_combined)
        
        # Optional: Apply threshold to reduce noise
        # Use percentile-based thresholding
        threshold = np.percentile(edges, 90)
        _, edges = cv2.threshold(edges, threshold, 255, cv2.THRESH_BINARY)
        
        return {
            'edges': edges,
            'sobel_x': cv2.convertScaleAbs(sobel_x),
            'sobel_y': cv2.convertScaleAbs(sobel_y),
            'method': 'sobel',
            'params': {
                'ksize': ksize,
                'dx': dx,
                'dy': dy,
                'scale': scale,
                'delta': delta
            }
        }
    
    def get_laplacian(self, image: np.ndarray,
                      ksize: int = 3,
                      scale: int = 1,
                      delta: int = 0) -> Dict[str, np.ndarray]:
        """
        Laplacian operator - optimized for rapid intensity changes.
        
        Best for: Detecting sharp transitions and fine details
        
        Args:
            image: Grayscale input image
            ksize: Kernel size (1, 3, 5, or 7)
            scale: Optional scale factor
            delta: Optional delta value added to result
            
        Returns:
            Dictionary with:
            - 'edges': Laplacian edge map
            - 'method': 'laplacian'
            - 'params': Parameters used
        """
        # Apply Laplacian operator
        laplacian = cv2.Laplacian(image, cv2.CV_64F, ksize=ksize, scale=scale, delta=delta)
        
        # Convert to absolute values and scale to 8-bit
        laplacian_abs = np.abs(laplacian)
        
        # Convert to 8-bit unsigned integer
        edges = cv2.convertScaleAbs(laplacian_abs)
        
        # Apply percentile-based thresholding
        threshold = np.percentile(edges, 90)
        _, edges = cv2.threshold(edges, threshold, 255, cv2.THRESH_BINARY)
        
        return {
            'edges': edges,
            'method': 'laplacian',
            'params': {
                'ksize': ksize,
                'scale': scale,
                'delta': delta
            }
        }
    
    def benchmark_all(self, image: np.ndarray,
                     canny_params: Dict = None,
                     sobel_params: Dict = None,
                     laplacian_params: Dict = None) -> Dict[str, Dict]:
        """
        Run all three edge detection methods on the same image.
        
        Args:
            image: Grayscale input image
            canny_params: Optional parameters for Canny
            sobel_params: Optional parameters for Sobel
            laplacian_params: Optional parameters for Laplacian
            
        Returns:
            Dictionary with results from all three methods
        """
        results = {}
        
        # Canny
        if canny_params:
            results['canny'] = self.get_canny(image, **canny_params)
        else:
            results['canny'] = self.get_canny(image)
        
        # Sobel
        if sobel_params:
            results['sobel'] = self.get_sobel(image, **sobel_params)
        else:
            results['sobel'] = self.get_sobel(image)
        
        # Laplacian
        if laplacian_params:
            results['laplacian'] = self.get_laplacian(image, **laplacian_params)
        else:
            results['laplacian'] = self.get_laplacian(image)
        
        return results
