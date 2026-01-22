"""
Color Isolation Module for ECG Images

This module provides methods to:
1. Isolate ECG traces by removing red grid and text
2. Isolate red grid by removing black ECG traces

Supports three libraries:
- OpenCV (method suffix: 'o')
- Pillow/PIL (method suffix: 'p')  
- scikit-image (method suffix: 's')

Output naming convention:
- {original_prefix}-{method}_ecg.png  (ECG traces only)
- {original_prefix}-{method}_grid.png (Grid only)
"""

import numpy as np
import cv2
from typing import Dict, Tuple, Optional, List
import base64
from io import BytesIO

# Try importing optional libraries
try:
    from PIL import Image as PILImage
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    from skimage import color, filters, morphology
    from skimage.color import rgb2hsv, hsv2rgb
    import skimage.io as skio
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False


class ColorIsolator:
    """
    Isolates colors from ECG images to separate grid from traces.
    
    Methods:
    - opencv (o): Uses OpenCV color space conversion and masking
    - pillow (p): Uses PIL channel splitting and manipulation
    - skimage (s): Uses scikit-image color processing
    """
    
    # Method identifiers for file naming
    METHOD_SUFFIXES = {
        'opencv': 'o',
        'pillow': 'p',
        'skimage': 's'
    }
    
    def __init__(self):
        self.available_methods = ['opencv']
        if PILLOW_AVAILABLE:
            self.available_methods.append('pillow')
        if SKIMAGE_AVAILABLE:
            self.available_methods.append('skimage')
    
    def get_available_methods(self) -> List[str]:
        """Return list of available methods based on installed libraries."""
        return self.available_methods
    
    def isolate_ecg_opencv(self, image: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Remove red grid and text, keep black ECG traces using OpenCV.
        
        Args:
            image: BGR image (OpenCV format)
            
        Returns:
            Tuple of (processed_image, metrics)
        """
        metrics = {'method': 'opencv', 'type': 'ecg'}
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Red color ranges in HSV (red wraps around 0/180)
        # Lower red range (0-10)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        # Upper red range (170-180)
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        # Create masks for red regions
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(mask_red1, mask_red2)
        
        # Also detect light pink/salmon grid colors
        lower_pink = np.array([0, 20, 150])
        upper_pink = np.array([20, 100, 255])
        pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
        
        # Combine red and pink masks
        grid_mask = cv2.bitwise_or(red_mask, pink_mask)
        
        # Dilate mask slightly to ensure complete removal
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        grid_mask = cv2.dilate(grid_mask, kernel, iterations=1)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Create output - white background where grid was
        result = gray.copy()
        result[grid_mask > 0] = 255
        
        # Also remove any remaining colored pixels (text labels often blue/black)
        # Keep only dark pixels that aren't in the grid mask
        dark_threshold = 100
        dark_mask = gray < dark_threshold
        non_grid_dark = np.logical_and(dark_mask, grid_mask == 0)
        
        # Final result: white background with dark traces
        final = np.ones_like(gray) * 255
        final[non_grid_dark] = gray[non_grid_dark]
        
        # Convert back to BGR for consistency
        final_bgr = cv2.cvtColor(final, cv2.COLOR_GRAY2BGR)
        
        # Calculate metrics
        metrics['pixels_removed'] = int(np.sum(grid_mask > 0))
        metrics['pixels_kept'] = int(np.sum(non_grid_dark))
        metrics['removal_percentage'] = float(metrics['pixels_removed'] / (image.shape[0] * image.shape[1]) * 100)
        
        return final_bgr, metrics
    
    def isolate_grid_opencv(self, image: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Remove black ECG traces, keep red grid only using OpenCV.
        
        Args:
            image: BGR image (OpenCV format)
            
        Returns:
            Tuple of (processed_image, metrics)
        """
        metrics = {'method': 'opencv', 'type': 'grid'}
        
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Red color ranges in HSV
        lower_red1 = np.array([0, 30, 30])
        upper_red1 = np.array([15, 255, 255])
        lower_red2 = np.array([165, 30, 30])
        upper_red2 = np.array([180, 255, 255])
        
        # Create masks for red regions
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(mask_red1, mask_red2)
        
        # Also include pink/salmon colors
        lower_pink = np.array([0, 10, 150])
        upper_pink = np.array([25, 150, 255])
        pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
        
        # Combine masks
        grid_mask = cv2.bitwise_or(red_mask, pink_mask)
        
        # Clean up mask
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        grid_mask = cv2.morphologyEx(grid_mask, cv2.MORPH_CLOSE, kernel)
        
        # Create output - white background with red grid only
        result = np.ones_like(image) * 255
        result[grid_mask > 0] = image[grid_mask > 0]
        
        # Calculate metrics
        metrics['pixels_kept'] = int(np.sum(grid_mask > 0))
        metrics['pixels_removed'] = int(image.shape[0] * image.shape[1] - metrics['pixels_kept'])
        metrics['grid_percentage'] = float(metrics['pixels_kept'] / (image.shape[0] * image.shape[1]) * 100)
        
        return result, metrics
    
    def isolate_ecg_pillow(self, image: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Remove red grid using Pillow channel splitting.
        
        Args:
            image: BGR image (will be converted)
            
        Returns:
            Tuple of (processed_image, metrics)
        """
        if not PILLOW_AVAILABLE:
            raise ImportError("Pillow not available")
        
        metrics = {'method': 'pillow', 'type': 'ecg'}
        
        # Convert BGR to RGB for Pillow
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = PILImage.fromarray(rgb)
        
        # Split into channels
        r, g, b = pil_image.split()
        r_array = np.array(r)
        g_array = np.array(g)
        b_array = np.array(b)
        
        # Detect red pixels: high R, low G and B
        # Red grid typically has R > 150, G < 100, B < 100
        red_dominant = (r_array > 120) & (r_array > g_array + 30) & (r_array > b_array + 30)
        
        # Also detect pink: high R, medium G and B
        pink = (r_array > 180) & (g_array > 100) & (b_array > 100) & (r_array > g_array)
        
        # Combine masks
        grid_mask = red_dominant | pink
        
        # Create grayscale output
        gray = np.array(pil_image.convert('L'))
        
        # Remove grid, keep dark traces
        result = np.ones_like(gray) * 255
        dark_mask = gray < 120
        keep_mask = dark_mask & ~grid_mask
        result[keep_mask] = gray[keep_mask]
        
        # Convert back to BGR
        result_bgr = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        
        metrics['pixels_removed'] = int(np.sum(grid_mask))
        metrics['pixels_kept'] = int(np.sum(keep_mask))
        metrics['removal_percentage'] = float(metrics['pixels_removed'] / (image.shape[0] * image.shape[1]) * 100)
        
        return result_bgr, metrics
    
    def isolate_grid_pillow(self, image: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Keep only red grid using Pillow channel analysis.
        
        Args:
            image: BGR image
            
        Returns:
            Tuple of (processed_image, metrics)
        """
        if not PILLOW_AVAILABLE:
            raise ImportError("Pillow not available")
        
        metrics = {'method': 'pillow', 'type': 'grid'}
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = PILImage.fromarray(rgb)
        
        # Split channels
        r, g, b = pil_image.split()
        r_array = np.array(r)
        g_array = np.array(g)
        b_array = np.array(b)
        
        # Detect red/pink grid pixels
        red_dominant = (r_array > 100) & (r_array > g_array + 20) & (r_array > b_array + 20)
        pink = (r_array > 150) & (g_array > 80) & (b_array > 80) & (r_array > g_array)
        
        grid_mask = red_dominant | pink
        
        # Create white output with grid only
        result = np.ones_like(image) * 255
        result[grid_mask] = image[grid_mask]
        
        metrics['pixels_kept'] = int(np.sum(grid_mask))
        metrics['grid_percentage'] = float(metrics['pixels_kept'] / (image.shape[0] * image.shape[1]) * 100)
        
        return result, metrics
    
    def isolate_ecg_skimage(self, image: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Remove red grid using scikit-image color processing.
        
        Args:
            image: BGR image
            
        Returns:
            Tuple of (processed_image, metrics)
        """
        if not SKIMAGE_AVAILABLE:
            raise ImportError("scikit-image not available")
        
        metrics = {'method': 'skimage', 'type': 'ecg'}
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Normalize to 0-1 range for skimage
        rgb_float = rgb.astype(np.float64) / 255.0
        
        # Convert to HSV using skimage
        hsv = rgb2hsv(rgb_float)
        h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
        
        # Red hue is around 0 and 1 (wraps around)
        # Detect red: hue near 0 or 1, with some saturation
        red_hue = (h < 0.08) | (h > 0.92)
        saturated = s > 0.15
        red_mask = red_hue & saturated
        
        # Dilate to ensure complete removal
        red_mask = morphology.dilation(red_mask, morphology.disk(2))
        
        # Convert to grayscale
        gray = color.rgb2gray(rgb_float)
        
        # Keep only dark non-red pixels
        dark_mask = gray < 0.5
        keep_mask = dark_mask & ~red_mask
        
        # Create output
        result = np.ones_like(gray)
        result[keep_mask] = gray[keep_mask]
        
        # Convert back to uint8 BGR
        result_uint8 = (result * 255).astype(np.uint8)
        result_bgr = cv2.cvtColor(result_uint8, cv2.COLOR_GRAY2BGR)
        
        metrics['pixels_removed'] = int(np.sum(red_mask))
        metrics['pixels_kept'] = int(np.sum(keep_mask))
        metrics['removal_percentage'] = float(metrics['pixels_removed'] / (image.shape[0] * image.shape[1]) * 100)
        
        return result_bgr, metrics
    
    def isolate_grid_skimage(self, image: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Keep only red grid using scikit-image.
        
        Args:
            image: BGR image
            
        Returns:
            Tuple of (processed_image, metrics)
        """
        if not SKIMAGE_AVAILABLE:
            raise ImportError("scikit-image not available")
        
        metrics = {'method': 'skimage', 'type': 'grid'}
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb_float = rgb.astype(np.float64) / 255.0
        
        # Convert to HSV
        hsv = rgb2hsv(rgb_float)
        h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
        
        # Detect red/pink grid
        red_hue = (h < 0.1) | (h > 0.9)
        has_color = s > 0.1
        grid_mask = red_hue & has_color
        
        # Create white output with grid
        result = np.ones_like(image) * 255
        result[grid_mask] = image[grid_mask]
        
        metrics['pixels_kept'] = int(np.sum(grid_mask))
        metrics['grid_percentage'] = float(metrics['pixels_kept'] / (image.shape[0] * image.shape[1]) * 100)
        
        return result, metrics
    
    def process(self, image: np.ndarray, method: str = 'opencv', 
                output_type: str = 'both') -> Dict:
        """
        Process image to isolate colors.
        
        Args:
            image: BGR image
            method: 'opencv', 'pillow', or 'skimage'
            output_type: 'ecg', 'grid', or 'both'
            
        Returns:
            Dictionary with processed images and metrics
        """
        result = {
            'success': True,
            'method': method,
            'method_suffix': self.METHOD_SUFFIXES.get(method, 'x'),
            'outputs': {}
        }
        
        try:
            if output_type in ['ecg', 'both']:
                if method == 'opencv':
                    ecg_img, ecg_metrics = self.isolate_ecg_opencv(image)
                elif method == 'pillow':
                    ecg_img, ecg_metrics = self.isolate_ecg_pillow(image)
                elif method == 'skimage':
                    ecg_img, ecg_metrics = self.isolate_ecg_skimage(image)
                else:
                    raise ValueError(f"Unknown method: {method}")
                
                result['outputs']['ecg'] = {
                    'image': ecg_img,
                    'metrics': ecg_metrics
                }
            
            if output_type in ['grid', 'both']:
                if method == 'opencv':
                    grid_img, grid_metrics = self.isolate_grid_opencv(image)
                elif method == 'pillow':
                    grid_img, grid_metrics = self.isolate_grid_pillow(image)
                elif method == 'skimage':
                    grid_img, grid_metrics = self.isolate_grid_skimage(image)
                else:
                    raise ValueError(f"Unknown method: {method}")
                
                result['outputs']['grid'] = {
                    'image': grid_img,
                    'metrics': grid_metrics
                }
                
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def generate_output_filename(self, original_filename: str, method: str, 
                                  output_type: str, next_number: int = 10) -> str:
        """
        Generate output filename following naming convention.
        
        Naming: {prefix}-{method}{number}-{r|b}.png
        - r = red (grid only)
        - b = black (ECG traces only)
        
        Args:
            original_filename: Original file name (e.g., "12345-0001.png")
            method: Processing method ('opencv', 'pillow', 'skimage')
            output_type: 'ecg' or 'grid'
            next_number: Number to use (should be higher than existing)
            
        Returns:
            New filename (e.g., "12345-o0010-b.png")
        """
        import os
        base, ext = os.path.splitext(original_filename)
        
        # Extract prefix (number before the first dash)
        if '-' in base:
            prefix = base.split('-')[0]
        else:
            prefix = base
        
        # Get method suffix
        method_suffix = self.METHOD_SUFFIXES.get(method, 'x')
        
        # Get color suffix: r = red/grid, b = black/ecg
        color_suffix = 'r' if output_type == 'grid' else 'b'
        
        # Format number with leading zeros (4 digits)
        num_str = f"{next_number:04d}"
        
        # Generate new filename: {prefix}-{method}{number}-{color}.png
        new_filename = f"{prefix}-{method_suffix}{num_str}-{color_suffix}{ext}"
        
        return new_filename
    
    def get_next_number_for_group(self, existing_filenames: list, method: str) -> int:
        """
        Get the next available number for a group, considering existing files.
        
        Args:
            existing_filenames: List of existing filenames in the group
            method: Processing method ('opencv', 'pillow', 'skimage')
            
        Returns:
            Next number to use (starts at 10 for first isolated image)
        """
        import re
        
        method_suffix = self.METHOD_SUFFIXES.get(method, 'x')
        max_number = 9  # Start at 10 for isolated images
        
        for filename in existing_filenames:
            # Check for existing isolated files with pattern: prefix-{method}{number}-{r|b}
            # e.g., 12345-o0010-b.png
            match = re.search(rf'-{method_suffix}(\d+)-[rb]\.', filename)
            if match:
                num = int(match.group(1))
                max_number = max(max_number, num)
        
        return max_number + 1


# Convenience functions
def isolate_ecg(image: np.ndarray, method: str = 'opencv') -> Tuple[np.ndarray, Dict]:
    """Convenience function to isolate ECG traces."""
    isolator = ColorIsolator()
    result = isolator.process(image, method=method, output_type='ecg')
    if result['success']:
        return result['outputs']['ecg']['image'], result['outputs']['ecg']['metrics']
    else:
        raise RuntimeError(result.get('error', 'Unknown error'))


def isolate_grid(image: np.ndarray, method: str = 'opencv') -> Tuple[np.ndarray, Dict]:
    """Convenience function to isolate grid."""
    isolator = ColorIsolator()
    result = isolator.process(image, method=method, output_type='grid')
    if result['success']:
        return result['outputs']['grid']['image'], result['outputs']['grid']['metrics']
    else:
        raise RuntimeError(result.get('error', 'Unknown error'))


# Test function
def test_isolation():
    """Test the color isolation with a sample image."""
    # Create a test image with red grid and black traces
    test_img = np.ones((200, 300, 3), dtype=np.uint8) * 255
    
    # Add red grid lines
    for i in range(0, 200, 20):
        test_img[i:i+2, :] = [0, 0, 200]  # Red in BGR
    for j in range(0, 300, 20):
        test_img[:, j:j+2] = [0, 0, 200]
    
    # Add black ECG-like trace
    for x in range(300):
        y = int(100 + 30 * np.sin(x * 0.1))
        if 0 <= y < 200:
            test_img[y:y+3, x] = [0, 0, 0]
    
    isolator = ColorIsolator()
    
    print(f"Available methods: {isolator.get_available_methods()}")
    
    for method in isolator.get_available_methods():
        print(f"\nTesting {method}...")
        result = isolator.process(test_img, method=method, output_type='both')
        
        if result['success']:
            print(f"  ECG metrics: {result['outputs']['ecg']['metrics']}")
            print(f"  Grid metrics: {result['outputs']['grid']['metrics']}")
        else:
            print(f"  Error: {result.get('error')}")
    
    return True


if __name__ == '__main__':
    test_isolation()
