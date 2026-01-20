"""
Base Transformer Class
Abstract base class for all grid transformation methods
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
import numpy as np
import cv2


class BaseTransformer(ABC):
    """
    Base class for all grid transformation methods.
    All transformers must implement these methods.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.params = {}
        self.metrics = {}
        
    @abstractmethod
    def detect_grid(self, image: np.ndarray) -> Dict:
        """
        Detect grid lines and intersections in the image.
        
        Args:
            image: Input ECG image (numpy array)
            
        Returns:
            Dictionary with:
            - horizontal_lines: List of horizontal line coordinates
            - vertical_lines: List of vertical line coordinates
            - intersections: List of intersection points
        """
        pass
    
    @abstractmethod
    def estimate_transformation(self, grid_data: Dict) -> Dict:
        """
        Estimate transformation parameters from grid data.
        
        Args:
            grid_data: Output from detect_grid()
            
        Returns:
            Dictionary with transformation parameters
        """
        pass
    
    @abstractmethod
    def apply_transformation(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """
        Apply transformation to image.
        
        Args:
            image: Input image
            params: Transformation parameters from estimate_transformation()
            
        Returns:
            Transformed image
        """
        pass
    
    @abstractmethod
    def calculate_quality(self, original_grid: Dict, transformed_grid: Dict) -> Dict:
        """
        Calculate quality metrics for the transformation.
        
        Args:
            original_grid: Grid data from original image
            transformed_grid: Grid data from transformed image
            
        Returns:
            Dictionary with quality metrics (R², RMSE, MAE, etc.)
        """
        pass
    
    def transform(self, image: np.ndarray) -> Dict:
        """
        Complete transformation pipeline.
        
        Args:
            image: Input ECG image
            
        Returns:
            Dictionary with:
            - transformed_image: Corrected image
            - params: Transformation parameters
            - metrics: Quality metrics
            - grid_data: Detected grid information
        """
        # Step 1: Detect grid
        grid_data = self.detect_grid(image)
        
        # Step 2: Estimate transformation
        params = self.estimate_transformation(grid_data)
        self.params = params
        
        # Step 3: Apply transformation
        transformed = self.apply_transformation(image, params)
        
        # Step 4: Detect grid in transformed image
        transformed_grid = self.detect_grid(transformed)
        
        # Step 5: Calculate quality
        metrics = self.calculate_quality(grid_data, transformed_grid)
        self.metrics = metrics
        
        return {
            'transformed_image': transformed,
            'params': params,
            'metrics': metrics,
            'grid_data': grid_data,
            'transformed_grid': transformed_grid,
            'method': self.name
        }
