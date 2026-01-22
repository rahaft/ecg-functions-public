"""
ECG Grid Transformation Methods
Multiple transformation approaches for correcting distorted ECG images

New Preprocessing Modules:
- Quality Gates: Pre-flight quality checks
- Color Separation: LAB/HSV color space separation
- Illumination Normalization: CLAHE, background subtraction
- Multi-Scale Grid Detection: 1mm and 5mm grid detection
- FFT Grid Reconstruction: Reconstruct missing grids
- Adaptive Processor: 3-tier fallback pipeline
- Low Contrast Rejection: Final quality check
"""

from .base_transformer import BaseTransformer

# New preprocessing modules
from .quality_gates import QualityGates, check_image_quality
from .color_separation import ColorSeparator, separate_lab, separate_hsv
from .illumination_normalization import (
    IlluminationNormalizer, 
    normalize_clahe, 
    normalize_background_subtract,
    normalize_morphological
)
from .multi_scale_grid_detector import MultiScaleGridDetector
from .fft_grid_reconstruction import FFTGridReconstructor, reconstruct_grid_fft
from .adaptive_processor import AdaptiveProcessor, process_adaptive
from .low_contrast_rejection import LowContrastRejector, reject_low_contrast
from .edge_detector import EdgeDetector, detect_edges, crop_to_content

__all__ = [
    'BaseTransformer',
    # Preprocessing modules
    'QualityGates',
    'check_image_quality',
    'ColorSeparator',
    'separate_lab',
    'separate_hsv',
    'IlluminationNormalizer',
    'normalize_clahe',
    'normalize_background_subtract',
    'normalize_morphological',
    'MultiScaleGridDetector',
    'FFTGridReconstructor',
    'reconstruct_grid_fft',
    'AdaptiveProcessor',
    'process_adaptive',
    'LowContrastRejector',
    'reject_low_contrast',
    # Edge detection
    'EdgeDetector',
    'detect_edges',
    'crop_to_content',
]
