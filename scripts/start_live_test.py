"""
Start Live Test Server
Quick launcher for the live testing interface
"""

import sys
import os
from pathlib import Path

# Add functions_python to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'functions_python'))

# Check if Flask is installed
try:
    import flask
except ImportError:
    print("Error: Flask is not installed")
    print("Please install it with: pip install flask")
    sys.exit(1)

# Import the app
try:
    from live_test_server import app
except ImportError as e:
    print(f"Error importing live_test_server: {e}")
    print("Please check that all dependencies are installed:")
    print("  pip install flask werkzeug")
    sys.exit(1)
except Exception as e:
    print(f"Error loading live_test_server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == '__main__':
    print("=" * 60)
    print("ECG Digitization - Live Test Server")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("Open your browser and navigate to the URL above")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")
