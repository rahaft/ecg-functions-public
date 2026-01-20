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
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from digitization_pipeline import ECGDigitizer, process_ecg_for_firebase

# Import multi-method processor
try:
    from transformers.multi_method_processor import MultiMethodProcessor
    MULTI_METHOD_AVAILABLE = True
except ImportError:
    MULTI_METHOD_AVAILABLE = False
    print("Warning: Multi-method transformer not available. Install transformers module.")

# Flask app for multi-method processing (if using Cloud Run)
if FLASK_AVAILABLE:
    app = Flask(__name__)
    
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
            return jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__
            }), 500
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'multi_method_available': MULTI_METHOD_AVAILABLE
        })
    
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
