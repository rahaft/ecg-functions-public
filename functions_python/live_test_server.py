"""
Live Test Server
Web interface for real-time ECG image testing
"""

import os
import sys
import io
import base64
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, send_file
from werkzeug.utils import secure_filename
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from PIL import Image

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from digitization_pipeline import ECGDigitizer
from line_visualization import LineVisualizer
from quality_assessment import QualityAssessor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'data/uploads'
app.config['RESULTS_FOLDER'] = 'data/live_results'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image_to_base64(image_path):
    """Convert image to base64 for web display"""
    with open(image_path, 'rb') as f:
        img_data = f.read()
    return base64.b64encode(img_data).decode('utf-8')

def create_signal_plot(leads, output_path):
    """Create signal plot and return as base64"""
    fig, axes = plt.subplots(4, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for i, lead_data in enumerate(leads):
        if i >= 12:
            break
        
        ax = axes[i]
        signal_values = np.array(lead_data['values'])
        time = np.arange(len(signal_values)) / lead_data['sampling_rate']
        
        ax.plot(time, signal_values, linewidth=1.5, color='#2E86AB')
        ax.set_title(f"Lead {lead_data['name']}", fontsize=10, fontweight='bold')
        ax.set_xlabel('Time (s)', fontsize=8)
        ax.set_ylabel('Voltage (mV)', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for i in range(len(leads), 12):
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return process_image_to_base64(output_path)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ECG Digitization - Live Test</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content {
            padding: 30px;
        }
        .upload-section {
            background: #f8f9fa;
            border: 3px dashed #667eea;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
        }
        .upload-section.dragover {
            background: #e3f2fd;
            border-color: #2196F3;
        }
        .file-input-wrapper {
            position: relative;
            display: inline-block;
        }
        .file-input {
            position: absolute;
            opacity: 0;
            width: 100%;
            height: 100%;
            cursor: pointer;
        }
        .file-label {
            display: inline-block;
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
        }
        .file-label:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .process-btn {
            margin-top: 20px;
            padding: 15px 40px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .process-btn:hover:not(:disabled) {
            background: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
        }
        .process-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .results {
            display: none;
            margin-top: 30px;
        }
        .results-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .result-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .result-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .result-image {
            width: 100%;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .metric-card {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }
        .full-width {
            grid-column: 1 / -1;
        }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
            border-left: 4px solid #c62828;
        }
        .filename {
            margin-top: 10px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ ECG Digitization Pipeline</h1>
            <p>Live Testing Interface</p>
        </div>
        <div class="content">
            <div class="upload-section" id="uploadSection">
                <h2 style="margin-bottom: 20px; color: #333;">Upload ECG Image</h2>
                <div class="file-input-wrapper">
                    <input type="file" id="fileInput" class="file-input" accept="image/*">
                    <label for="fileInput" class="file-label">📁 Choose Image</label>
                </div>
                <div class="filename" id="filename"></div>
                <button class="process-btn" id="processBtn" onclick="processImage()" disabled>🚀 Process Image</button>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Processing image... This may take a moment.</p>
            </div>
            
            <div class="error" id="error" style="display: none;"></div>
            
            <div class="results" id="results">
                <h2 style="margin-bottom: 20px; color: #333;">Results</h2>
                
                <div class="results-grid">
                    <div class="result-card">
                        <h3>Grid Detection</h3>
                        <img id="gridImage" class="result-image" alt="Grid visualization">
                    </div>
                    <div class="result-card">
                        <h3>Signal Plots</h3>
                        <img id="signalImage" class="result-image" alt="Signal plots">
                    </div>
                </div>
                
                <div class="metrics" id="metrics"></div>
            </div>
        </div>
    </div>
    
    <script>
        const fileInput = document.getElementById('fileInput');
        const processBtn = document.getElementById('processBtn');
        const filename = document.getElementById('filename');
        const uploadSection = document.getElementById('uploadSection');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const error = document.getElementById('error');
        
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                filename.textContent = 'Selected: ' + e.target.files[0].name;
                processBtn.disabled = false;
            }
        });
        
        uploadSection.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadSection.classList.add('dragover');
        });
        
        uploadSection.addEventListener('dragleave', function(e) {
            uploadSection.classList.remove('dragover');
        });
        
        uploadSection.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadSection.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                filename.textContent = 'Selected: ' + e.dataTransfer.files[0].name;
                processBtn.disabled = false;
            }
        });
        
        async function processImage() {
            const file = fileInput.files[0];
            if (!file) return;
            
            // Show loading, hide results
            loading.style.display = 'block';
            results.style.display = 'none';
            error.style.display = 'none';
            processBtn.disabled = true;
            
            const formData = new FormData();
            formData.append('image', file);
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.error) {
                    error.textContent = 'Error: ' + data.error;
                    error.style.display = 'block';
                } else {
                    // Display results
                    document.getElementById('gridImage').src = 'data:image/png;base64,' + data.grid_image;
                    document.getElementById('signalImage').src = 'data:image/png;base64,' + data.signal_image;
                    
                    // Display metrics
                    const metricsDiv = document.getElementById('metrics');
                    metricsDiv.innerHTML = `
                        <div class="metric-card">
                            <div class="metric-label">Overall Quality Score</div>
                            <div class="metric-value">${data.quality.overall_score.toFixed(3)}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Mean SNR</div>
                            <div class="metric-value">${data.quality.snr.mean_snr.toFixed(2)} dB</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Grid Score</div>
                            <div class="metric-value">${data.quality.grid_quality ? data.quality.grid_quality.grid_score.toFixed(3) : 'N/A'}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Clarity Score</div>
                            <div class="metric-value">${data.quality.signal_clarity.clarity_score.toFixed(3)}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Completeness</div>
                            <div class="metric-value">${data.quality.completeness.overall_completeness.toFixed(3)}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Valid Leads</div>
                            <div class="metric-value">${data.quality.completeness.valid_leads}/${data.quality.completeness.num_leads}</div>
                        </div>
                    `;
                    
                    results.style.display = 'block';
                }
            } catch (err) {
                error.textContent = 'Error: ' + err.message;
                error.style.display = 'block';
            } finally {
                loading.style.display = 'none';
                processBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process():
    """Process uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, or TIFF'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process image
        # Set visualizer output to results folder
        visualizer = LineVisualizer(output_dir=app.config['RESULTS_FOLDER'])
        digitizer = ECGDigitizer(
            use_segmented_processing=True,
            enable_visualization=False  # We'll handle visualization manually
        )
        digitizer.visualizer = visualizer  # Set custom visualizer
        
        result = digitizer.process_image(filepath)
        grid_info = digitizer.last_grid_info
        
        # Quality assessment
        quality_assessor = QualityAssessor(sampling_rate=digitizer.sampling_rate)
        quality = quality_assessor.assess_quality(result['leads'], grid_info)
        
        # Generate visualizations
        # Grid visualization
        original_image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        viz_filename = f'grid_{Path(filename).stem}'
        grid_viz_path = visualizer.visualize_grid_lines(
            original_image, grid_info, filename=viz_filename
        )
        grid_image_b64 = process_image_to_base64(grid_viz_path)
        
        # Signal plots
        signal_plot_path = os.path.join(app.config['RESULTS_FOLDER'], f'signals_{Path(filename).stem}.png')
        signal_image_b64 = create_signal_plot(result['leads'], signal_plot_path)
        
        return jsonify({
            'success': True,
            'grid_image': grid_image_b64 or '',
            'signal_image': signal_image_b64,
            'quality': {
                'overall_score': quality['overall_score'],
                'snr': {
                    'mean_snr': quality['snr']['mean_snr'],
                    'min_snr': quality['snr']['min_snr'],
                    'max_snr': quality['snr']['max_snr']
                },
                'grid_quality': quality.get('grid_quality'),
                'signal_clarity': quality['signal_clarity'],
                'completeness': quality['completeness']
            }
        })
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error processing image: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("ECG Digitization - Live Test Server")
    print("=" * 60)
    print(f"Server starting on http://localhost:5000")
    print("Open your browser and navigate to the URL above")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
