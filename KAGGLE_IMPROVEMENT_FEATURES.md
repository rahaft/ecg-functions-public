# Kaggle Improvement Features - Step-by-Step Implementation

This document organizes improvements into specific features that can be implemented independently.

---

## 🎯 Feature 1: Enhanced Grid Detection & Validation

**Priority:** ⭐⭐⭐ High  
**Impact:** Affects all downstream processing  
**Files to Modify:** `grid_detection.py`, `digitization_pipeline.py`

### **Step 1.1: Add Grid Regularity Validation**

**Location:** `grid_detection.py` → `GridDetector.detect_grid()`

**Implementation:**
```python
def detect_grid(self, image: np.ndarray) -> Dict:
    # ... existing code ...
    
    # NEW: Validate grid regularity
    grid_quality = self._validate_grid_regularity(
        horizontal_lines, vertical_lines, intersections
    )
    
    return {
        'horizontal_lines': horizontal_lines,
        'vertical_lines': vertical_lines,
        'intersections': intersections,
        'horizontal_spacing': h_spacing,
        'vertical_spacing': v_spacing,
        'image_shape': image.shape,
        'grid_quality': grid_quality  # NEW
    }

def _validate_grid_regularity(self, h_lines, v_lines, intersections):
    """Validate that grid is regular and well-formed"""
    quality = {
        'is_regular': True,
        'spacing_variance': 0.0,
        'missing_lines': 0,
        'warnings': []
    }
    
    # Check spacing consistency
    if len(h_lines) > 1:
        h_positions = sorted([line['function'](line['domain'][0] + line['domain'][1] / 2) 
                             for line in h_lines])
        h_spacings = np.diff(h_positions)
        quality['spacing_variance'] = float(np.var(h_spacings))
        
        if quality['spacing_variance'] > 100:  # Threshold
            quality['is_regular'] = False
            quality['warnings'].append("High horizontal spacing variance")
    
    # Similar for vertical lines
    if len(v_lines) > 1:
        v_positions = sorted([line['function'](line['domain'][0] + line['domain'][1] / 2) 
                             for line in v_lines])
        v_spacings = np.diff(v_positions)
        v_variance = float(np.var(v_spacings))
        
        if v_variance > quality['spacing_variance']:
            quality['spacing_variance'] = v_variance
        
        if v_variance > 100:
            quality['is_regular'] = False
            quality['warnings'].append("High vertical spacing variance")
    
    # Check for expected number of intersections
    expected_intersections = len(h_lines) * len(v_lines)
    if len(intersections) < expected_intersections * 0.5:
        quality['warnings'].append(f"Missing intersections: {len(intersections)}/{expected_intersections}")
    
    return quality
```

**Testing:**
- Test with regular grids (should pass)
- Test with distorted grids (should flag warnings)
- Verify quality metrics are reasonable

---

### **Step 1.2: Improve Grid Spacing Calculation**

**Location:** `grid_detection.py` → `_calculate_grid_spacing()`

**Implementation:**
```python
def _calculate_grid_spacing(self, lines: List[Dict], dimension_size: int) -> float:
    """Calculate average grid spacing with outlier rejection"""
    if len(lines) < 2:
        return 10.0
    
    # Extract positions
    positions = []
    for line in lines:
        if line['orientation'] == 'horizontal':
            x_mid = (line['domain'][0] + line['domain'][1]) / 2
            y_mid = line['function'](x_mid)
            positions.append(y_mid)
        else:
            y_mid = (line['domain'][0] + line['domain'][1]) / 2
            x_mid = line['function'](y_mid)
            positions.append(x_mid)
    
    positions = sorted(positions)
    
    if len(positions) < 2:
        return 10.0
    
    # Calculate all spacings
    spacings = np.diff(positions)
    
    # NEW: Use multiple methods for robustness
    # Method 1: Median of valid spacings (existing)
    median_spacing = np.median(spacings)
    valid_spacings = spacings[np.abs(spacings - median_spacing) < median_spacing * 0.5]
    
    # Method 2: Mode-based (most common spacing)
    if len(spacings) > 5:
        # Bin spacings and find mode
        bins = np.linspace(spacings.min(), spacings.max(), 20)
        hist, bin_edges = np.histogram(spacings, bins=bins)
        mode_bin = np.argmax(hist)
        mode_spacing = (bin_edges[mode_bin] + bin_edges[mode_bin + 1]) / 2
        
        # Use mode if it's close to median, otherwise use median
        if abs(mode_spacing - median_spacing) < median_spacing * 0.2:
            return float(mode_spacing)
    
    # Return median of valid spacings
    if len(valid_spacings) > 0:
        return float(np.median(valid_spacings))
    
    return 10.0
```

**Testing:**
- Test with regular grids
- Test with noisy/dirty grids
- Compare spacing accuracy

---

### **Step 1.3: Add Adaptive Line Detection Thresholds**

**Location:** `grid_detection.py` → `_detect_lines_hough()`

**Implementation:**
```python
def _detect_lines_hough(self, image: np.ndarray) -> Tuple[List, List]:
    """Detect lines using Hough Transform with adaptive thresholds"""
    
    # NEW: Adaptive edge detection based on image characteristics
    image_mean = np.mean(image)
    image_std = np.std(image)
    
    # Adjust Canny thresholds based on image contrast
    if image_std < 30:  # Low contrast
        low_threshold = 30
        high_threshold = 100
    elif image_std > 80:  # High contrast
        low_threshold = 80
        high_threshold = 200
    else:  # Normal contrast
        low_threshold = 50
        high_threshold = 150
    
    edges = cv2.Canny(image, low_threshold, high_threshold, apertureSize=3)
    
    # NEW: Adaptive Hough parameters
    # Adjust threshold based on image size
    hough_threshold = max(50, int(min(image.shape) * 0.1))
    min_line_length = max(30, int(min(image.shape) * 0.05))
    
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 
                            threshold=hough_threshold,
                            minLineLength=min_line_length, 
                            maxLineGap=10)
    
    # ... rest of existing code ...
```

**Testing:**
- Test with low-contrast images
- Test with high-contrast images
- Verify more lines detected

---

## 🎯 Feature 2: Robust Signal Extraction

**Priority:** ⭐⭐⭐ High  
**Impact:** Directly affects score  
**Files to Modify:** `digitization_pipeline.py`

### **Step 2.1: Add Adaptive Signal Path Detection**

**Location:** `digitization_pipeline.py` → `extract_signal()` / `_extract_signal_standard()`

**Implementation:**
```python
def _extract_signal_standard(self, region: np.ndarray, calibration: Dict) -> np.ndarray:
    """Standard signal extraction with adaptive thresholding"""
    height, width = region.shape
    signal_values = []
    
    # NEW: Pre-calculate image statistics for adaptive thresholding
    region_mean = np.mean(region)
    region_std = np.std(region)
    
    for col in range(width):
        column = region[:, col]
        
        # Invert if light background
        if np.mean(column) > 128:
            column = 255 - column
        
        # NEW: Adaptive threshold per column
        # Use local statistics instead of global max
        col_max = np.max(column)
        col_mean = np.mean(column)
        col_std = np.std(column)
        
        # Adaptive threshold: use percentile or statistical method
        if col_std > 10:  # Has variation
            # Use percentile-based threshold
            threshold = np.percentile(column, 75)  # Top 25% darkest
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
            # NEW: Better fallback - use previous value or median
            if len(signal_values) > 0:
                # Use previous signal value converted back to pixel position
                prev_voltage = signal_values[-1]
                center = height / 2 - (prev_voltage * calibration['pixels_per_mv'])
                center = np.clip(center, 0, height - 1)
            else:
                center = height / 2
        
        voltage_pixels = height / 2 - center
        voltage_mv = voltage_pixels / calibration['pixels_per_mv']
        signal_values.append(voltage_mv)
    
    return np.array(signal_values)
```

**Testing:**
- Test with noisy signals
- Test with low-contrast regions
- Verify signal continuity

---

### **Step 2.2: Add Signal Smoothing & Noise Reduction**

**Location:** `digitization_pipeline.py` → `extract_signal()`

**Implementation:**
```python
def extract_signal(self, region: np.ndarray, calibration: Dict) -> np.ndarray:
    """Extract time-series signal with smoothing"""
    # ... existing segmented/standard extraction ...
    
    signal_array = # ... existing code ...
    
    # NEW: Apply median filter to remove outliers
    if len(signal_array) > 3:
        # Small median filter to remove spikes
        signal_array = scipy.ndimage.median_filter(signal_array, size=3)
    
    # NEW: Apply Gaussian smoothing (light)
    if len(signal_array) > 5:
        signal_array = scipy.ndimage.gaussian_filter1d(signal_array, sigma=0.5)
    
    # Resample to standard sampling rate (existing code)
    # ... rest of existing code ...
```

**Testing:**
- Test with noisy signals
- Verify signal shape preserved
- Check amplitude accuracy

---

### **Step 2.3: Add Signal Continuity Validation**

**Location:** `digitization_pipeline.py` → `extract_signal()`

**Implementation:**
```python
def extract_signal(self, region: np.ndarray, calibration: Dict) -> np.ndarray:
    """Extract signal with continuity checks"""
    # ... existing extraction code ...
    
    signal_array = # ... extracted signal ...
    
    # NEW: Validate signal continuity
    if len(signal_array) > 1:
        # Check for sudden jumps (likely errors)
        diffs = np.abs(np.diff(signal_array))
        median_diff = np.median(diffs)
        mad = np.median(np.abs(diffs - median_diff))  # Median Absolute Deviation
        
        # Flag outliers (jumps > 3 * MAD)
        outlier_threshold = median_diff + 3 * mad
        outliers = np.where(diffs > outlier_threshold)[0]
        
        if len(outliers) > len(signal_array) * 0.1:  # More than 10% outliers
            # Apply more aggressive smoothing
            signal_array = scipy.ndimage.gaussian_filter1d(signal_array, sigma=1.0)
        
        # Interpolate over detected outliers
        if len(outliers) > 0 and len(outliers) < len(signal_array) * 0.2:
            for idx in outliers:
                if idx > 0 and idx < len(signal_array) - 1:
                    # Interpolate from neighbors
                    signal_array[idx] = (signal_array[idx-1] + signal_array[idx+1]) / 2
    
    # ... rest of existing code ...
```

**Testing:**
- Test with signals containing jumps
- Verify outliers are corrected
- Check signal quality

---

## 🎯 Feature 3: Improved Lead Detection

**Priority:** ⭐⭐ Medium  
**Impact:** Missing leads = zeros in submission  
**Files to Modify:** `digitization_pipeline.py`

### **Step 3.1: Add Template-Based Lead Detection**

**Location:** `digitization_pipeline.py` → `detect_leads()`

**Implementation:**
```python
def detect_leads(self, image: np.ndarray, grid_info: Dict) -> Dict[str, np.ndarray]:
    """Detect leads with improved layout detection"""
    height, width = image.shape
    
    # NEW: Detect actual layout (3-column, 4-column, etc.)
    layout_type = self._detect_layout_type(image, grid_info)
    
    # NEW: Use grid to find lead boundaries more accurately
    h_lines = grid_info.get('horizontal_lines', [])
    v_lines = grid_info.get('vertical_lines', [])
    
    if len(h_lines) >= 4 and len(v_lines) >= 3:
        # Use grid lines to define regions
        lead_regions = self._detect_leads_from_grid(image, h_lines, v_lines)
    else:
        # Fallback to simple division
        lead_regions = self._detect_leads_simple(image)
    
    # NEW: Validate all 12 leads are found
    required_leads = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
    missing_leads = [lead for lead in required_leads if lead not in lead_regions]
    
    if missing_leads:
        print(f"Warning: Missing leads: {missing_leads}")
        # Try to fill missing leads with estimated regions
        lead_regions = self._fill_missing_leads(lead_regions, image, missing_leads)
    
    return lead_regions

def _detect_layout_type(self, image, grid_info):
    """Detect ECG layout type (3-column, 4-column, etc.)"""
    # Analyze grid structure
    h_lines = grid_info.get('horizontal_lines', [])
    v_lines = grid_info.get('vertical_lines', [])
    
    # Count major divisions
    if len(v_lines) >= 3:
        return '3_column'
    elif len(v_lines) >= 4:
        return '4_column'
    else:
        return 'unknown'

def _detect_leads_from_grid(self, image, h_lines, v_lines):
    """Use grid lines to accurately detect lead regions"""
    lead_regions = {}
    height, width = image.shape
    
    # Get line positions
    h_positions = sorted([line['function'](line['domain'][0] + line['domain'][1] / 2) 
                         for line in h_lines])
    v_positions = sorted([line['function'](line['domain'][0] + line['domain'][1] / 2) 
                         for line in v_lines])
    
    # Standard 12-lead layout: 3 columns x 4 rows
    lead_positions = [
        ('I', 0, 0), ('aVR', 1, 0), ('V1', 2, 0),
        ('II', 0, 1), ('aVL', 1, 1), ('V2', 2, 1),
        ('III', 0, 2), ('aVF', 1, 2), ('V3', 2, 2),
        ('V4', 0, 3), ('V5', 1, 3), ('V6', 2, 3),
    ]
    
    # Calculate row/column boundaries from grid
    if len(h_positions) >= 5:
        row_boundaries = h_positions[:5]  # First 5 horizontal lines
    else:
        row_height = height // 5
        row_boundaries = [i * row_height for i in range(5)]
    
    if len(v_positions) >= 4:
        col_boundaries = v_positions[:4]  # First 4 vertical lines
    else:
        col_width = width // 3
        col_boundaries = [i * col_width for i in range(4)]
    
    # Extract regions based on grid
    for lead_name, col_idx, row_idx in lead_positions:
        if col_idx < len(col_boundaries) - 1 and row_idx < len(row_boundaries) - 1:
            x1 = int(col_boundaries[col_idx])
            x2 = int(col_boundaries[col_idx + 1])
            y1 = int(row_boundaries[row_idx])
            y2 = int(row_boundaries[row_idx + 1])
            
            # Ensure within bounds
            x1 = max(0, x1)
            x2 = min(width, x2)
            y1 = max(0, y1)
            y2 = min(height, y2)
            
            if x2 > x1 and y2 > y1:
                lead_regions[lead_name] = image[y1:y2, x1:x2]
    
    return lead_regions

def _fill_missing_leads(self, lead_regions, image, missing_leads):
    """Fill missing leads with estimated regions"""
    # Use average size of existing leads
    if lead_regions:
        avg_height = int(np.mean([r.shape[0] for r in lead_regions.values()]))
        avg_width = int(np.mean([r.shape[1] for r in lead_regions.values()]))
    else:
        avg_height = image.shape[0] // 5
        avg_width = image.shape[1] // 3
    
    # Simple fallback: divide image into grid
    for lead_name in missing_leads:
        # Use a default region (will be filled with zeros in submission)
        lead_regions[lead_name] = np.zeros((avg_height, avg_width), dtype=image.dtype)
    
    return lead_regions
```

**Testing:**
- Test with standard layouts
- Test with non-standard layouts
- Verify all 12 leads detected

---

## 🎯 Feature 4: Enhanced Calibration

**Priority:** ⭐⭐ Medium  
**Impact:** Affects all voltage measurements  
**Files to Modify:** `digitization_pipeline.py`

### **Step 4.1: Add Scale Detection from Image**

**Location:** `digitization_pipeline.py` → `calibrate_scales()`

**Implementation:**
```python
def calibrate_scales(self, grid_info: Dict) -> Dict:
    """Calibrate with scale detection from image"""
    # ... existing intersection-based calibration ...
    
    # NEW: Try to detect actual scale from image if available
    # (Some ECG images have scale markers)
    detected_scale = self._detect_scale_from_image(grid_info)
    
    if detected_scale:
        # Use detected scale if available
        pixels_per_mm_x = detected_scale['pixels_per_mm_x']
        pixels_per_mm_y = detected_scale['pixels_per_mm_y']
    else:
        # Use grid-based calibration (existing)
        pixels_per_mm_x = h_spacing
        pixels_per_mm_y = v_spacing
    
    # NEW: Validate calibration values are reasonable
    # Standard ECG: 1mm = 0.1mV, so pixels_per_mv should be ~10 * pixels_per_mm
    pixels_per_mv = pixels_per_mm_y / self.voltage_scale
    
    # Check if calibration seems reasonable
    if pixels_per_mv < 1 or pixels_per_mv > 1000:
        print(f"Warning: Unusual calibration: {pixels_per_mv:.2f} pixels/mV")
        # Fallback to default
        pixels_per_mv = 10.0 / self.voltage_scale  # Assume 10 pixels/mm
    
    # Similar validation for time scale
    pixels_per_sec = pixels_per_mm_x / self.time_scale
    if pixels_per_sec < 1 or pixels_per_sec > 1000:
        print(f"Warning: Unusual time calibration: {pixels_per_sec:.2f} pixels/sec")
        pixels_per_sec = 10.0 / self.time_scale  # Assume 10 pixels/mm
    
    return {
        'pixels_per_mv': pixels_per_mv,
        'pixels_per_sec': pixels_per_sec,
        'pixels_per_mm_x': pixels_per_mm_x,
        'pixels_per_mm_y': pixels_per_mm_y,
        'grid_spacing_h': h_spacing,
        'grid_spacing_v': v_spacing,
        'calibration_validated': True  # NEW
    }

def _detect_scale_from_image(self, grid_info):
    """Try to detect scale markers in image (if present)"""
    # This is a placeholder - actual implementation would:
    # 1. Look for scale markers (e.g., "1mV" text or markers)
    # 2. Measure distance between markers
    # 3. Calculate actual scale
    
    # For now, return None to use grid-based calibration
    return None
```

**Testing:**
- Test with standard grids
- Test with non-standard scales
- Verify calibration values are reasonable

---

### **Step 4.2: Add Calibration Validation**

**Location:** `digitization_pipeline.py` → `calibrate_scales()`

**Implementation:**
```python
def _validate_calibration(self, calibration: Dict, image_shape: Tuple) -> Dict:
    """Validate calibration values are reasonable"""
    warnings = []
    
    # Check voltage scale
    pixels_per_mv = calibration['pixels_per_mv']
    if pixels_per_mv < 5:
        warnings.append(f"Very small voltage scale: {pixels_per_mv:.2f} pixels/mV")
    elif pixels_per_mv > 200:
        warnings.append(f"Very large voltage scale: {pixels_per_mv:.2f} pixels/mV")
    
    # Check time scale
    pixels_per_sec = calibration['pixels_per_sec']
    if pixels_per_sec < 5:
        warnings.append(f"Very small time scale: {pixels_per_sec:.2f} pixels/sec")
    elif pixels_per_sec > 200:
        warnings.append(f"Very large time scale: {pixels_per_sec:.2f} pixels/sec")
    
    # Check consistency
    if abs(pixels_per_mv / pixels_per_sec - 0.1 / 0.04) > 0.5:
        warnings.append("Voltage and time scales seem inconsistent")
    
    calibration['warnings'] = warnings
    calibration['is_valid'] = len(warnings) == 0
    
    return calibration
```

**Testing:**
- Test with various calibration values
- Verify warnings are appropriate
- Check validation accuracy

---

## 🎯 Feature 5: Advanced Post-Processing

**Priority:** ⭐⭐ Medium  
**Impact:** Improves signal quality  
**Files to Modify:** `digitization_pipeline.py`

### **Step 5.1: Add Adaptive Filtering**

**Location:** `digitization_pipeline.py` → `post_process_signals()`

**Implementation:**
```python
def post_process_signals(self, signals: Dict[str, np.ndarray]) -> List[Dict]:
    """Post-process with adaptive filtering"""
    processed = []
    
    for lead_name, sig in signals.items():
        # NEW: Calculate signal quality before filtering
        initial_snr = self._estimate_snr(sig)
        
        # 1. Remove baseline wander (existing)
        sos = signal.butter(3, 0.5, btype='high', fs=self.sampling_rate, output='sos')
        sig_highpass = signal.sosfilt(sos, sig)
        
        # NEW: Adaptive low-pass filter based on signal quality
        if initial_snr < 10:  # Low SNR - more aggressive filtering
            cutoff = 40  # Lower cutoff for noisy signals
        elif initial_snr > 30:  # High SNR - preserve more detail
            cutoff = 100  # Higher cutoff
        else:
            cutoff = 100  # Standard
        
        sos = signal.butter(3, cutoff, btype='low', fs=self.sampling_rate, output='sos')
        sig_filtered = signal.sosfilt(sos, sig_highpass)
        
        # 3. Remove powerline interference (existing)
        for freq in [50, 60]:
            b, a = signal.iirnotch(freq, 30, self.sampling_rate)
            sig_filtered = signal.filtfilt(b, a, sig_filtered)
        
        # NEW: Validate filtering improved SNR
        final_snr = self._estimate_snr(sig_filtered)
        
        processed.append({
            'name': lead_name,
            'values': sig_filtered.tolist(),
            'sampling_rate': self.sampling_rate,
            'duration': len(sig_filtered) / self.sampling_rate,
            'snr_improvement': final_snr - initial_snr  # NEW
        })
    
    return processed

def _estimate_snr(self, signal: np.ndarray) -> float:
    """Estimate signal-to-noise ratio"""
    if len(signal) < 10:
        return 0.0
    
    # Simple SNR estimation
    signal_power = np.mean(signal ** 2)
    
    # Estimate noise from high-frequency components
    if len(signal) > 20:
        # High-pass filter to get noise
        sos = signal.butter(3, 40, btype='high', fs=self.sampling_rate, output='sos')
        noise = signal.sosfilt(sos, signal)
        noise_power = np.mean(noise ** 2)
    else:
        noise_power = np.var(signal) * 0.1  # Rough estimate
    
    if noise_power > 0:
        snr_db = 10 * np.log10(signal_power / noise_power)
    else:
        snr_db = 60  # Very high SNR
    
    return float(snr_db)
```

**Testing:**
- Test with noisy signals
- Test with clean signals
- Verify SNR improvement

---

### **Step 5.2: Add Signal Amplitude Preservation**

**Location:** `digitization_pipeline.py` → `post_process_signals()`

**Implementation:**
```python
def post_process_signals(self, signals: Dict[str, np.ndarray]) -> List[Dict]:
    """Post-process with amplitude preservation"""
    processed = []
    
    for lead_name, sig in signals.items():
        # Store original amplitude range
        original_range = np.max(sig) - np.min(sig)
        original_mean = np.mean(sig)
        
        # Apply filters (existing code)
        # ... filtering steps ...
        
        # NEW: Preserve amplitude range
        filtered_range = np.max(sig_filtered) - np.min(sig_filtered)
        if filtered_range > 0 and original_range > 0:
            # Scale to preserve original range
            scale_factor = original_range / filtered_range
            sig_filtered = sig_filtered * scale_factor
        
        # NEW: Preserve DC offset (baseline)
        filtered_mean = np.mean(sig_filtered)
        sig_filtered = sig_filtered - filtered_mean + original_mean
        
        processed.append({
            'name': lead_name,
            'values': sig_filtered.tolist(),
            # ... rest ...
        })
    
    return processed
```

**Testing:**
- Test amplitude preservation
- Verify signal shape unchanged
- Check calibration accuracy

---

## 🎯 Feature 6: Error Handling & Validation

**Priority:** ⭐ Low  
**Impact:** Prevents bad submissions  
**Files to Modify:** `digitization_pipeline.py`, `kaggle_cell_5_complete.py`

### **Step 6.1: Add Signal Range Validation**

**Location:** `kaggle_cell_5_complete.py` → `process_image()`

**Implementation:**
```python
def process_image(image_path: Path) -> dict:
    """Process a single ECG image with validation"""
    # ... existing code ...
    
    signals = {}
    for lead_data in result.get('leads', []):
        lead_name = lead_data['name']
        if lead_name not in LEAD_NAMES:
            continue
        
        signal = np.array(lead_data['values'])
        
        # ... existing 2D flattening code ...
        
        # NEW: Validate signal range
        signal_min = np.min(signal)
        signal_max = np.max(signal)
        signal_range = signal_max - signal_min
        
        # ECG signals should be in reasonable range (typically -5 to +5 mV)
        if signal_range > 20:  # Unusually large range
            print(f"  ⚠️  Warning: {lead_name} has large range: {signal_range:.2f} mV")
            # Clip to reasonable range
            signal = np.clip(signal, -10, 10)
        elif signal_range < 0.01:  # Very small range (likely noise or zero)
            print(f"  ⚠️  Warning: {lead_name} has very small range: {signal_range:.2f} mV")
            # Keep as is (might be flat line)
        
        # NEW: Check for NaN or Inf
        if np.any(np.isnan(signal)) or np.any(np.isinf(signal)):
            print(f"  ⚠️  Warning: {lead_name} contains NaN/Inf, replacing with zeros")
            signal = np.nan_to_num(signal, nan=0.0, posinf=0.0, neginf=0.0)
        
        # ... rest of existing padding/truncation code ...
```

**Testing:**
- Test with out-of-range signals
- Test with NaN/Inf values
- Verify validation works

---

### **Step 6.2: Add Processing Quality Metrics**

**Location:** `digitization_pipeline.py` → `calculate_quality_metrics()`

**Implementation:**
```python
def calculate_quality_metrics(self, processed_signals: List[Dict]) -> Dict:
    """Calculate comprehensive quality metrics"""
    snr_values = []
    lead_counts = []
    signal_ranges = []
    
    for lead_data in processed_signals:
        sig = np.array(lead_data['values'])
        
        # Existing SNR calculation
        # ... existing code ...
        snr_values.append(snr)
        
        # NEW: Additional metrics
        signal_range = np.max(sig) - np.min(sig)
        signal_ranges.append(signal_range)
        
        # Check if signal is mostly zeros
        non_zero_ratio = np.count_nonzero(sig) / len(sig)
        lead_counts.append(non_zero_ratio)
    
    return {
        'mean_snr': float(np.mean(snr_values)),
        'min_snr': float(np.min(snr_values)),
        'lead_snrs': {lead['name']: snr for lead, snr in zip(processed_signals, snr_values)},
        # NEW metrics
        'mean_signal_range': float(np.mean(signal_ranges)),
        'leads_with_signal': sum(1 for ratio in lead_counts if ratio > 0.1),
        'quality_score': float(np.mean(snr_values)) * (sum(1 for ratio in lead_counts if ratio > 0.1) / 12)
    }
```

**Testing:**
- Test with various signal qualities
- Verify metrics are reasonable
- Check quality score accuracy

---

## 📋 Implementation Priority Order

### **Week 1: Critical Fixes**
1. ✅ Feature 2.1: Adaptive Signal Path Detection
2. ✅ Feature 2.2: Signal Smoothing
3. ✅ Feature 6.1: Signal Range Validation

### **Week 2: Core Improvements**
4. ✅ Feature 1.2: Improved Grid Spacing
5. ✅ Feature 3.1: Improved Lead Detection
6. ✅ Feature 2.3: Signal Continuity Validation

### **Week 3: Optimization**
7. ✅ Feature 1.1: Grid Regularity Validation
8. ✅ Feature 4.1: Scale Detection
9. ✅ Feature 5.1: Adaptive Filtering

### **Week 4: Polish**
10. ✅ Feature 1.3: Adaptive Line Detection
11. ✅ Feature 4.2: Calibration Validation
12. ✅ Feature 5.2: Amplitude Preservation
13. ✅ Feature 6.2: Quality Metrics

---

## 🧪 Testing Strategy

For each feature:
1. **Unit Test**: Test the new function in isolation
2. **Integration Test**: Test with full pipeline
3. **Validation Test**: Compare before/after on sample images
4. **Kaggle Test**: Submit and compare scores

---

## 📝 Notes

- **Start Small**: Implement one feature at a time
- **Test Thoroughly**: Each feature should improve score or robustness
- **Keep It Simple**: Don't over-engineer
- **Monitor Impact**: Track score changes after each feature

---

**Ready to start implementing? Pick Feature 2.1 (Adaptive Signal Path Detection) first - it has the highest impact!**
