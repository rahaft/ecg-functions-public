# ============================================================================
# STEP 2: Segmented Processing Module
# ============================================================================
# This file: kaggle_cell_2_segmented_processing.py
# Purpose: Cell 2 code for Kaggle notebook - Segmented Processing
# Usage: Copy entire file into Cell 2 of Kaggle notebook
# Source: functions_python/segmented_processing.py
# ============================================================================

"""
Segmented Processing Module
Processes images in overlapping segments with different parameters per segment
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass


@dataclass
class Segment:
    """Represents an image segment"""
    x_start: int
    x_end: int
    y_start: int
    y_end: int
    overlap_left: int = 0
    overlap_right: int = 0
    overlap_top: int = 0
    overlap_bottom: int = 0
    parameters: Optional[Dict] = None


class SegmentedProcessor:
    """Process images in overlapping segments"""
    
    def __init__(self, overlap_ratio: float = 0.2, min_segment_size: int = 100):
        """
        Initialize segmented processor
        
        Args:
            overlap_ratio: Ratio of segment size to use for overlap (0.0 to 0.5)
            min_segment_size: Minimum segment size in pixels
        """
        self.overlap_ratio = overlap_ratio
        self.min_segment_size = min_segment_size
    
    def create_segments(self, image_shape: Tuple[int, int], 
                       segment_size: Optional[Tuple[int, int]] = None,
                       num_segments: Optional[Tuple[int, int]] = None) -> List[Segment]:
        """
        Create overlapping segments for an image
        
        Args:
            image_shape: (height, width) of image
            segment_size: (height, width) of each segment (if specified)
            num_segments: (num_rows, num_cols) of segments (if specified)
            
        Returns:
            List of Segment objects
        """
        height, width = image_shape
        
        if segment_size is not None:
            seg_height, seg_width = segment_size
            num_rows = max(1, int(np.ceil(height / seg_height)))
            num_cols = max(1, int(np.ceil(width / seg_width)))
        elif num_segments is not None:
            num_rows, num_cols = num_segments
            seg_height = height // num_rows
            seg_width = width // num_cols
        else:
            # Default: divide into 4 segments
            num_rows = 2
            num_cols = 2
            seg_height = height // num_rows
            seg_width = width // num_cols
        
        # Ensure minimum segment size
        seg_height = max(self.min_segment_size, seg_height)
        seg_width = max(self.min_segment_size, seg_width)
        
        # Calculate overlap
        overlap_h = int(seg_height * self.overlap_ratio)
        overlap_w = int(seg_width * self.overlap_ratio)
        
        segments = []
        
        for row in range(num_rows):
            for col in range(num_cols):
                # Calculate segment boundaries
                y_start = row * seg_height
                y_end = min((row + 1) * seg_height, height)
                x_start = col * seg_width
                x_end = min((col + 1) * seg_width, width)
                
                # Calculate overlaps
                overlap_left = overlap_w if col > 0 else 0
                overlap_right = overlap_w if col < num_cols - 1 else 0
                overlap_top = overlap_h if row > 0 else 0
                overlap_bottom = overlap_h if row < num_rows - 1 else 0
                
                # Adjust boundaries to include overlap
                y_start_adj = max(0, y_start - overlap_top)
                y_end_adj = min(height, y_end + overlap_bottom)
                x_start_adj = max(0, x_start - overlap_left)
                x_end_adj = min(width, x_end + overlap_right)
                
                segment = Segment(
                    x_start=x_start_adj,
                    x_end=x_end_adj,
                    y_start=y_start_adj,
                    y_end=y_end_adj,
                    overlap_left=overlap_left if col > 0 else 0,
                    overlap_right=overlap_right if col < num_cols - 1 else 0,
                    overlap_top=overlap_top if row > 0 else 0,
                    overlap_bottom=overlap_bottom if row < num_rows - 1 else 0
                )
                
                segments.append(segment)
        
        return segments
    
    def extract_segment(self, image: np.ndarray, segment: Segment) -> np.ndarray:
        """Extract image region for a segment"""
        return image[segment.y_start:segment.y_end, segment.x_start:segment.x_end]
    
    def process_segmented(self, image: np.ndarray, 
                         process_func: Callable[[np.ndarray, Dict], Dict],
                         segment_parameters: Optional[List[Dict]] = None,
                         segment_size: Optional[Tuple[int, int]] = None,
                         num_segments: Optional[Tuple[int, int]] = None) -> Dict:
        """
        Process image in segments and merge results
        
        Args:
            image: Input image
            process_func: Function to process each segment (image, params) -> result
            segment_parameters: Optional list of parameters for each segment
            segment_size: Size of each segment
            num_segments: Number of segments (rows, cols)
            
        Returns:
            Merged processing results
        """
        segments = self.create_segments(image.shape, segment_size, num_segments)
        
        if segment_parameters is None:
            segment_parameters = [{}] * len(segments)
        elif len(segment_parameters) < len(segments):
            # Extend with default parameters
            segment_parameters.extend([{}] * (len(segments) - len(segment_parameters)))
        
        # Process each segment
        segment_results = []
        for i, segment in enumerate(segments):
            segment_image = self.extract_segment(image, segment)
            params = segment_parameters[i] if i < len(segment_parameters) else {}
            segment.params = params
            
            result = process_func(segment_image, params)
            result['segment'] = segment
            segment_results.append(result)
        
        # Merge results
        merged_result = self._merge_segment_results(segment_results, image.shape)
        
        return merged_result
    
    def _merge_segment_results(self, segment_results: List[Dict], 
                               image_shape: Tuple[int, int]) -> Dict:
        """
        Merge results from multiple segments with weighted blending in overlap zones
        
        Args:
            segment_results: List of results from each segment
            image_shape: (height, width) of full image
            
        Returns:
            Merged result dictionary
        """
        height, width = image_shape
        
        # Initialize merged arrays
        merged_data = {}
        weight_accumulator = {}
        
        for result in segment_results:
            segment = result['segment']
            
            # Process each data field in result
            for key, value in result.items():
                if key == 'segment':
                    continue
                
                if isinstance(value, np.ndarray):
                    # Handle array data
                    if key not in merged_data:
                        merged_data[key] = np.zeros(image_shape, dtype=value.dtype)
                        weight_accumulator[key] = np.zeros(image_shape, dtype=np.float32)
                    
                    # Create weight mask for this segment
                    weights = self._create_segment_weights(
                        segment, image_shape, value.shape
                    )
                    
                    # Map segment coordinates to full image coordinates
                    seg_h, seg_w = value.shape[:2] if len(value.shape) >= 2 else (value.shape[0], 1)
                    
                    # Adjust for actual segment size
                    y_start = segment.y_start
                    y_end = min(segment.y_end, y_start + seg_h)
                    x_start = segment.x_start
                    x_end = min(segment.x_end, x_start + seg_w)
                    
                    # Extract relevant portion
                    seg_y_end = y_end - y_start
                    seg_x_end = x_end - x_start
                    
                    if len(value.shape) == 2:
                        # 2D array
                        seg_data = value[:seg_y_end, :seg_x_end]
                        merged_data[key][y_start:y_end, x_start:x_end] += (
                            seg_data * weights[y_start:y_end, x_start:x_end]
                        )
                        weight_accumulator[key][y_start:y_end, x_start:x_end] += (
                            weights[y_start:y_end, x_start:x_end]
                        )
                    elif len(value.shape) == 1:
                        # 1D array - handle as row or column
                        if seg_h > seg_w:
                            # Column vector - need to match the shape of merged_data slice
                            seg_data = value[:seg_y_end]
                            # Ensure seg_data matches the slice size
                            seg_data = seg_data[:y_end - y_start]
                            # merged_data[key][y_start:y_end, x_start] is 1D, so we add 1D
                            merged_data[key][y_start:y_end, x_start] += (
                                seg_data * weights[y_start:y_end, x_start]
                            )
                            weight_accumulator[key][y_start:y_end, x_start] += (
                                weights[y_start:y_end, x_start]
                            )
                        else:
                            # Row vector
                            seg_data = value[:seg_x_end]
                            seg_data = seg_data[:x_end - x_start]
                            weight_slice = weights[y_start, x_start:x_end]
                            merged_data[key][y_start, x_start:x_end] += (
                                seg_data * weight_slice
                            )
                            weight_accumulator[key][y_start, x_start:x_end] += weight_slice
                elif isinstance(value, (dict, list)):
                    # Handle nested structures - collect all and merge later
                    if key not in merged_data:
                        merged_data[key] = []
                    merged_data[key].append(value)
        
        # Normalize by weights
        for key in merged_data:
            if isinstance(merged_data[key], np.ndarray) and key in weight_accumulator:
                weights = weight_accumulator[key]
                # Avoid division by zero
                weights = np.where(weights > 0, weights, 1.0)
                merged_data[key] = merged_data[key] / weights
        
        return merged_data
    
    def _create_segment_weights(self, segment: Segment, 
                               image_shape: Tuple[int, int],
                               segment_data_shape: Tuple) -> np.ndarray:
        """
        Create weight mask for segment with smooth transitions in overlap zones
        
        Args:
            segment: Segment object
            image_shape: Full image shape
            segment_data_shape: Shape of segment data
            
        Returns:
            Weight array matching image_shape
        """
        height, width = image_shape
        weights = np.ones((height, width), dtype=np.float32)
        
        # Reduce weights in overlap regions
        y_start = segment.y_start
        y_end = segment.y_end
        x_start = segment.x_start
        x_end = segment.x_end
        
        # Top overlap
        if segment.overlap_top > 0:
            overlap_region = weights[y_start:y_start + segment.overlap_top, x_start:x_end]
            fade = np.linspace(0.5, 1.0, segment.overlap_top)
            weights[y_start:y_start + segment.overlap_top, x_start:x_end] = (
                fade[:, np.newaxis] * overlap_region
            )
        
        # Bottom overlap
        if segment.overlap_bottom > 0:
            overlap_region = weights[y_end - segment.overlap_bottom:y_end, x_start:x_end]
            fade = np.linspace(1.0, 0.5, segment.overlap_bottom)
            weights[y_end - segment.overlap_bottom:y_end, x_start:x_end] = (
                fade[:, np.newaxis] * overlap_region
            )
        
        # Left overlap
        if segment.overlap_left > 0:
            overlap_region = weights[y_start:y_end, x_start:x_start + segment.overlap_left]
            fade = np.linspace(0.5, 1.0, segment.overlap_left)
            weights[y_start:y_end, x_start:x_start + segment.overlap_left] = (
                fade[np.newaxis, :] * overlap_region
            )
        
        # Right overlap
        if segment.overlap_right > 0:
            overlap_region = weights[y_start:y_end, x_end - segment.overlap_right:x_end]
            fade = np.linspace(1.0, 0.5, segment.overlap_right)
            weights[y_start:y_end, x_end - segment.overlap_right:x_end] = (
                fade[np.newaxis, :] * overlap_region
            )
        
        # Edge handling: full weight at image boundaries
        if y_start == 0:
            weights[0, :] = 1.0
        if y_end == height:
            weights[-1, :] = 1.0
        if x_start == 0:
            weights[:, 0] = 1.0
        if x_end == width:
            weights[:, -1] = 1.0
        
        return weights
    
    def get_segment_for_point(self, x: int, y: int, segments: List[Segment]) -> Optional[Segment]:
        """
        Get the segment that contains a point, prioritizing non-overlap regions
        
        Args:
            x: X coordinate
            y: Y coordinate
            segments: List of segments
            
        Returns:
            Segment containing the point, or None
        """
        # First, find all segments containing the point
        containing_segments = []
        for seg in segments:
            if (seg.x_start <= x < seg.x_end and 
                seg.y_start <= y < seg.y_end):
                containing_segments.append(seg)
        
        if not containing_segments:
            return None
        
        # If only one segment, return it
        if len(containing_segments) == 1:
            return containing_segments[0]
        
        # If multiple segments (overlap region), prefer the one where
        # the point is NOT in the overlap zone
        for seg in containing_segments:
            # Check if point is in overlap zones
            in_left_overlap = (seg.overlap_left > 0 and 
                             seg.x_start <= x < seg.x_start + seg.overlap_left)
            in_right_overlap = (seg.overlap_right > 0 and 
                              seg.x_end - seg.overlap_right <= x < seg.x_end)
            in_top_overlap = (seg.overlap_top > 0 and 
                            seg.y_start <= y < seg.y_start + seg.overlap_top)
            in_bottom_overlap = (seg.overlap_bottom > 0 and 
                               seg.y_end - seg.overlap_bottom <= y < seg.y_end)
            
            # If not in any overlap zone, prefer this segment
            if not (in_left_overlap or in_right_overlap or in_top_overlap or in_bottom_overlap):
                return seg
        
        # If all are in overlap, return the first one
        return containing_segments[0]

# ============================================================================
# STEP 2: Segmented Processing Module
# ============================================================================
# This file: kaggle_cell_2_segmented_processing.py
# Purpose: Cell 2 code for Kaggle notebook - Segmented Processing
# Usage: Copy entire file into Cell 2 of Kaggle notebook
# Source: functions_python/segmented_processing.py
# ============================================================================
