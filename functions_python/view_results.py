"""
View Results
Simple web-based viewer for ECG digitization results
"""

import os
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import time


class ResultsViewer:
    """Simple web viewer for results"""
    
    def __init__(self, results_dir: str = 'data/test_output', port: int = 8000):
        """
        Initialize viewer
        
        Args:
            results_dir: Directory containing results
            port: Port for web server
        """
        self.results_dir = Path(results_dir)
        self.port = port
        self.server = None
    
    def create_viewer_html(self):
        """Create HTML viewer page"""
        results_dir_str = str(self.results_dir)
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ECG Digitization Results Viewer</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .image-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .image-card {{
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            background: #fafafa;
        }}
        .image-card img {{
            width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        .image-card h3 {{
            margin: 10px 0 5px 0;
            color: #555;
        }}
        .info {{
            font-size: 12px;
            color: #777;
            margin-top: 5px;
        }}
        .refresh-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        .refresh-btn:hover {{
            background: #45a049;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ECG Digitization Results</h1>
        <button class="refresh-btn" onclick="location.reload()">Refresh</button>
        
        <div class="image-grid" id="imageGrid">
            <!-- Images will be loaded here -->
        </div>
    </div>
    
    <script>
        function loadImages() {{
            const grid = document.getElementById('imageGrid');
            const resultsDir = '{results_dir_str}';
            
            // List of image types to display
            const imageTypes = [
                {{name: 'Grid Visualization', pattern: 'grid_*.png'}},
                {{name: 'Signal Plots', pattern: '*_signals.png'}}
            ];
            
            // This is a simplified version - in production, you'd use a backend API
            // to list files dynamically
            const images = [
                // Add your image paths here or use a backend endpoint
            ];
            
            images.forEach(img => {{
                const card = document.createElement('div');
                card.className = 'image-card';
                card.innerHTML = `
                    <h3>${{img.name}}</h3>
                    <img src="/${{img.path}}" alt="${{img.name}}" />
                    <div class="info">${{img.info}}</div>
                `;
                grid.appendChild(card);
            }});
        }}
        
        window.onload = loadImages;
    </script>
</body>
</html>
"""
        return html_content
    
    def start_server(self, open_browser: bool = True):
        """Start web server"""
        class CustomHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(self.results_dir), **kwargs)
        
        # Set directory for handler
        CustomHandler.directory = str(self.results_dir)
        
        self.server = HTTPServer(('localhost', self.port), CustomHandler)
        
        def open_browser_delayed():
            time.sleep(1)
        if open_browser:
            webbrowser.open(f'http://localhost:{self.port}')
        
        print(f"Server started at http://localhost:{self.port}")
        print(f"Serving files from: {self.results_dir}")
        print("Press Ctrl+C to stop")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            self.server.shutdown()
    
    def list_results(self):
        """List available result files"""
        if not self.results_dir.exists():
            print(f"Results directory does not exist: {self.results_dir}")
            return []
        
        results = {
            'images': [],
            'reports': [],
            'data': []
        }
        
        for file_path in self.results_dir.iterdir():
            if file_path.is_file():
                if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    results['images'].append(str(file_path.name))
                elif file_path.suffix == '.txt':
                    results['reports'].append(str(file_path.name))
                elif file_path.suffix == '.json':
                    results['data'].append(str(file_path.name))
        
        return results


def view_results(results_dir: str = 'data/test_output', port: int = 8000):
    """
    View results in web browser
    
    Args:
        results_dir: Directory containing results
        port: Port for web server
    """
    viewer = ResultsViewer(results_dir, port)
    
    # List available files
    results = viewer.list_results()
    
    if not any(results.values()):
        print(f"No results found in {results_dir}")
        print("Run test_pipeline.py first to generate results")
        return
    
    print("Available results:")
    if results['images']:
        print(f"  Images: {len(results['images'])}")
        for img in results['images'][:5]:
            print(f"    - {img}")
    if results['reports']:
        print(f"  Reports: {len(results['reports'])}")
    if results['data']:
        print(f"  Data files: {len(results['data'])}")
    
    # Start server
    viewer.start_server()


if __name__ == "__main__":
    import sys
    
    results_dir = sys.argv[1] if len(sys.argv) > 1 else 'data/test_output'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    view_results(results_dir, port)
