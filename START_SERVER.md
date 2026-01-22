# Start Live Test Server

## Quick Command

Open a new terminal and run:

```powershell
cd functions_python
python live_test_server.py
```

You should see:
```
============================================================
ECG Digitization - Live Test Server
============================================================
Starting server on http://localhost:5000
Open your browser and navigate to the URL above
Press Ctrl+C to stop the server
============================================================
 * Running on http://0.0.0.0:5000
```

## Then Open Your Browser

Go to: **http://localhost:5000**

You'll see a web interface where you can:
- Upload ECG images (drag & drop or browse)
- Process images in real-time
- View grid detection visualizations
- See signal plots for all 12 leads
- Check quality metrics
