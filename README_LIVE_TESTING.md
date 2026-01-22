# Live Testing Interface

## Quick Start

### 1. Install Flask (if not already installed)

```bash
cd functions_python
pip install flask werkzeug
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Start the Live Test Server

```bash
python scripts/start_live_test.py
```

Or directly:
```bash
python functions_python/live_test_server.py
```

### 3. Open in Browser

The server will start on `http://localhost:5000`

Open your web browser and navigate to:
```
http://localhost:5000
```

## Features

### Interactive Web Interface

- **Drag & Drop Upload**: Drag ECG images directly onto the upload area
- **File Browser**: Click to browse and select images
- **Real-time Processing**: See results instantly after processing
- **Visual Results**: 
  - Grid detection visualization
  - Signal plots for all 12 leads
- **Quality Metrics**: 
  - Overall quality score
  - SNR (Signal-to-Noise Ratio)
  - Grid quality score
  - Signal clarity
  - Completeness metrics

### Supported Image Formats

- PNG
- JPG/JPEG
- TIFF/TIF

### How to Use

1. **Start the server** (see above)
2. **Open browser** to `http://localhost:5000`
3. **Upload an image**:
   - Drag and drop an ECG image onto the upload area, OR
   - Click "Choose Image" to browse for a file
4. **Click "Process Image"** button
5. **View results**:
   - Grid detection visualization (left)
   - Signal plots (right)
   - Quality metrics below

## Example Workflow

```bash
# Terminal 1: Start the server
python scripts/start_live_test.py

# Browser: Open http://localhost:5000
# Then upload and process images interactively
```

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, you can change it:

Edit `functions_python/live_test_server.py` and change:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```
to:
```python
app.run(host='0.0.0.0', port=8080, debug=True)  # or any other port
```

### Flask Not Found

```bash
pip install flask werkzeug
```

### Images Not Processing

- Check that the image file is a valid ECG image
- Ensure file size is under 16MB
- Check server console for error messages

### Browser Not Opening Automatically

Manually navigate to `http://localhost:5000` in your browser.

## Server Output

The server will show:
- Processing status
- Any errors that occur
- File upload confirmations

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Advanced Usage

### Custom Port

```python
# In live_test_server.py, change:
app.run(host='0.0.0.0', port=YOUR_PORT, debug=True)
```

### Network Access

The server runs on `0.0.0.0` by default, so it's accessible from other devices on your network:
- Local: `http://localhost:5000`
- Network: `http://YOUR_IP:5000`

### Debug Mode

Debug mode is enabled by default. For production, set `debug=False` in the `app.run()` call.
