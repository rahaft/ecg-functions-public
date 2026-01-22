"""
WebSocket Server for Parallel ECG Image Processing
Handles multiple concurrent image processing requests via WebSocket connections

Documentation:
- Purpose: Enable parallel processing of multiple ECG images simultaneously
- Architecture: WebSocket server with worker pool (10+ concurrent connections)
- What works: Async processing with asyncio, connection pooling
- What didn't work: Thread-based approach (GIL limitations), synchronous processing
- Changes: Migrated to asyncio for better concurrency, added connection limits
"""

import asyncio
import json
import base64
import numpy as np
import cv2
from io import BytesIO
from PIL import Image
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# WebSocket server
try:
    import websockets
    from websockets.server import serve
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("Warning: websockets library not available. Install with: pip install websockets")

# Import processing modules
try:
    from transformers.edge_detector import EdgeDetector, detect_edges, crop_to_content
    from transformers.color_separation import ColorSeparator
    from transformers.multi_scale_grid_detector import MultiScaleGridDetector
    from transformers.quality_gates import QualityGates
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    print(f"Warning: Transformers not available: {e}")

# GCS integration
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("Warning: GCS not available. Install with: pip install google-cloud-storage")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessingWorker:
    """
    Worker for processing individual images.
    Notebook-ready: Yes - can be used in Kaggle notebook with async support
    """
    
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.busy = False
        
    async def process_image(self, image_data: bytes, options: Dict) -> Dict:
        """
        Process a single ECG image.
        
        Args:
            image_data: Image bytes
            options: Processing options (edge_detection, color_separation, etc.)
            
        Returns:
            Dictionary with processing results
        """
        self.busy = True
        try:
            # Decode image
            image = self._decode_image(image_data)
            
            results = {
                'worker_id': self.worker_id,
                'timestamp': datetime.now().isoformat(),
                'steps': {}
            }
            
            # Edge detection
            if options.get('edge_detection', False):
                edge_result = await self._detect_edges(image)
                results['steps']['edge_detection'] = edge_result
                if options.get('crop_to_content', False):
                    image = edge_result.get('cropped_image', image)
            
            # Color separation
            if options.get('color_separation', False):
                color_result = await self._separate_colors(image, options.get('color_method', 'lab'))
                results['steps']['color_separation'] = color_result
                if color_result.get('trace_image') is not None:
                    image = color_result['trace_image']
            
            # Grid detection
            if options.get('grid_detection', False):
                grid_result = await self._detect_grid(image)
                results['steps']['grid_detection'] = grid_result
            
            # Quality check
            if options.get('quality_check', False):
                quality_result = await self._check_quality(image)
                results['steps']['quality_check'] = quality_result
            
            results['success'] = True
            return results
            
        except Exception as e:
            logger.error(f"Worker {self.worker_id} error: {str(e)}")
            return {
                'worker_id': self.worker_id,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        finally:
            self.busy = False
    
    def _decode_image(self, image_data: bytes) -> np.ndarray:
        """Decode image from bytes."""
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Failed to decode image")
        return image
    
    async def _detect_edges(self, image: np.ndarray) -> Dict:
        """Detect edges in image."""
        if not TRANSFORMERS_AVAILABLE:
            return {'error': 'Edge detector not available'}
        
        detector = EdgeDetector(method='canny')
        grid_data = detector.detect_grid(image)
        x, y, w, h = grid_data['bounding_box']
        
        # Crop if requested
        cropped = crop_to_content(image, padding=10)
        
        return {
            'bounding_box': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
            'edge_pixels': int(grid_data['edge_pixels']),
            'contour_count': int(grid_data['edge_count']),
            'cropped_image': cropped if cropped is not None else None
        }
    
    async def _separate_colors(self, image: np.ndarray, method: str = 'lab') -> Dict:
        """Separate ECG trace from grid."""
        if not TRANSFORMERS_AVAILABLE:
            return {'error': 'Color separator not available'}
        
        separator = ColorSeparator()
        if method == 'hsv':
            trace, grid_mask = separator.separate_hsv(image)
        else:
            trace, grid_mask = separator.separate_lab(image)
        
        return {
            'method': method,
            'trace_pixels': int(np.sum(trace > 0)) if trace is not None else 0,
            'grid_pixels': int(np.sum(grid_mask > 0)) if grid_mask is not None else 0,
            'trace_image': trace
        }
    
    async def _detect_grid(self, image: np.ndarray) -> Dict:
        """Detect grid lines."""
        if not TRANSFORMERS_AVAILABLE:
            return {'error': 'Grid detector not available'}
        
        detector = MultiScaleGridDetector()
        result = detector.detect(image)
        
        return {
            'fine_lines': int(result.get('fine_lines', 0)),
            'bold_lines': int(result.get('bold_lines', 0)),
            'quality_score': float(result.get('quality_score', 0))
        }
    
    async def _check_quality(self, image: np.ndarray) -> Dict:
        """Check image quality."""
        if not TRANSFORMERS_AVAILABLE:
            return {'error': 'Quality gates not available'}
        
        gates = QualityGates()
        result = gates.check_all(image)
        
        return {
            'passed': result.get('passed', False),
            'blur_score': float(result.get('blur', {}).get('score', 0)),
            'dpi': float(result.get('resolution', {}).get('estimated_dpi', 0)),
            'warnings': result.get('warnings', [])
        }


class WebSocketProcessingServer:
    """
    WebSocket server for parallel image processing.
    Supports 10+ concurrent connections for parallel processing.
    
    Notebook-ready: Yes - can run in Kaggle notebook with asyncio
    """
    
    def __init__(self, max_workers: int = 10, port: int = 8765):
        self.max_workers = max_workers
        self.port = port
        self.workers = [ProcessingWorker(i) for i in range(max_workers)]
        self.active_connections = set()
        self.gcs_client = None
        
        if GCS_AVAILABLE:
            try:
                self.gcs_client = storage.Client()
            except Exception as e:
                logger.warning(f"GCS client initialization failed: {e}")
    
    async def handle_connection(self, websocket, path):
        """Handle a new WebSocket connection."""
        self.active_connections.add(websocket)
        logger.info(f"New connection. Total connections: {len(self.active_connections)}")
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed")
        finally:
            self.active_connections.remove(websocket)
    
    async def handle_message(self, websocket, message: str):
        """Handle incoming message."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'process_image':
                await self.process_single_image(websocket, data)
            elif message_type == 'process_batch':
                await self.process_batch(websocket, data)
            elif message_type == 'process_gcs_batch':
                await self.process_gcs_batch(websocket, data)
            else:
                await websocket.send(json.dumps({
                    'error': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({'error': 'Invalid JSON'}))
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await websocket.send(json.dumps({'error': str(e)}))
    
    async def process_single_image(self, websocket, data: Dict):
        """Process a single image."""
        image_data = base64.b64decode(data.get('image', ''))
        options = data.get('options', {})
        
        # Find available worker
        worker = await self.get_available_worker()
        if worker is None:
            await websocket.send(json.dumps({
                'error': 'No available workers'
            }))
            return
        
        result = await worker.process_image(image_data, options)
        await websocket.send(json.dumps(result))
    
    async def process_batch(self, websocket, data: Dict):
        """Process multiple images in parallel."""
        images = data.get('images', [])
        options = data.get('options', {})
        
        if len(images) > self.max_workers:
            await websocket.send(json.dumps({
                'error': f'Too many images. Maximum: {self.max_workers}'
            }))
            return
        
        # Process all images in parallel
        tasks = []
        for i, image_data_b64 in enumerate(images):
            image_data = base64.b64decode(image_data_b64)
            worker = self.workers[i % len(self.workers)]
            task = worker.process_image(image_data, options)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        await websocket.send(json.dumps({
            'type': 'batch_result',
            'results': results,
            'count': len(results)
        }))
    
    async def process_gcs_batch(self, websocket, data: Dict):
        """Process batch of images from Google Cloud Storage."""
        if not GCS_AVAILABLE or self.gcs_client is None:
            await websocket.send(json.dumps({
                'error': 'GCS not available'
            }))
            return
        
        bucket_name = data.get('bucket_name')
        image_paths = data.get('image_paths', [])
        options = data.get('options', {})
        
        if len(image_paths) > self.max_workers:
            await websocket.send(json.dumps({
                'error': f'Too many images. Maximum: {self.max_workers}'
            }))
            return
        
        # Download and process in parallel
        tasks = []
        bucket = self.gcs_client.bucket(bucket_name)
        
        for i, image_path in enumerate(image_paths):
            task = self.process_gcs_image(bucket, image_path, options, i)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        await websocket.send(json.dumps({
            'type': 'gcs_batch_result',
            'results': results,
            'count': len(results)
        }))
    
    async def process_gcs_image(self, bucket, image_path: str, options: Dict, worker_idx: int) -> Dict:
        """Download and process a single GCS image."""
        try:
            blob = bucket.blob(image_path)
            image_data = blob.download_as_bytes()
            
            worker = self.workers[worker_idx % len(self.workers)]
            result = await worker.process_image(image_data, options)
            result['image_path'] = image_path
            return result
        except Exception as e:
            return {
                'image_path': image_path,
                'success': False,
                'error': str(e)
            }
    
    async def get_available_worker(self) -> Optional[ProcessingWorker]:
        """Get an available worker."""
        for worker in self.workers:
            if not worker.busy:
                return worker
        return None
    
    async def start(self):
        """Start the WebSocket server."""
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets library required. Install with: pip install websockets")
        
        logger.info(f"Starting WebSocket server on port {self.port}")
        async with serve(self.handle_connection, "localhost", self.port):
            await asyncio.Future()  # Run forever


async def main():
    """Main entry point."""
    server = WebSocketProcessingServer(max_workers=10, port=8765)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
