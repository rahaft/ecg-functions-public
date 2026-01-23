"""
ECG Image Digitization Pipeline
Core processing modules for converting ECG images to time-series data

This can be deployed as:
1. Python Cloud Function (using functions-framework)
2. Docker container on Cloud Run
3. Local processing with Firebase Admin SDK
"""

print("=" * 70)
print("STEP 4: Loading digitization_pipeline.py")
print("=" * 70)
print("File: functions_python/digitization_pipeline.py")
print("Status: Starting...")

import numpy as np
import cv2
from scipy import signal
from scipy.ndimage import gaussian_filter1d, median_filter
from typing import Dict, List, Tuple, Optional
import json

# STEP 4: KAGGLE_CELL_4_READY_TO_PASTE.py

# Import classes from previous cells (they're in global namespace, not modules)
# Try to get from global namespace first (from previous cells)
# Then fall back to module import (if files were uploaded)

print("\n[Step 4.1] Loading GridDetector...")
try:
    # First try: Get from global namespace (Cell 1)
    if 'GridDetector' in globals():
        GridDetector = globals()['GridDetector']
        print("  ✓ Success: Loaded GridDetector from Cell 1 (grid_detection.py)")
    else:
        # Second try: Import as module (if file was uploaded)
        from grid_detection import GridDetector
        print("  ✓ Success: Imported GridDetector from grid_detection module")
except Exception as e:
    print(f"  ✗ ERROR: Could not load GridDetector: {e}")
    print("  → Make sure Cell 1 (grid_detection.py) ran successfully!")
    print("  → Check that you see 'STEP 1: ... SUCCESS' message from Cell 1")
    raise

print("\n[Step 4.2] Loading SegmentedProcessor...")
try:
    if 'SegmentedProcessor' in globals():
        SegmentedProcessor = globals()['SegmentedProcessor']
        print("  ✓ Success: Loaded SegmentedProcessor from Cell 2 (segmented_processing.py)")
    else:
        from segmented_processing import SegmentedProcessor
        print("  ✓ Success: Imported SegmentedProcessor from segmented_processing module")
except Exception as e:
    print(f"  ✗ ERROR: Could not load SegmentedProcessor: {e}")
    print("  → Make sure Cell 2 (segmented_processing.py) ran successfully!")
    print("  → Check that you see 'STEP 2: ... SUCCESS' message from Cell 2")
    raise

print("\n[Step 4.3] Loading LineVisualizer...")
try:
    if 'LineVisualizer' in globals():
        LineVisualizer = globals()['LineVisualizer']
        print("  ✓ Success: Loaded LineVisualizer from Cell 3 (line_visualization.py)")
    else:
        from line_visualization import LineVisualizer
        print("  ✓ Success: Imported LineVisualizer from line_visualization module")
except Exception as e:
    print(f"  ✗ ERROR: Could not load LineVisualizer: {e}")
    print("  → Make sure Cell 3 (line_visualization.py) ran successfully!")
    print("  → Check that you see 'STEP 3: ... SUCCESS' message from Cell 3")
    raise

# STEP 4: KAGGLE_CELL_4_READY_TO_PASTE.py

print("\n" + "=" * 70)
print("STEP 4: All dependencies loaded successfully!")
print("File: functions_python/digitization_pipeline.py")
print("Status: Loading ECGDigitizer class...")
print("=" * 70)


class ECGDigitizer:
    """Main class for ECG image digitization"""
    
    def __init__(self, use_segmented_processing: bool = True, 
                 enable_visualization: bool = False):
        self.lead_names = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
        self.sampling_rate = 500  # Hz
        self.grid_spacing_mm = 1.0  # mm per small square
        self.voltage_scale = 0.1  # mV per mm (standard ECG)
        self.time_scale = 0.04  # seconds per mm (25 mm/s standard)
        
        # Initialize new modules
        self.grid_detector = GridDetector(max_polynomial_degree=3)
        self.segmented_processor = SegmentedProcessor(overlap_ratio=0.2) if use_segmented_processing else None
        self.visualizer = LineVisualizer() if enable_visualization else None
        self.use_segmented = use_segmented_processing
        
    def process_image(self, image_path: str) -> Dict:
        """
        Main processing pipeline
        
        Args:
            image_path: Path to ECG image file
            
        Returns:
            Dictionary containing extracted time-series data and metadata
        """
        # Step 1: Load and preprocess image
        image = self.load_image(image_path)
        preprocessed = self.preprocess_image(image)
        
        # Step 2: Detect grid and calibrate (using enhanced grid detection)
        grid_info = self.detect_grid(preprocessed)
        self.last_grid_info = grid_info  # Store for quality assessment
        
        # Visualize if enabled
        if self.visualizer:
            self.visualizer.visualize_grid_lines(image, grid_info, 
                                                filename=f"grid_{image_path.split('/')[-1]}")
        
        calibration = self.calibrate_scales(grid_info)
        
        # Step 3: Detect and extract leads
        lead_regions = self.detect_leads(preprocessed, grid_info)
        
        # STEP 4: KAGGLE_CELL_4_READY_TO_PASTE.py
        
        # Step 4: Extract signals from each lead
        signals = {}
        for lead_name, region in lead_regions.items():
            signal_data = self.extract_signal(region, calibration)
            signals[lead_name] = signal_data
            
        # Step 5: Post-process signals
        processed_signals = self.post_process_signals(signals)
        
        # Step 6: Calculate quality metrics
        quality = self.calculate_quality_metrics(processed_signals)
        
        return {
            'leads': processed_signals,
            'metadata': {
                'sampling_rate': self.sampling_rate,
                'calibration': calibration,
                'quality': quality
            }
        }
    
    def load_image(self, image_path: str) -> np.ndarray:
        """Load and convert image to grayscale"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        return gray
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image: denoise, enhance contrast, correct rotation
        """
        # 1. Denoise
        denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        
        # 2. Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 3. Detect and correct rotation
        rotated = self.correct_rotation(enhanced)
        
        # STEP 4: KAGGLE_CELL_4_READY_TO_PASTE.py
        
        # 4. Binarize (threshold)
        _, binary = cv2.threshold(rotated, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def correct_rotation(self, image: np.ndarray) -> np.ndarray:
        """Detect and correct image rotation using Hough line detection"""
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is None:
            return image
        
        # Calculate dominant angle
        angles = []
        for line in lines[:20]:  # Use top 20 lines
            rho, theta = line[0]
            angle = np.degrees(theta) - 90
            if abs(angle) < 45:  # Only consider small rotations
                angles.append(angle)
        
        if not angles:
            return image
        
        # Use median angle to avoid outliers
        rotation_angle = np.median(angles)
        
        # STEP 4: KAGGLE_CELL_4_READY_TO_PASTE.py
        
        # Rotate image
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), 
                                 flags=cv2.INTER_CUBIC,
                                 borderMode=cv2.BORDER_REPLICATE)
        
        return rotated
    
    def detect_grid(self, image: np.ndarray) -> Dict:
        """
        Detect ECG grid lines using enhanced polynomial grid detection
        
        Args:
            image: Preprocessed binary image
            
        Returns:
            Dictionary containing grid information
        """
        if self.use_segmented and self.segmented_processor:
            # Use segmented processing for grid detection
            def process_segment(seg_image, params):
                return self.grid_detector.detect_grid(seg_image)
            
            # Process in segments and merge
            segment_results = self.segmented_processor.process_segmented(
                image, process_segment
            )
            
            # Merge grid information from segments
            # For now, use the first segment's result (can be enhanced)
            if segment_results and 'horizontal_lines' in segment_results:
                grid_info = {
                    'horizontal_lines': segment_results.get('horizontal_lines', []),
                    'vertical_lines': segment_results.get('vertical_lines', []),
                    'intersections': segment_results.get('intersections', []),
                    'horizontal_spacing': segment_results.get('horizontal_spacing', 10.0),
                    'vertical_spacing': segment_results.get('vertical_spacing', 10.0),
                    'image_shape': image.shape
                }
            else:
                # Fallback to non-segmented detection
                grid_info = self.grid_detector.detect_grid(image)
        else:
            # Use standard grid detection
            grid_info = self.grid_detector.detect_grid(image)
        
        return grid_info
    
    # STEP 4: KAGGLE_CELL_4_READY_TO_PASTE.py
    
    def calibrate_scales(self, grid_info: Dict) -> Dict:
        """
        Calibrate voltage and time scales based on grid intersections
        
        Standard ECG:
        - Small square: 1mm x 1mm
        - Large square: 5mm x 5mm
        - Voltage: 1mm = 0.1 mV
        - Time: 1mm = 0.04s (at 25mm/s)
        """
        # Use intersection-based calibration if available
        if 'intersections' in grid_info and len(grid_info['intersections']) > 1:
            # Calculate spacing from intersections
            intersections = grid_info['intersections']
            
            # Safely extract coordinates from intersections
            # Handle both dict and list formats
            try:
                y_coords = []
                x_coords = []
                
                for item in intersections:
                    if isinstance(item, dict):
                        # Dictionary format: {'x': ..., 'y': ...}
                        # Handle nested dicts or direct values
                        x_val = item.get('x')
                        y_val = item.get('y')
                        
                        # If values are dicts, try to extract numeric values
                        if isinstance(x_val, dict):
                            # Try common keys
                            x_val = x_val.get('value') or x_val.get('coord') or x_val.get('x')
                        if isinstance(y_val, dict):
                            y_val = y_val.get('value') or y_val.get('coord') or y_val.get('y')
                        
                        # Convert to float if possible
                        try:
                            if x_val is not None and y_val is not None:
                                x_coords.append(float(x_val))
                                y_coords.append(float(y_val))
                        except (ValueError, TypeError):
                            continue  # Skip this intersection if conversion fails
                    elif isinstance(item, (list, tuple)) and len(item) >= 2:
                        # List/tuple format: [x, y] or (x, y)
                        try:
                            x_coords.append(float(item[0]))
                            y_coords.append(float(item[1]))
                        except (ValueError, TypeError):
                            continue  # Skip this intersection if conversion fails
                
                # Group intersections by approximate grid position
                # For horizontal spacing, look at y-coordinates
                if len(y_coords) > 1:
                    y_coords = sorted(y_coords)
                    v_spacings = np.diff(y_coords)
                    v_spacing = float(np.median(v_spacings[v_spacings > 0]))
                else:
                    v_spacing = grid_info.get('vertical_spacing', 10.0)
                
                # For vertical spacing, look at x-coordinates
                if len(x_coords) > 1:
                    x_coords = sorted(x_coords)
                    h_spacings = np.diff(x_coords)
                    h_spacing = float(np.median(h_spacings[h_spacings > 0]))
                else:
                    h_spacing = grid_info.get('horizontal_spacing', 10.0)
            except (KeyError, IndexError, TypeError, ValueError) as e:
                # Fallback to spacing-based calibration if intersection parsing fails
                print(f"Warning: Could not parse intersections: {e}. Using spacing-based calibration.")
                h_spacing = grid_info.get('horizontal_spacing', 10.0)
                v_spacing = grid_info.get('vertical_spacing', 10.0)
        else:
            # Fallback to spacing-based calibration
            h_spacing = grid_info.get('horizontal_spacing', 10.0)
            v_spacing = grid_info.get('vertical_spacing', 10.0)
        
        # Assume spacing is for small squares (1mm)
        pixels_per_mm_x = h_spacing
        pixels_per_mm_y = v_spacing
        
        # Calculate scale factors
        pixels_per_mv = pixels_per_mm_y / self.voltage_scale
        pixels_per_sec = pixels_per_mm_x / self.time_scale
        
        return {
            'pixels_per_mv': pixels_per_mv,
            'pixels_per_sec': pixels_per_sec,
            'pixels_per_mm_x': pixels_per_mm_x,
            'pixels_per_mm_y': pixels_per_mm_y,
            'grid_spacing_h': h_spacing,
            'grid_spacing_v': v_spacing
        }
    
    # STEP 4: KAGGLE_CELL_4_READY_TO_PASTE.py
    
    def detect_leads(self, image: np.ndarray, grid_info: Dict) -> Dict[str, np.ndarray]:
        """
        Detect the 12 lead regions in the ECG image
        
        Standard 12-lead layout:
        - Usually arranged in 3-4 columns
        - Each lead typically 2.5 seconds long
        """
        height, width = image.shape
        
        # Standard layout: 3 columns x 4 rows + 1 long rhythm strip
        # This is a simplified detection - actual implementation should be more robust
        
        lead_regions = {}
        
        # Divide into approximate regions (this needs to be improved with actual detection)
        col_width = width // 3
        row_height = height // 5
        
        lead_positions = [
            ('I', 0, 0), ('aVR', 1, 0), ('V1', 2, 0),
            ('II', 0, 1), ('aVL', 1, 1), ('V2', 2, 1),
            ('III', 0, 2), ('aVF', 1, 2), ('V3', 2, 2),
            ('V4', 0, 3), ('V5', 1, 3), ('V6', 2, 3),
        ]
        
        for lead_name, col, row in lead_positions:
            x1 = col * col_width
            x2 = (col + 1) * col_width
            y1 = row * row_height
            y2 = (row + 1) * row_height
            
            region = image[y1:y2, x1:x2]
            lead_regions[lead_name] = region
        
        return lead_regions
    
    # STEP 4: KAGGLE_CELL_4_READY_TO_PASTE.py
    
    def extract_signal(self, region: np.ndarray, calibration: Dict) -> np.ndarray:
        """
        Extract time-series signal from a lead region
        Uses grid intersections for alignment if available
        
        Method: For each column (time point), find the darkest pixels (signal path)
        """
        height, width = region.shape
        signal_values = []
        
        # Use segmented processing if enabled and region is large enough
        if self.use_segmented and self.segmented_processor and width > 200:
            def extract_segment_signal(seg_image, params):
                seg_h, seg_w = seg_image.shape
                seg_signal = []
                
                for col in range(seg_w):
                    column = seg_image[:, col]
                    
                    # Find signal position
                    if np.mean(column) > 128:
                        column = 255 - column
                    
                    threshold = np.max(column) * 0.5
                    dark_pixels = column > threshold
                    
                    if np.any(dark_pixels):
                        positions = np.where(dark_pixels)[0]
                        weights = column[dark_pixels]
                        center = np.average(positions, weights=weights)
                    else:
                        center = seg_h / 2
                    
                    voltage_pixels = seg_h / 2 - center
                    voltage_mv = voltage_pixels / calibration['pixels_per_mv']
                    seg_signal.append(voltage_mv)
                
                return {'signal': np.array(seg_signal)}
            
            result = self.segmented_processor.process_segmented(
                region, extract_segment_signal, num_segments=(1, max(1, width // 150))
            )
            
            if 'signal' in result:
                signal_array = result['signal']
            else:
                # Fallback to standard extraction
                signal_array = self._extract_signal_standard(region, calibration)
        else:
            signal_array = self._extract_signal_standard(region, calibration)
        
        # STEP 4: KAGGLE_CELL_4_READY_TO_PASTE.py
        
        # Resample to standard sampling rate (500 Hz)
        duration_sec = width / calibration['pixels_per_sec']
        target_samples = int(duration_sec * self.sampling_rate)
        
        if len(signal_array) > 1:
            resampled = signal.resample(signal_array, target_samples)
        else:
            resampled = signal_array
        
        return resampled
    
    def _extract_signal_standard(self, region: np.ndarray, calibration: Dict) -> np.ndarray:
        """
        FEATURE 2.1: Standard signal extraction with adaptive thresholding
        """
        height, width = region.shape
        signal_values = []
        
        # FEATURE 2.1: Pre-calculate image statistics for adaptive thresholding
        region_mean = np.mean(region)
        region_std = np.std(region)
        
        for col in range(width):
            column = region[:, col]
            
            # Find signal position (darkest pixels)
            if np.mean(column) > 128:  # Light background
                column = 255 - column
            
            # FEATURE 2.1: Adaptive threshold per column
            # Use local statistics instead of fixed 50% of max
            col_max = np.max(column)
            col_mean = np.mean(column)
            col_std = np.std(column)
            
            # Adaptive threshold: use percentile or statistical method
            if col_std > 10:  # Has variation
                # Use percentile-based threshold (top 25% darkest)
                threshold = np.percentile(column, 75)
            else:
                # Low variation - use mean-based
                threshold = col_mean + col_std
            
            # Ensure threshold is reasonable
            threshold = max(threshold, col_max * 0.3)  # At least 30% of max
            threshold = min(threshold, col_max * 0.8)  # At most 80% of max
            
            dark_pixels = column > threshold
            
            if np.any(dark_pixels):
                positions = np.where(dark_pixels)[0]
                weights = column[dark_pixels]
                center = np.average(positions, weights=weights)
            else:
                # FEATURE 2.1: Better fallback - use previous value or median
                if len(signal_values) > 0:
                    # Use previous signal value converted back to pixel position
                    prev_voltage = signal_values[-1]
                    center = height / 2 - (prev_voltage * calibration['pixels_per_mv'])
                    center = np.clip(center, 0, height - 1)
                else:
                    center = height / 2  # Default to middle
            
            # Convert pixel position to voltage
            voltage_pixels = height / 2 - center
            voltage_mv = voltage_pixels / calibration['pixels_per_mv']
            
            signal_values.append(voltage_mv)
        
        return np.array(signal_values)
    
    def post_process_signals(self, signals: Dict[str, np.ndarray]) -> List[Dict]:
        """
        Post-process extracted signals:
        - Remove baseline wander
        - Filter noise
        - Align signals
        """
        processed = []
        
        for lead_name, sig in signals.items():
            # 1. Remove baseline wander (high-pass filter at 0.5 Hz)
            sos = signal.butter(3, 0.5, btype='high', fs=self.sampling_rate, output='sos')
            sig_highpass = signal.sosfilt(sos, sig)
            
            # 2. Remove high-frequency noise (low-pass filter at 100 Hz)
            sos = signal.butter(3, 100, btype='low', fs=self.sampling_rate, output='sos')
            sig_filtered = signal.sosfilt(sos, sig_highpass)
            
            # 3. Remove powerline interference (50/60 Hz notch filter)
            for freq in [50, 60]:
                b, a = signal.iirnotch(freq, 30, self.sampling_rate)
                sig_filtered = signal.filtfilt(b, a, sig_filtered)
            
            # STEP 4: KAGGLE_CELL_4_READY_TO_PASTE.py
            
            processed.append({
                'name': lead_name,
                'values': sig_filtered.tolist(),
                'sampling_rate': self.sampling_rate,
                'duration': len(sig_filtered) / self.sampling_rate
            })
        
        return processed
    
    # STEP 4: KAGGLE_CELL_4_READY_TO_PASTE.py
    
    def calculate_quality_metrics(self, processed_signals: List[Dict]) -> Dict:
        """Calculate signal quality metrics"""
        snr_values = []
        
        for lead_data in processed_signals:
            sig = np.array(lead_data['values'])
            
            # Estimate SNR (simplified)
            signal_power = np.mean(sig ** 2)
            
            # Estimate noise from high-frequency components
            sos = signal.butter(3, [40, 100], btype='band', fs=self.sampling_rate, output='sos')
            noise = signal.sosfilt(sos, sig)
            noise_power = np.mean(noise ** 2)
            
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
            else:
                snr = 60  # Very high SNR
            
            snr_values.append(snr)
        
        return {
            'mean_snr': float(np.mean(snr_values)),
            'min_snr': float(np.min(snr_values)),
            'lead_snrs': {lead['name']: snr for lead, snr in zip(processed_signals, snr_values)}
        }


def process_ecg_for_firebase(image_bytes: bytes) -> Dict:
    """
    Wrapper function for Firebase Cloud Function
    
    Args:
        image_bytes: Image file as bytes
        
    Returns:
        Processed ECG data as dictionary
    """
    import tempfile
    import os
    
    # Save bytes to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        tmp_file.write(image_bytes)
        tmp_path = tmp_file.name
    
    try:
        digitizer = ECGDigitizer()
        result = digitizer.process_image(tmp_path)
        return result
    finally:
        os.unlink(tmp_path)

# STEP 4: KAGGLE_CELL_4_READY_TO_PASTE.py

print("\n" + "=" * 70)
print("STEP 4: digitization_pipeline.py loaded successfully!")
print("File: functions_python/digitization_pipeline.py")
print("Status: ✓ SUCCESS")
print("Class: ECGDigitizer is now available")
print("=" * 70)

# ============================================================================
# FILE IDENTIFICATION
# ============================================================================
# This file: kaggle_cell_4_ready_to_paste.py
# Source: KAGGLE_CELL_4_READY_TO_PASTE.py
# Purpose: Complete Cell 4 code for Kaggle notebook with fixed imports
# Usage: Copy entire file into Cell 4 of Kaggle notebook
# ============================================================================
