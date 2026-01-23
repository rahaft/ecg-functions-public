"""
Edge Detection Benchmarking Suite
Modular system for comparing edge detection methods for document boundaries and ECG signal extraction
"""

from .preprocessor import PreProcessor
from .edge_benchmarker import EdgeBenchmarker
from .metrics_calculator import MetricsCalculator
from .extraction_engine import ExtractionEngine
from .visualizer import Visualizer

__all__ = [
    'PreProcessor',
    'EdgeBenchmarker',
    'MetricsCalculator',
    'ExtractionEngine',
    'Visualizer'
]
