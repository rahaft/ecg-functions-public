"""
Color Space Separation Module
Handles ANY color combination for ECG images

Methods:
1. LAB Color Space (Default) - Separate red/pink grids from black ECG
2. HSV Color Space (Alternative) - Isolate specific colors
"""

import numpy as np
import cv2
from typing import Dict, Tuple, Optional


class ColorSeparator:
    """
    Color Space Separation for ECG Images
    
    Purpose: Handle ANY color combination (red grids, black grids, colored paper)
    """
    
    def __init__(self, method: str = 'lab'):
        """
        Initialize Color Separator
        
        Args:
            method: 'lab' (default) or 'hsv'
        """
        self.method = method.lower()
        if self.method not in ['lab', 'hsv']:
            raise ValueError(f"Method must be 'lab' or 'hsv', got '{method}'")
    
    def separate(self, image: np.ndarray, grid_color: str = 'auto') -> Dict:
        """
        Separate grid from ECG trace based on color
        
        Args:
            image: Input image (BGR format)
            grid_color: 'red', 'black', or 'auto' (default)
            
        Returns:
            Dictionary with separated components
        """
        if self.method == 'lab':
            return self._separate_lab(image, grid_color)
        else:
            return self._separate_hsv(image, grid_color)
    
    def _separate_lab(self, image: np.ndarray, grid_color: str = 'auto') -> Dict:
        """
        Separate using LAB color space
        
        LAB separation:
        - L-channel (Lightness): ECG trace (always darker)
        - A-channel (Red/Green axis): Grid if red/pink
        
        Args:
            image: Input BGR image
            grid_color: 'red', 'black', or 'auto'
            
        Returns:
            Dictionary with separated components
        """
        # Convert BGR to LAB
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        # L-channel contains trace (dark = signal, light = background)
        trace_image = l_channel
        
        # A-channel shows red/green (red = positive, green = negative)
        # For red/pink grids, A-channel will be high
        # For black grids, A-channel will be neutral
        
        if grid_color == 'auto':
            # Auto-detect: if A-channel has high values, it's a red grid
            a_mean = np.mean(a_channel)
            grid_color = 'red' if a_mean > 127 else 'black'
        
        if grid_color == 'red':
            # Red/pink grid: A-channel > threshold
            # Threshold around 127 (neutral) + offset
            threshold = 140  # Adjustable
            grid_mask = a_channel > threshold
        else:
            # Black grid: use L-channel (low values = dark = grid)
            threshold = 127  # Adjustable
            grid_mask = l_channel < threshold
        
        # Create grid-only image
        grid_image = cv2.bitwise_and(image, image, mask=grid_mask.astype(np.uint8) * 255)
        
        # Create trace-only image (inverse of grid mask)
        trace_mask = ~grid_mask
        trace_only_image = cv2.bitwise_and(image, image, mask=trace_mask.astype(np.uint8) * 255)
        
        return {
            'method': 'lab',
            'grid_color': grid_color,
            'trace_image': trace_image,  # L-channel (grayscale)
            'grid_mask': grid_mask.astype(np.uint8) * 255,
            'grid_image': grid_image,
            'trace_only_image': trace_only_image,
            'a_channel': a_channel,  # For visualization
            'l_channel': l_channel,  # For visualization
        }
    
    def _separate_hsv(self, image: np.ndarray, grid_color: str = 'auto') -> Dict:
        """
        Separate using HSV color space
        
        HSV separation:
        - H-channel (Hue): Isolate specific colors
        - S-channel (Saturation): Separate grid from signal
        
        Args:
            image: Input BGR image
            grid_color: 'red', 'black', or 'auto'
            
        Returns:
            Dictionary with separated components
        """
        # Convert BGR to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h_channel, s_channel, v_channel = cv2.split(hsv)
        
        # V-channel (Value/Brightness): ECG trace (darker = signal)
        trace_image = v_channel
        
        if grid_color == 'auto':
            # Auto-detect based on S-channel (saturation)
            # High saturation = colored grid (red/pink)
            s_mean = np.mean(s_channel)
            grid_color = 'red' if s_mean > 100 else 'black'
        
        if grid_color == 'red':
            # Red/pink grid: H-channel in red range (0-10 or 170-180)
            # Create mask for red hues
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            grid_mask = cv2.bitwise_or(mask1, mask2) > 0
        else:
            # Black grid: Low V-channel (dark = grid)
            threshold = 100  # Adjustable
            grid_mask = v_channel < threshold
        
        # Create grid-only image
        grid_image = cv2.bitwise_and(image, image, mask=grid_mask.astype(np.uint8) * 255)
        
        # Create trace-only image (inverse of grid mask)
        trace_mask = ~grid_mask
        trace_only_image = cv2.bitwise_and(image, image, mask=trace_mask.astype(np.uint8) * 255)
        
        return {
            'method': 'hsv',
            'grid_color': grid_color,
            'trace_image': trace_image,  # V-channel (grayscale)
            'grid_mask': grid_mask.astype(np.uint8) * 255,
            'grid_image': grid_image,
            'trace_only_image': trace_only_image,
            'h_channel': h_channel,  # For visualization
            's_channel': s_channel,  # For visualization
            'v_channel': v_channel,  # For visualization
        }


# Convenience functions
def separate_lab(image: np.ndarray, grid_color: str = 'auto') -> Dict:
    """Separate using LAB color space"""
    separator = ColorSeparator(method='lab')
    return separator.separate(image, grid_color)


def separate_hsv(image: np.ndarray, grid_color: str = 'auto') -> Dict:
    """Separate using HSV color space"""
    separator = ColorSeparator(method='hsv')
    return separator.separate(image, grid_color)
