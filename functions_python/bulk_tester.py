"""
Bulk Testing Framework
Test specific functions or processes with multiple images in parallel

Documentation:
- Purpose: Test individual functions or pipeline steps with bulk image sets
- Architecture: Async testing with result tracking and comparison
- What works: Parallel execution, result aggregation, error tracking
- What didn't work: Synchronous testing (too slow), single-threaded approach
- Changes: Added async support, result caching, comparison metrics
"""

import asyncio
import json
import numpy as np
import cv2
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
import logging
from pathlib import Path
import traceback

# GCS integration
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

# Import transformers for testing
try:
    from transformers.edge_detector import EdgeDetector, detect_edges, crop_to_content
    from transformers.color_separation import ColorSeparator
    from transformers.quality_gates import QualityGates
    from transformers.multi_scale_grid_detector import MultiScaleGridDetector
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestResult:
    """Result from a single test execution."""
    
    def __init__(self, test_name: str, image_path: str, success: bool, 
                 result: Any = None, error: str = None, metrics: Dict = None,
                 execution_time: float = 0.0):
        self.test_name = test_name
        self.image_path = image_path
        self.success = success
        self.result = result
        self.error = error
        self.metrics = metrics or {}
        self.execution_time = execution_time
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'test_name': self.test_name,
            'image_path': self.image_path,
            'success': self.success,
            'result': str(self.result) if self.result is not None else None,
            'error': self.error,
            'metrics': self.metrics,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp
        }


class BulkTester:
    """
    Bulk testing framework for ECG processing functions.
    
    Notebook-ready: Yes - can be used in Kaggle notebook
    """
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.results: List[TestResult] = []
        self.gcs_client = None
        
        if GCS_AVAILABLE:
            try:
                self.gcs_client = storage.Client()
            except Exception:
                pass
    
    async def test_function(self, 
                          function: Callable,
                          image_paths: List[str],
                          test_name: str,
                          source: str = 'local',  # 'local', 'gcs'
                          bucket_name: str = None,
                          **kwargs) -> List[TestResult]:
        """
        Test a function with multiple images.
        
        Args:
            function: Function to test (must accept image as first arg)
            image_paths: List of image paths
            test_name: Name for this test
            source: 'local' or 'gcs'
            bucket_name: GCS bucket name if source is 'gcs'
            **kwargs: Additional arguments to pass to function
            
        Returns:
            List of TestResult objects
        """
        logger.info(f"Testing {test_name} with {len(image_paths)} images")
        
        # Create tasks for parallel execution
        tasks = []
        for image_path in image_paths:
            if source == 'gcs':
                task = self._test_gcs_image(function, image_path, test_name, 
                                          bucket_name, **kwargs)
            else:
                task = self._test_local_image(function, image_path, test_name, **kwargs)
            tasks.append(task)
        
        # Execute in parallel (limit concurrency)
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def bounded_task(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(*[bounded_task(task) for task in tasks])
        self.results.extend(results)
        
        return results
    
    async def _test_local_image(self, function: Callable, image_path: str, 
                               test_name: str, **kwargs) -> TestResult:
        """Test function with local image."""
        start_time = datetime.now()
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            # Run function
            if asyncio.iscoroutinefunction(function):
                result = await function(image, **kwargs)
            else:
                result = function(image, **kwargs)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Extract metrics if result is a dict
            metrics = {}
            if isinstance(result, dict):
                metrics = {k: v for k, v in result.items() 
                          if isinstance(v, (int, float, str, bool))}
            
            return TestResult(
                test_name=test_name,
                image_path=image_path,
                success=True,
                result=result,
                metrics=metrics,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestResult(
                test_name=test_name,
                image_path=image_path,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def _test_gcs_image(self, function: Callable, image_path: str,
                            test_name: str, bucket_name: str, **kwargs) -> TestResult:
        """Test function with GCS image."""
        start_time = datetime.now()
        try:
            if not GCS_AVAILABLE or self.gcs_client is None:
                raise ImportError("GCS not available")
            
            # Download image
            bucket = self.gcs_client.bucket(bucket_name)
            blob = bucket.blob(image_path)
            image_data = blob.download_as_bytes()
            
            # Decode image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError(f"Failed to decode image: {image_path}")
            
            # Run function
            if asyncio.iscoroutinefunction(function):
                result = await function(image, **kwargs)
            else:
                result = function(image, **kwargs)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Extract metrics
            metrics = {}
            if isinstance(result, dict):
                metrics = {k: v for k, v in result.items() 
                          if isinstance(v, (int, float, str, bool))}
            
            return TestResult(
                test_name=test_name,
                image_path=image_path,
                success=True,
                result=result,
                metrics=metrics,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestResult(
                test_name=test_name,
                image_path=image_path,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def get_summary(self) -> Dict:
        """Get summary statistics."""
        if not self.results:
            return {'message': 'No results yet'}
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful
        
        # Group by test name
        by_test = {}
        for result in self.results:
            if result.test_name not in by_test:
                by_test[result.test_name] = {'total': 0, 'success': 0, 'failed': 0, 
                                            'avg_time': 0.0}
            by_test[result.test_name]['total'] += 1
            if result.success:
                by_test[result.test_name]['success'] += 1
            else:
                by_test[result.test_name]['failed'] += 1
            by_test[result.test_name]['avg_time'] += result.execution_time
        
        # Calculate averages
        for test_name in by_test:
            count = by_test[test_name]['total']
            by_test[test_name]['avg_time'] /= count if count > 0 else 1
        
        return {
            'total_tests': total,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total if total > 0 else 0,
            'by_test': by_test,
            'total_execution_time': sum(r.execution_time for r in self.results)
        }
    
    def save_results(self, output_path: str):
        """Save results to JSON file."""
        data = {
            'summary': self.get_summary(),
            'results': [r.to_dict() for r in self.results]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
    
    def clear_results(self):
        """Clear all results."""
        self.results = []


# Convenience functions for common tests

async def test_edge_detection(image_paths: List[str], source: str = 'local',
                              bucket_name: str = None) -> List[TestResult]:
    """Test edge detection on multiple images."""
    tester = BulkTester()
    await tester.test_function(
        function=detect_edges,
        image_paths=image_paths,
        test_name='edge_detection',
        source=source,
        bucket_name=bucket_name,
        method='canny'
    )
    return tester.results


async def test_color_separation(image_paths: List[str], method: str = 'lab',
                               source: str = 'local', bucket_name: str = None) -> List[TestResult]:
    """Test color separation on multiple images."""
    tester = BulkTester()
    
    def separate_colors(image):
        separator = ColorSeparator()
        if method == 'hsv':
            return separator.separate_hsv(image)
        else:
            return separator.separate_lab(image)
    
    await tester.test_function(
        function=separate_colors,
        image_paths=image_paths,
        test_name=f'color_separation_{method}',
        source=source,
        bucket_name=bucket_name
    )
    return tester.results


async def test_quality_gates(image_paths: List[str], source: str = 'local',
                            bucket_name: str = None) -> List[TestResult]:
    """Test quality gates on multiple images."""
    tester = BulkTester()
    
    def check_quality(image):
        gates = QualityGates()
        return gates.check_all(image)
    
    await tester.test_function(
        function=check_quality,
        image_paths=image_paths,
        test_name='quality_gates',
        source=source,
        bucket_name=bucket_name
    )
    return tester.results


if __name__ == "__main__":
    # Example usage
    async def main():
        tester = BulkTester(max_workers=10)
        
        # Test edge detection
        image_paths = ['test1.png', 'test2.png']  # Replace with actual paths
        await tester.test_function(
            function=detect_edges,
            image_paths=image_paths,
            test_name='edge_detection',
            method='canny'
        )
        
        # Print summary
        print(json.dumps(tester.get_summary(), indent=2))
        
        # Save results
        tester.save_results('test_results.json')
    
    asyncio.run(main())
