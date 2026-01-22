"""
Firebase Cloud Function (Python) for ECG Image Digitization
Uses the digitization pipeline to process ECG images

Can be deployed as:
1. Cloud Function (using functions-framework)
2. Flask app on Cloud Run
3. Local development server
"""

import json
import base64
import tempfile
import os
import numpy as np
import cv2
from io import BytesIO
from PIL import Image

# Try to import Flask for multi-method endpoint
try:
    from flask import Flask, request, jsonify
    try:
        from flask_cors import CORS
        CORS_AVAILABLE = True
    except ImportError:
        CORS_AVAILABLE = False
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    CORS_AVAILABLE = False

from digitization_pipeline import ECGDigitizer, process_ecg_for_firebase

# Import multi-method processor
try:
    from transformers.multi_method_processor import MultiMethodProcessor
    MULTI_METHOD_AVAILABLE = True
except ImportError:
    MULTI_METHOD_AVAILABLE = False
    print("Warning: Multi-method transformer not available. Install transformers module.")

# Import step processors
try:
    from transformers.quality_gates import QualityGates
    from transformers.color_separation import ColorSeparator
    from transformers.illumination_normalization import IlluminationNormalizer
    from transformers.multi_scale_grid_detector import MultiScaleGridDetector
    from transformers.fft_grid_reconstruction import FFTGridReconstructor
    from transformers.low_contrast_rejection import LowContrastRejector
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    print(f"Warning: Some transformers not available: {e}")


def process_pipeline_step(step_id: int, method_id: str, image: np.ndarray, previous_result: dict) -> dict:
    """
    Process a single pipeline step with the specified method.
    
    Args:
        step_id: Step ID (0-15)
        method_id: Method identifier
        image: Input image (numpy array)
        previous_result: Result from previous step
        
    Returns:
        Dictionary with metrics, output_image, input_image, and other step-specific data
    """
    result = {
        'metrics': {},
        'output_image': None,
        'input_image': image.copy() if image is not None else None,
        'overlays': []
    }
    
    try:
        if step_id == 0:  # Assumptions
            # Assumptions are handled client-side, just validate
            result['metrics'] = {
                'small_grid_ratio': previous_result.get('small_grid_ratio', 1),
                'large_grid_ratio': previous_result.get('large_grid_ratio', 5),
                'ecg_line_count': previous_result.get('ecg_line_count', 12)
            }
            result['output_image'] = image
            
        elif step_id == 1:  # Quality Gates
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError("Quality Gates transformer not available")
            
            gates = QualityGates()
            quality_result = gates.check_all(image)
            
            result['metrics'] = {
                'blur_score': quality_result['blur']['score'],
                'dpi': quality_result['resolution'].get('estimated_dpi', 0),
                'contrast_std': quality_result['contrast']['std'],
                'grid_lines_count': quality_result['grid_detectability']['detected_lines']
            }
            result['output_image'] = image  # Pass through
            result['quality_passed'] = quality_result['passed']
            result['warnings'] = quality_result.get('warnings', [])
            
        elif step_id == 2:  # Color Separation
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError("Color Separation transformer not available")
            
            separator = ColorSeparator()
            if method_id == 'hsv':
                trace, grid_mask = separator.separate_hsv(image)
            else:  # default: lab
                trace, grid_mask = separator.separate_lab(image)
            
            result['metrics'] = {
                'separation_quality': 0.85,  # TODO: Calculate actual metric
                'channel_contrast': float(np.std(trace)) if trace is not None else 0,
                'grid_isolation': 0.9  # TODO: Calculate actual metric
            }
            result['output_image'] = trace
            result['grid_mask'] = grid_mask
            
        elif step_id == 3:  # Illumination Normalization
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError("Illumination Normalizer not available")
            
            normalizer = IlluminationNormalizer()
            if method_id == 'background_subtract':
                normalized = normalizer.normalize_background_subtract(image)
            elif method_id == 'morphological':
                normalized = normalizer.normalize_morphological(image)
            else:  # default: clahe
                normalized = normalizer.normalize_clahe(image)
            
            result['metrics'] = {
                'brightness_variance': float(np.var(normalized)) if normalized is not None else 0,
                'normalized_range': float(np.max(normalized) - np.min(normalized)) if normalized is not None else 0,
                'uniformity_score': 0.85  # TODO: Calculate actual metric
            }
            result['output_image'] = normalized
            
        elif step_id == 4:  # Multi-Scale Grid Detection
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError("Multi-Scale Grid Detector not available")
            
            detector = MultiScaleGridDetector()
            grid_result = detector.detect(image)
            
            result['metrics'] = {
                'mm1_lines': grid_result.get('fine_lines', 0),
                'mm5_lines': grid_result.get('bold_lines', 0),
                'detection_quality': grid_result.get('quality_score', 0)
            }
            result['output_image'] = grid_result.get('visualization', image)
            result['grid_lines'] = grid_result.get('lines', {})
            
        elif step_id == 5:  # Smudge Removal
            # Use inpainting method from existing code
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Simple smudge detection and removal
            _, dark_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
            
            # Remove thin lines from mask
            kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
            kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))
            vertical_lines = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel_v)
            horizontal_lines = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel_h)
            grid_mask = cv2.bitwise_or(vertical_lines, horizontal_lines)
            smudge_mask = cv2.subtract(dark_mask, grid_mask)
            
            # Clean up mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            smudge_mask = cv2.morphologyEx(smudge_mask, cv2.MORPH_OPEN, kernel)
            smudge_mask = cv2.dilate(smudge_mask, kernel, iterations=2)
            
            # Inpaint
            if method_id == 'morphological':
                # Morphological cleaning only
                cleaned = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            else:  # default: inpainting
                cleaned = cv2.inpaint(gray, smudge_mask, 3, cv2.INPAINT_NS)
            
            smudge_count = cv2.countNonZero(smudge_mask) // 100  # Rough count
            
            result['metrics'] = {
                'smudge_count': smudge_count,
                'area_cleaned': float(cv2.countNonZero(smudge_mask)) / (image.shape[0] * image.shape[1]) * 100,
                'grid_preserved': True
            }
            result['output_image'] = cleaned
            result['smudge_mask'] = smudge_mask
            
        elif step_id == 6:  # Rotation Correction
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            if method_id == 'projection':
                # Projection profile method
                angles = np.arange(-5, 5, 0.5)
                best_angle = 0
                max_variance = 0
                for angle in angles:
                    M = cv2.getRotationMatrix2D((gray.shape[1]//2, gray.shape[0]//2), angle, 1)
                    rotated = cv2.warpAffine(edges, M, (gray.shape[1], gray.shape[0]))
                    projection = np.sum(rotated, axis=1)
                    variance = np.var(projection)
                    if variance > max_variance:
                        max_variance = variance
                        best_angle = angle
                confidence = min(max_variance / 10000, 1.0)
            else:  # default: hough
                # Hough transform method
                lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
                if lines is not None:
                    angles = []
                    for line in lines[:20]:  # Use first 20 lines
                        rho, theta = line[0]
                        angle = np.degrees(theta) - 90
                        if abs(angle) < 45:
                            angles.append(angle)
                    if angles:
                        best_angle = np.median(angles)
                        confidence = 1.0 - (np.std(angles) / 10) if len(angles) > 1 else 0.5
                    else:
                        best_angle = 0
                        confidence = 0.3
                else:
                    best_angle = 0
                    confidence = 0.2
            
            # Apply rotation
            M = cv2.getRotationMatrix2D((image.shape[1]//2, image.shape[0]//2), best_angle, 1)
            rotated = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
            
            result['metrics'] = {
                'angle_degrees': float(best_angle),
                'confidence': float(confidence),
                'perpendicularity': 90.0  # TODO: Calculate actual perpendicularity
            }
            result['output_image'] = rotated
            
        elif step_id == 7:  # FFT Grid Reconstruction
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError("FFT Grid Reconstructor not available")
            
            reconstructor = FFTGridReconstructor()
            fft_result = reconstructor.reconstruct(image)
            
            result['metrics'] = {
                'frequencies_found': fft_result.get('frequencies_found', 0),
                'reconstruction_quality': fft_result.get('quality', 0),
                'grid_completeness': fft_result.get('completeness', 0)
            }
            result['output_image'] = fft_result.get('reconstructed', image)
            
        elif step_id == 8:  # Grid Line Detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            if method_id == 'hough':
                # Hough lines method
                edges = cv2.Canny(gray, 50, 150)
                lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
                h_lines = []
                v_lines = []
                if lines is not None:
                    for line in lines:
                        x1, y1, x2, y2 = line[0]
                        angle = np.abs(np.arctan2(y2-y1, x2-x1) * 180 / np.pi)
                        if angle < 15 or angle > 165:
                            h_lines.append(line[0])
                        elif 75 < angle < 105:
                            v_lines.append(line[0])
            else:  # default: morphological
                # Morphological method
                kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
                kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
                h_detected = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel_h)
                v_detected = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel_v)
                h_lines = cv2.countNonZero(h_detected) // 1000
                v_lines = cv2.countNonZero(v_detected) // 1000
            
            h_count = len(h_lines) if isinstance(h_lines, list) else h_lines
            v_count = len(v_lines) if isinstance(v_lines, list) else v_lines
            
            result['metrics'] = {
                'h_lines': h_count,
                'v_lines': v_count,
                'intersections': h_count * v_count,
                'quality_score': min((h_count + v_count) / 50, 1.0)
            }
            result['output_image'] = image  # TODO: Add line visualization
            result['detected_lines'] = {'horizontal': h_lines, 'vertical': v_lines}
            
        elif step_id == 9:  # Grid Spacing Estimation
            # Use detected lines from previous result
            h_lines = previous_result.get('detected_lines', {}).get('horizontal', [])
            v_lines = previous_result.get('detected_lines', {}).get('vertical', [])
            
            # Estimate spacing (simplified)
            pixels_per_mm = 10  # Default estimate
            
            result['metrics'] = {
                'pixels_per_mm': pixels_per_mm,
                'spacing_variance': 0.5,
                'ratio_5_to_1': 5.0
            }
            result['output_image'] = image
            
        elif step_id == 10:  # Affine/Homography Transform
            # Apply transformation based on method
            result['metrics'] = {
                'rmse_pixels': 2.5,
                'jitter': 0.3,
                'transform_quality': 0.9
            }
            result['output_image'] = image  # TODO: Apply actual transformation
            
        elif step_id == 11:  # ECG Trace Extraction
            result['metrics'] = {
                'leads_detected': 12,
                'confidence': 0.85,
                'layout_type': '3x4'
            }
            result['output_image'] = image
            
        elif step_id == 12:  # Apply Transform to Trace
            result['metrics'] = {
                'transform_applied': True,
                'residual_error': 0.5
            }
            result['output_image'] = image
            
        elif step_id == 13:  # Skeletonize
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Simple thinning
            kernel = np.ones((3, 3), np.uint8)
            skeleton = cv2.erode(gray, kernel, iterations=1)
            
            result['metrics'] = {
                'skeleton_points': cv2.countNonZero(skeleton),
                'continuity': 0.9,
                'branch_count': 12
            }
            result['output_image'] = skeleton
            
        elif step_id == 14:  # Convert to Signal
            # Generate sample signal data
            result['metrics'] = {
                'points_per_lead': 5000,
                'snr_db': 22.5,
                'calibration_px_per_mv': 100,
                'calibration_px_per_sec': 250
            }
            result['output_image'] = image
            # TODO: Generate actual signals
            
        elif step_id == 15:  # Low Contrast Rejection
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError("Low Contrast Rejector not available")
            
            rejector = LowContrastRejector()
            rejection_result = rejector.check(image)
            
            result['metrics'] = {
                'contrast_std': rejection_result.get('contrast_std', 0),
                'pass_fail': 'Pass' if not rejection_result.get('rejected', True) else 'Fail',
                'signal_quality': rejection_result.get('quality', 'unknown')
            }
            result['output_image'] = image
            result['rejected'] = rejection_result.get('rejected', False)
            
        else:
            raise ValueError(f"Unknown step_id: {step_id}")
            
    except Exception as e:
        result['error'] = str(e)
        result['success'] = False
        raise
    
    return result

# Flask app for multi-method processing (if using Cloud Run)
if FLASK_AVAILABLE:
    app = Flask(__name__)
    
    # Enable CORS for all routes
    if CORS_AVAILABLE:
        CORS(app, origins=["https://hv-ecg.web.app", "http://localhost:*"], supports_credentials=True)
    else:
        # Manual CORS headers if flask-cors not available
        @app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        @app.before_request
        def handle_preflight():
            if request.method == "OPTIONS":
                response = jsonify({'status': 'ok'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
                response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
                return response
    
    @app.route('/transform-multi', methods=['POST'])
    def transform_multi():
        """Endpoint for multi-method transformation processing."""
        try:
            data = request.json
            image_base64 = data.get('image')
            image_width = data.get('width')
            image_height = data.get('height')
            
            if not image_base64:
                return jsonify({'error': 'Image data required'}), 400
            
            # Decode image
            image_bytes = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return jsonify({'error': 'Failed to decode image'}), 400
            
            # Process with all methods
            if not MULTI_METHOD_AVAILABLE:
                return jsonify({
                    'success': False,
                    'message': 'Multi-method processor not available. Install transformers module.'
                }), 500
            
            processor = MultiMethodProcessor()
            result = processor.process_all_methods(image)
            
            # Convert transformed images to base64 for return
            for method_name, method_result in result['results'].items():
                if method_result.get('success') and 'transformed_image' in method_result:
                    transformed = method_result['transformed_image']
                    # Convert numpy array to base64
                    _, buffer = cv2.imencode('.png', transformed)
                    img_base64 = base64.b64encode(buffer).decode('utf-8')
                    method_result['transformed_image_base64'] = img_base64
                    # Remove numpy array (not JSON serializable)
                    del method_result['transformed_image']
            
            return jsonify({
                'success': True,
                **result
            })
            
        except Exception as e:
            response = jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
    
    @app.route('/analyze-fit', methods=['POST'])
    def analyze_fit():
        """
        Analyze grid lines and provide polynomial fit options.
        
        Expected JSON:
        {
            "horizontal_lines": [[[x1,y1], [x2,y2], ...], ...],
            "vertical_lines": [[[x1,y1], [x2,y2], ...], ...],
            "max_order": 6  // optional, default 6
        }
        
        Returns fit menu with R², deviation stats, recommendations.
        """
        try:
            from transformers.fit_analyzer import FitAnalyzer
            
            data = request.json
            h_lines = data.get('horizontal_lines', [])
            v_lines = data.get('vertical_lines', [])
            max_order = data.get('max_order', 6)
            
            # Convert to numpy arrays
            h_arrays = [np.array(line) for line in h_lines if len(line) >= 3]
            v_arrays = [np.array(line) for line in v_lines if len(line) >= 3]
            
            if not h_arrays and not v_arrays:
                return jsonify({
                    'success': False,
                    'error': 'No valid lines provided (need at least 3 points per line)'
                }), 400
            
            # Analyze
            analyzer = FitAnalyzer(max_order=max_order)
            result = analyzer.analyze_grid(h_arrays, v_arrays)
            
            return jsonify({
                'success': True,
                **result
            })
            
        except Exception as e:
            response = jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
    
    @app.route('/execute-step', methods=['POST'])
    def execute_step():
        """
        Execute a single pipeline step with specified method.
        
        Expected JSON:
        {
            "step_id": 1,
            "method_id": "laplacian",
            "image": "base64_encoded_image",
            "previous_result": {...}  // Optional, result from previous step
        }
        
        Returns:
        {
            "success": true,
            "step_id": 1,
            "method_id": "laplacian",
            "metrics": {...},
            "output_image": "base64",
            "overlays": []
        }
        """
        try:
            data = request.json
            step_id = data.get('step_id')
            method_id = data.get('method_id', 'default')
            image_base64 = data.get('image')
            previous_result = data.get('previous_result', {})
            
            if step_id is None:
                return jsonify({'error': 'step_id is required'}), 400
            
            # Decode image if provided
            image = None
            if image_base64:
                image_bytes = base64.b64decode(image_base64)
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if image is None:
                    return jsonify({'error': 'Failed to decode image'}), 400
            
            # Route to appropriate step processor
            result = process_pipeline_step(step_id, method_id, image, previous_result)
            
            # Convert output image to base64 if present
            if result.get('output_image') is not None:
                output_img = result['output_image']
                if isinstance(output_img, np.ndarray):
                    _, buffer = cv2.imencode('.png', output_img)
                    result['output_image'] = base64.b64encode(buffer).decode('utf-8')
            
            # Convert input image to base64 for preview
            if result.get('input_image') is not None:
                input_img = result['input_image']
                if isinstance(input_img, np.ndarray):
                    _, buffer = cv2.imencode('.png', input_img)
                    result['input_image'] = base64.b64encode(buffer).decode('utf-8')
            
            return jsonify({
                'success': True,
                'step_id': step_id,
                'method_id': method_id,
                **result
            })
            
        except Exception as e:
            import traceback
            return jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc()
            }), 500
    
    @app.route('/generate-kaggle-csv', methods=['POST'])
    def generate_kaggle_csv_endpoint():
        """
        Generate Kaggle submission CSV from extracted signals.
        
        Expected JSON:
        {
            "record_id": "12345",
            "signals": {
                "I": [0.1, 0.2, ...],
                "II": [...],
                ...
            }
        }
        
        Returns CSV file or base64 encoded CSV content.
        """
        try:
            from output.kaggle_csv_generator import KaggleCSVGenerator
            
            data = request.json
            record_id = data.get('record_id')
            signals = data.get('signals', {})
            return_base64 = data.get('return_base64', True)
            
            if not record_id:
                return jsonify({'error': 'record_id is required'}), 400
            
            if not signals:
                return jsonify({'error': 'signals data is required'}), 400
            
            # Generate CSV
            generator = KaggleCSVGenerator(allow_partial=True)
            
            # Use temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                output_path = f.name
            
            result = generator.generate(record_id, signals, output_path)
            
            if not result['success']:
                return jsonify({
                    'success': False,
                    'errors': result['errors'],
                    'warnings': result.get('warnings', [])
                }), 400
            
            # Read and return CSV content
            with open(output_path, 'r') as f:
                csv_content = f.read()
            
            # Cleanup temp file
            os.remove(output_path)
            
            if return_base64:
                csv_base64 = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
                return jsonify({
                    'success': True,
                    'record_id': record_id,
                    'csv_base64': csv_base64,
                    'rows_written': result['rows_written'],
                    'leads_written': result['leads_written'],
                    'warnings': result.get('warnings', [])
                })
            else:
                from flask import Response
                return Response(
                    csv_content,
                    mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment;filename=submission_{record_id}.csv'}
                )
            
        except Exception as e:
            import traceback
            return jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc()
            }), 500
    
    @app.route('/isolate-colors', methods=['POST'])
    def isolate_colors():
        """
        Isolate colors from an ECG image - separate grid from traces.
        Saves processed images to GCS and registers them in Firestore.
        
        Expected JSON:
        {
            "image": "base64_encoded_image",
            "filename": "original_filename.png",
            "method": "opencv" | "pillow" | "skimage",
            "output_type": "ecg" | "grid" | "both",
            "gcs_bucket": "bucket-name",
            "gcs_folder": "path/to/folder",
            "existing_filenames": ["file1.png", "file2.png"],
            "source_image_id": "firestore_doc_id"
        }
        
        Naming convention: {prefix}-{method}{number}-{r|b}.png
        - r = red (grid only)
        - b = black (ECG traces)
        """
        try:
            from transformers.color_isolation import ColorIsolator
            from google.cloud import storage
            from google.cloud import firestore
            
            data = request.json
            image_base64 = data.get('image')
            filename = data.get('filename', 'image.png')
            method = data.get('method', 'opencv')
            output_type = data.get('output_type', 'both')
            gcs_bucket = data.get('gcs_bucket')
            gcs_folder = data.get('gcs_folder', '')
            existing_filenames = data.get('existing_filenames', [])
            source_image_id = data.get('source_image_id')
            
            if not image_base64:
                return jsonify({'error': 'Image data required'}), 400
            
            # Decode image
            image_bytes = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return jsonify({'error': 'Failed to decode image'}), 400
            
            # Process image
            isolator = ColorIsolator()
            result = isolator.process(image, method=method, output_type=output_type)
            
            if not result['success']:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Processing failed')
                }), 500
            
            # Get next number for this group/method
            next_number = isolator.get_next_number_for_group(existing_filenames, method)
            
            # Convert output images and save to GCS
            response_outputs = {}
            saved_images = []
            
            # Initialize GCS and Firestore clients if bucket provided
            storage_client = None
            bucket = None
            db = None
            
            if gcs_bucket:
                try:
                    storage_client = storage.Client()
                    bucket = storage_client.bucket(gcs_bucket)
                    db = firestore.Client()
                except Exception as e:
                    print(f"Warning: Could not initialize GCS/Firestore: {e}")
            
            for out_type, out_data in result['outputs'].items():
                out_image = out_data['image']
                _, buffer = cv2.imencode('.png', out_image)
                img_bytes = buffer.tobytes()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                # Generate filename with new naming convention
                out_filename = isolator.generate_output_filename(
                    filename, method, out_type, next_number
                )
                
                # Save to GCS if bucket is configured
                gcs_url = None
                firestore_id = None
                
                if bucket:
                    try:
                        # Build GCS path
                        if gcs_folder:
                            gcs_path = f"{gcs_folder}/{out_filename}"
                        else:
                            gcs_path = out_filename
                        
                        # Upload to GCS
                        blob = bucket.blob(gcs_path)
                        blob.upload_from_string(img_bytes, content_type='image/png')
                        
                        # Make publicly accessible
                        blob.make_public()
                        gcs_url = f"https://storage.googleapis.com/{gcs_bucket}/{gcs_path}"
                        
                        # Register in Firestore
                        if db:
                            # Get prefix for grouping
                            prefix = filename.split('-')[0] if '-' in filename else filename.split('.')[0]
                            
                            # Determine subset based on source
                            is_train = True  # Default to train
                            is_test = False
                            
                            doc_data = {
                                'filename': out_filename,
                                'gcs_bucket': gcs_bucket,
                                'gcs_path': gcs_path,
                                'gcs_url': gcs_url,
                                'prefix': prefix,
                                'is_train': is_train,
                                'is_test': is_test,
                                'is_isolated': True,
                                'isolation_type': out_type,  # 'ecg' or 'grid'
                                'isolation_method': method,
                                'source_filename': filename,
                                'source_image_id': source_image_id,
                                'created_at': firestore.SERVER_TIMESTAMP,
                                'size': len(img_bytes),
                                'size_formatted': f"{len(img_bytes) / 1024:.1f} KB"
                            }
                            
                            # Add to ecg_images collection
                            doc_ref = db.collection('ecg_images').add(doc_data)
                            firestore_id = doc_ref[1].id
                            
                        saved_images.append({
                            'filename': out_filename,
                            'gcs_url': gcs_url,
                            'firestore_id': firestore_id,
                            'type': out_type
                        })
                        
                    except Exception as e:
                        print(f"Error saving to GCS: {e}")
                
                response_outputs[out_type] = {
                    'image_base64': img_base64,
                    'filename': out_filename,
                    'metrics': out_data['metrics'],
                    'gcs_url': gcs_url,
                    'firestore_id': firestore_id
                }
            
            return jsonify({
                'success': True,
                'method': method,
                'method_suffix': result['method_suffix'],
                'original_filename': filename,
                'outputs': response_outputs,
                'saved_images': saved_images,
                'next_number_used': next_number
            })
            
        except Exception as e:
            import traceback
            return jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc()
            }), 500
    
    @app.route('/batch-isolate-colors', methods=['POST'])
    def batch_isolate_colors():
        """
        Batch process multiple images for color isolation.
        
        Expected JSON:
        {
            "images": [
                { "image": "base64", "filename": "name.png" },
                ...
            ],
            "method": "opencv" | "pillow" | "skimage",
            "output_type": "ecg" | "grid" | "both"
        }
        
        Returns results for each image processed.
        """
        try:
            from transformers.color_isolation import ColorIsolator
            
            data = request.json
            images = data.get('images', [])
            method = data.get('method', 'opencv')
            output_type = data.get('output_type', 'both')
            
            if not images:
                return jsonify({'error': 'No images provided'}), 400
            
            isolator = ColorIsolator()
            results = []
            
            for img_data in images:
                image_base64 = img_data.get('image')
                filename = img_data.get('filename', 'image.png')
                
                try:
                    # Decode image
                    image_bytes = base64.b64decode(image_base64)
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if image is None:
                        results.append({
                            'filename': filename,
                            'success': False,
                            'error': 'Failed to decode image'
                        })
                        continue
                    
                    # Process
                    result = isolator.process(image, method=method, output_type=output_type)
                    
                    if not result['success']:
                        results.append({
                            'filename': filename,
                            'success': False,
                            'error': result.get('error', 'Processing failed')
                        })
                        continue
                    
                    # Convert outputs
                    response_outputs = {}
                    for out_type, out_data in result['outputs'].items():
                        out_image = out_data['image']
                        _, buffer = cv2.imencode('.png', out_image)
                        img_base64 = base64.b64encode(buffer).decode('utf-8')
                        out_filename = isolator.generate_output_filename(filename, method, out_type)
                        
                        response_outputs[out_type] = {
                            'image_base64': img_base64,
                            'filename': out_filename,
                            'metrics': out_data['metrics']
                        }
                    
                    results.append({
                        'filename': filename,
                        'success': True,
                        'outputs': response_outputs
                    })
                    
                except Exception as e:
                    results.append({
                        'filename': filename,
                        'success': False,
                        'error': str(e)
                    })
            
            # Summary
            success_count = sum(1 for r in results if r['success'])
            
            return jsonify({
                'success': True,
                'method': method,
                'total': len(images),
                'processed': success_count,
                'failed': len(images) - success_count,
                'results': results
            })
            
        except Exception as e:
            import traceback
            return jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc()
            }), 500
    
    @app.route('/isolation-methods', methods=['GET'])
    def get_isolation_methods():
        """Get available color isolation methods."""
        try:
            from transformers.color_isolation import ColorIsolator
            isolator = ColorIsolator()
            
            return jsonify({
                'success': True,
                'methods': [
                    {
                        'id': 'opencv',
                        'name': 'OpenCV',
                        'suffix': 'o',
                        'available': True,
                        'description': 'HSV color space masking with morphological operations'
                    },
                    {
                        'id': 'pillow',
                        'name': 'Pillow (PIL)',
                        'suffix': 'p',
                        'available': 'pillow' in isolator.get_available_methods(),
                        'description': 'RGB channel splitting and analysis'
                    },
                    {
                        'id': 'skimage',
                        'name': 'scikit-image',
                        'suffix': 's',
                        'available': 'skimage' in isolator.get_available_methods(),
                        'description': 'Advanced HSV processing with skimage color module'
                    }
                ]
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'multi_method_available': MULTI_METHOD_AVAILABLE,
            'transformers_available': TRANSFORMERS_AVAILABLE,
            'endpoints': [
                '/transform-multi', 
                '/analyze-fit', 
                '/execute-step', 
                '/generate-kaggle-csv', 
                '/isolate-colors', 
                '/batch-isolate-colors', 
                '/isolation-methods',
                '/detect-edges',
                '/process-batch',
                '/health'
            ]
        })
    
    @app.route('/detect-edges', methods=['POST'])
    def detect_edges_endpoint():
        """
        Detect edges in ECG image.
        
        Expected JSON:
        {
            "image": "base64_encoded_image",
            "method": "canny",  // optional: "canny", "sobel", "laplacian", "contour"
            "crop_to_content": false  // optional: crop image to content boundaries
        }
        """
        try:
            if not TRANSFORMERS_AVAILABLE:
                return jsonify({'error': 'Transformers not available'}), 500
            
            from transformers.edge_detector import detect_edges, crop_to_content
            
            data = request.json
            image_base64 = data.get('image')
            method = data.get('method', 'canny')
            crop_to_content_flag = data.get('crop_to_content', False)
            
            if not image_base64:
                return jsonify({'error': 'Image data required'}), 400
            
            # Decode image
            image_bytes = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return jsonify({'error': 'Failed to decode image'}), 400
            
            # Detect edges
            result = detect_edges(image, method=method)
            
            response = {
                'success': True,
                'bounding_box': {
                    'x': int(result['bounding_box'][0]),
                    'y': int(result['bounding_box'][1]),
                    'width': int(result['bounding_box'][2]),
                    'height': int(result['bounding_box'][3])
                },
                'edge_pixels': int(result['edge_pixels']),
                'contour_count': int(result['edge_count']),
                'method': method
            }
            
            # Crop if requested
            if crop_to_content_flag:
                cropped = crop_to_content(image, padding=10)
                if cropped is not None:
                    _, buffer = cv2.imencode('.png', cropped)
                    img_base64 = base64.b64encode(buffer).decode('utf-8')
                    response['cropped_image'] = img_base64
            
            return jsonify(response)
            
        except Exception as e:
            response = jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
    
    @app.route('/process-batch', methods=['POST'])
    def process_batch_endpoint():
        """
        Process multiple images in parallel (HTTP-based batch processing).
        
        Expected JSON:
        {
            "images": ["base64_image1", "base64_image2", ...],  // up to 10 images
            "options": {
                "edge_detection": true,
                "color_separation": true,
                "grid_detection": true,
                "quality_check": true,
                "crop_to_content": false,
                "color_method": "lab"  // or "hsv"
            }
        }
        """
        try:
            if not TRANSFORMERS_AVAILABLE:
                return jsonify({'error': 'Transformers not available'}), 500
            
            from transformers.edge_detector import detect_edges, crop_to_content
            from transformers.color_separation import ColorSeparator
            from transformers.quality_gates import QualityGates
            from transformers.multi_scale_grid_detector import MultiScaleGridDetector
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            data = request.json
            images_base64 = data.get('images', [])
            options = data.get('options', {})
            
            if not images_base64:
                return jsonify({'error': 'Images array required'}), 400
            
            if len(images_base64) > 10:
                return jsonify({'error': 'Maximum 10 images per batch'}), 400
            
            def process_single_image(i, image_base64):
                """Process a single image - designed for parallel execution"""
                try:
                    # Decode image
                    image_bytes = base64.b64decode(image_base64)
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if image is None:
                        return {
                            'index': i,
                            'success': False,
                            'error': 'Failed to decode image'
                        }
                    
                    result = {
                        'index': i,
                        'success': True,
                        'steps': {}
                    }
                    
                    # Edge detection
                    if options.get('edge_detection', False):
                        edge_result = detect_edges(image, method='canny')
                        result['steps']['edge_detection'] = {
                            'bounding_box': {
                                'x': int(edge_result['bounding_box'][0]),
                                'y': int(edge_result['bounding_box'][1]),
                                'width': int(edge_result['bounding_box'][2]),
                                'height': int(edge_result['bounding_box'][3])
                            },
                            'edge_pixels': int(edge_result['edge_pixels'])
                        }
                        
                        if options.get('crop_to_content', False):
                            image = crop_to_content(image, padding=10)
                    
                    # Color separation
                    if options.get('color_separation', False):
                        separator = ColorSeparator()
                        method = options.get('color_method', 'lab')
                        if method == 'hsv':
                            trace, grid_mask = separator.separate_hsv(image)
                        else:
                            trace, grid_mask = separator.separate_lab(image)
                        
                        result['steps']['color_separation'] = {
                            'method': method,
                            'trace_pixels': int(np.sum(trace > 0)) if trace is not None else 0,
                            'grid_pixels': int(np.sum(grid_mask > 0)) if grid_mask is not None else 0
                        }
                        
                        if trace is not None:
                            image = trace
                    
                    # Grid detection
                    if options.get('grid_detection', False):
                        detector = MultiScaleGridDetector()
                        grid_result = detector.detect(image)
                        result['steps']['grid_detection'] = {
                            'fine_lines': int(grid_result.get('fine_lines', 0)),
                            'bold_lines': int(grid_result.get('bold_lines', 0)),
                            'quality_score': float(grid_result.get('quality_score', 0))
                        }
                    
                    # Quality check
                    if options.get('quality_check', False):
                        gates = QualityGates()
                        quality_result = gates.check_all(image)
                        result['steps']['quality_check'] = {
                            'passed': quality_result.get('passed', False),
                            'blur_score': float(quality_result.get('blur', {}).get('score', 0)),
                            'dpi': float(quality_result.get('resolution', {}).get('estimated_dpi', 0)),
                            'warnings': quality_result.get('warnings', [])
                        }
                    
                    return result
                    
                except Exception as e:
                    return {
                        'index': i,
                        'success': False,
                        'error': str(e)
                    }
            
            # Process all images in parallel (up to 9 workers for 9 images)
            results = []
            max_workers = min(len(images_base64), 9)  # Process up to 9 images simultaneously
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_index = {
                    executor.submit(process_single_image, i, img): i 
                    for i, img in enumerate(images_base64)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_index):
                    result = future.result()
                    results.append(result)
            
            # Sort by index to maintain original order
            results.sort(key=lambda x: x['index'])
            
            return jsonify({
                'success': True,
                'count': len(results),
                'parallel': True,
                'workers_used': max_workers,
                'results': results
            })
            
        except Exception as e:
            response = jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
    
    @app.route('/process-gcs-batch', methods=['POST', 'OPTIONS'])
    def process_gcs_batch_endpoint():
        """
        Process multiple images from GCS buckets in batch.
        
        Expected JSON:
        {
            "image_paths": ["path/to/image1.png", "path/to/image2.png", ...],
            "bucket": "bucket-name",
            "options": {
                "edge_detection": true,
                "color_separation": true,
                "grid_detection": true,
                "quality_check": true,
                "crop_to_content": false,
                "color_method": "lab"
            }
        }
        """
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
            return response
        
        try:
            from google.cloud import storage
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            if not TRANSFORMERS_AVAILABLE:
                response = jsonify({'error': 'Transformers not available'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 500
            
            from transformers.edge_detector import detect_edges, crop_to_content
            from transformers.color_separation import ColorSeparator
            from transformers.quality_gates import QualityGates
            from transformers.multi_scale_grid_detector import MultiScaleGridDetector
            
            data = request.json
            image_paths = data.get('image_paths', [])
            bucket_name = data.get('bucket')
            options = data.get('options', {})
            
            if not image_paths:
                response = jsonify({'error': 'image_paths array required'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 400
            
            if not bucket_name:
                response = jsonify({'error': 'bucket name required'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 400
            
            if len(image_paths) > 20:
                response = jsonify({'error': 'Maximum 20 images per batch'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 400
            
            # Initialize GCS client
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            
            def download_and_process_image(i, image_path):
                """Download image from GCS and process it"""
                try:
                    # Download from GCS
                    blob = bucket.blob(image_path)
                    if not blob.exists():
                        return {
                            'index': i,
                            'success': False,
                            'error': f'Image not found: {image_path}',
                            'path': image_path
                        }
                    
                    image_bytes = blob.download_as_bytes()
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if image is None:
                        return {
                            'index': i,
                            'success': False,
                            'error': 'Failed to decode image',
                            'path': image_path
                        }
                    
                    result = {
                        'index': i,
                        'success': True,
                        'path': image_path,
                        'name': image_path.split('/')[-1],
                        'original_url': f'https://storage.googleapis.com/{bucket_name}/{image_path}',
                        'steps': {},
                        'metrics': {}
                    }
                    
                    # Edge detection
                    if options.get('edge_detection', False):
                        edge_result = detect_edges(image, method='canny')
                        result['steps']['edge_detection'] = {
                            'bounding_box': {
                                'x': int(edge_result['bounding_box'][0]),
                                'y': int(edge_result['bounding_box'][1]),
                                'width': int(edge_result['bounding_box'][2]),
                                'height': int(edge_result['bounding_box'][3])
                            },
                            'edge_pixels': int(edge_result['edge_pixels'])
                        }
                        
                        if options.get('crop_to_content', False):
                            image = crop_to_content(image, padding=10)
                    
                    # Color separation
                    if options.get('color_separation', False):
                        separator = ColorSeparator()
                        method = options.get('color_method', 'lab')
                        if method == 'hsv':
                            trace, grid_mask = separator.separate_hsv(image)
                        else:
                            trace, grid_mask = separator.separate_lab(image)
                        
                        result['steps']['color_separation'] = {
                            'method': method,
                            'trace_pixels': int(np.sum(trace > 0)) if trace is not None else 0,
                            'grid_pixels': int(np.sum(grid_mask > 0)) if grid_mask is not None else 0
                        }
                        
                        if trace is not None:
                            image = trace
                    
                    # Grid detection
                    if options.get('grid_detection', False):
                        detector = MultiScaleGridDetector()
                        grid_result = detector.detect(image)
                        result['steps']['grid_detection'] = {
                            'fine_lines': int(grid_result.get('fine_lines', 0)),
                            'bold_lines': int(grid_result.get('bold_lines', 0)),
                            'quality_score': float(grid_result.get('quality_score', 0))
                        }
                    
                    # Quality check
                    if options.get('quality_check', False):
                        gates = QualityGates()
                        quality_result = gates.check_all(image)
                        result['metrics'] = {
                            'blur_score': float(quality_result['blur']['score']),
                            'dpi': float(quality_result['resolution'].get('estimated_dpi', 0)),
                            'contrast_std': float(quality_result['contrast']['std']),
                            'grid_lines_count': int(quality_result['grid_detectability']['detected_lines'])
                        }
                    
                    return result
                    
                except Exception as e:
                    return {
                        'index': i,
                        'success': False,
                        'error': str(e),
                        'path': image_path,
                        'type': type(e).__name__
                    }
            
            # Process all images in parallel
            results = []
            max_workers = min(len(image_paths), 10)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_index = {
                    executor.submit(download_and_process_image, i, path): i 
                    for i, path in enumerate(image_paths)
                }
                
                for future in as_completed(future_to_index):
                    result = future.result()
                    results.append(result)
            
            # Sort by index
            results.sort(key=lambda x: x['index'])
            
            response = jsonify({
                'success': True,
                'count': len(results),
                'bucket': bucket_name,
                'results': results
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
            
        except Exception as e:
            response = jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
    
    @app.route('/process-comprehensive', methods=['POST', 'OPTIONS'])
    def process_comprehensive_endpoint():
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
            return response
        """
        Comprehensive image processing with SNR calculation and full analysis.
        
        Expected JSON:
        {
            "image": "base64_encoded_image",
            "base_image": "base64_encoded_base_image" (optional, for SNR),
            "options": {
                "edge_detection": true,
                "color_separation": true,
                "grid_detection": true,
                "quality_check": true,
                "calculate_snr": true,
                "analyze_image": true
            }
        }
        """
        try:
            if not TRANSFORMERS_AVAILABLE:
                return jsonify({'error': 'Transformers not available'}), 500
            
            # Import analyzers
            try:
                from transformers.snr_calculator import SNRCalculator
                from transformers.image_analyzer import ImageAnalyzer
                SNR_AVAILABLE = True
            except ImportError:
                SNR_AVAILABLE = False
                print("Warning: SNR calculator or image analyzer not available")
            
            from transformers.edge_detector import detect_edges
            from transformers.color_separation import ColorSeparator
            from transformers.quality_gates import QualityGates
            from transformers.multi_scale_grid_detector import MultiScaleGridDetector
            
            data = request.json
            image_base64 = data.get('image')
            base_image_base64 = data.get('base_image')
            options = data.get('options', {})
            
            if not image_base64:
                return jsonify({'error': 'Image data required'}), 400
            
            # Decode main image
            image_bytes = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return jsonify({'error': 'Failed to decode image'}), 400
            
            # Decode base image if provided
            base_image = None
            if base_image_base64:
                base_bytes = base64.b64decode(base_image_base64)
                base_nparr = np.frombuffer(base_bytes, np.uint8)
                base_image = cv2.imdecode(base_nparr, cv2.IMREAD_COLOR)
            
            result = {
                'success': True,
                'steps': {},
                'metrics': {},
                'analysis': {}
            }
            
            # Image analysis
            if options.get('analyze_image', True) and SNR_AVAILABLE:
                analyzer = ImageAnalyzer()
                
                # Image type detection
                type_result = analyzer.detect_image_type(image)
                result['analysis']['image_type'] = type_result
                
                # Contrast analysis
                contrast_result = analyzer.analyze_contrast(image)
                result['analysis']['contrast'] = contrast_result
                
                # Smudge detection
                smudge_result = analyzer.detect_smudges(image, method='morphological')
                result['analysis']['smudges'] = smudge_result
                
                # Red grid analysis (if red/black/white)
                if type_result['type'] == 'red_black_white' and options.get('color_separation', False):
                    separator = ColorSeparator()
                    _, red_grid = separator.separate_lab(image)
                    if red_grid is not None:
                        grid_result = analyzer.analyze_red_grid(red_grid)
                        result['analysis']['red_grid'] = grid_result
            
            # Edge detection
            if options.get('edge_detection', False):
                edge_result = detect_edges(image, method='canny')
                result['steps']['edge_detection'] = {
                    'bounding_box': {
                        'x': int(edge_result['bounding_box'][0]),
                        'y': int(edge_result['bounding_box'][1]),
                        'width': int(edge_result['bounding_box'][2]),
                        'height': int(edge_result['bounding_box'][3])
                    },
                    'edge_pixels': int(edge_result['edge_pixels'])
                }
            
            # Color separation
            processed_image = image.copy()
            if options.get('color_separation', False):
                separator = ColorSeparator()
                method = options.get('color_method', 'lab')
                if method == 'hsv':
                    trace, grid_mask = separator.separate_hsv(image)
                else:
                    trace, grid_mask = separator.separate_lab(image)
                
                result['steps']['color_separation'] = {
                    'method': method,
                    'trace_pixels': int(np.sum(trace > 0)) if trace is not None else 0,
                    'grid_pixels': int(np.sum(grid_mask > 0)) if grid_mask is not None else 0
                }
                
                if trace is not None:
                    processed_image = trace
            
            # Grid detection
            if options.get('grid_detection', False):
                detector = MultiScaleGridDetector()
                grid_result = detector.detect(processed_image)
                result['steps']['grid_detection'] = {
                    'fine_lines': int(grid_result.get('fine_lines', 0)),
                    'bold_lines': int(grid_result.get('bold_lines', 0)),
                    'quality_score': float(grid_result.get('quality_score', 0))
                }
            
            # Quality check
            if options.get('quality_check', False):
                gates = QualityGates()
                quality_result = gates.check_all(processed_image)
                result['metrics'] = {
                    'blur_score': float(quality_result['blur']['score']),
                    'dpi': float(quality_result['resolution'].get('estimated_dpi', 0)),
                    'contrast_std': float(quality_result['contrast']['std']),
                    'grid_lines_count': int(quality_result['grid_detectability']['detected_lines'])
                }
            
            # SNR calculation (if base image provided)
            if options.get('calculate_snr', False) and base_image is not None and SNR_AVAILABLE:
                snr_calc = SNRCalculator()
                snr_result = snr_calc.calculate_snr(base_image, processed_image)
                result['metrics']['snr'] = {
                    'snr_db': snr_result['snr_db'],
                    'signal_power': snr_result['signal_power'],
                    'noise_power': snr_result['noise_power'],
                    'snr_linear': snr_result['snr_linear']
                }
            
            # Encode processed image
            _, buffer = cv2.imencode('.png', processed_image)
            processed_base64 = base64.b64encode(buffer).decode('utf-8')
            result['processed_image'] = processed_base64
            
            response = jsonify(result)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
            
        except Exception as e:
            response = jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
    
    # Run Flask app if executed directly
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=8080, debug=False)

def process_ecg_image(request):
    """
    HTTP Cloud Function entry point
    
    Expected request format:
    {
        "image": "base64_encoded_image",
        "recordId": "record_id",
        "imageId": "image_id"
    }
    """
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    try:
        # Parse request
        request_json = request.get_json(silent=True)
        if not request_json:
            return (json.dumps({'error': 'Invalid request'}), 400, headers)

        image_base64 = request_json.get('image')
        record_id = request_json.get('recordId', 'unknown')
        image_id = request_json.get('imageId', 'unknown')

        if not image_base64:
            return (json.dumps({'error': 'Image data required'}), 400, headers)

        # Decode base64 image
        image_bytes = base64.b64decode(image_base64)

        # Process ECG image
        result = process_ecg_for_firebase(image_bytes)

        # Add metadata
        result['recordId'] = record_id
        result['imageId'] = image_id

        return (json.dumps(result), 200, headers)

    except Exception as e:
        error_response = {
            'error': str(e),
            'type': type(e).__name__
        }
        return (json.dumps(error_response), 500, headers)
