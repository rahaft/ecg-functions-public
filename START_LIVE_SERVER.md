# Starting the Live Test Server

## Quick Start

### Step 1: Navigate to functions_python directory
```powershell
cd functions_python
```

### Step 2: Run the server
```powershell
python live_test_server.py
```

### Step 3: Open browser
Once you see:
```
Starting server on http://localhost:5000
```

Open your web browser and go to:
```
http://localhost:5000
```

## What You'll See

A web interface where you can:
1. **Upload ECG images** - Drag & drop or click to browse
2. **Process images** - Click "Process Image" button
3. **View results instantly**:
   - Grid detection visualization
   - Signal plots for all 12 leads
   - Quality metrics (SNR, grid quality, etc.)

## If You Get Import Errors

### Error: "No module named 'cv2'"
OpenCV is missing. Try installing it:
```powershell
pip install opencv-python
```

### Error: "No module named 'flask'"
Flask is missing. Install it:
```powershell
pip install flask werkzeug
```

### Install All Dependencies at Once
```powershell
pip install -r requirements.txt
```

## Alternative: Use Virtual Environment

If you set up a virtual environment:
```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Then start server
cd functions_python
python live_test_server.py
```

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Troubleshooting

### Port 5000 Already in Use
Change the port in `live_test_server.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)  # Use port 8080 instead
```

### Server Won't Start
Check for error messages in the terminal. Common issues:
- Missing dependencies (install with pip)
- Port conflict (change port number)
- File path issues (make sure you're in the right directory)

## Features of the Live Interface

- **Drag & Drop Upload** - Simply drag ECG images onto the page
- **Real-time Processing** - See results immediately
- **Visual Feedback** - Loading spinner during processing
- **Quality Metrics** - Comprehensive quality assessment
- **Grid Visualization** - See detected grid lines overlaid on image
- **Signal Plots** - View digitized ECG waveforms for all 12 leads
