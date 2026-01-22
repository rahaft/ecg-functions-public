# Testing the ECG Digitization Pipeline

## Quick Start

### 1. Test a Single Image

```bash
# Test an ECG image
python scripts/run_test.py test path/to/ecg_image.jpg

# Or use the interactive mode
python scripts/run_test.py interactive
```

This will:
- Process the image through the pipeline
- Generate grid visualizations
- Create signal plots for all 12 leads
- Generate a quality report
- Save all outputs to `data/test_output/`

### 2. View Results in Browser

```bash
# Start web server to view results
python scripts/run_test.py view

# Or specify custom results directory
python scripts/run_test.py view data/test_output
```

This starts a local web server at `http://localhost:8000` where you can view:
- Grid detection visualizations
- Signal plots
- Quality reports

### 3. Direct Python Testing

```python
from functions_python.test_pipeline import test_single_image

# Test an image
result, quality = test_single_image('path/to/image.jpg', 'output_dir')
```

## Output Files

After testing, you'll find in the output directory:

- `grid_<image_name>.png` - Grid line detection visualization
- `<image_name>_signals.png` - Signal plots for all 12 leads
- `<image_name>_quality_report.txt` - Detailed quality metrics

## Testing with Sample Images

### Option 1: Use Your Own Images
Place ECG images in a directory and test them:

```bash
python scripts/run_test.py test my_ecg_images/sample1.jpg
```

### Option 2: Download from Kaggle (if set up)
```python
from functions_python.data_loader import CompetitionDataLoader

loader = CompetitionDataLoader(data_source='kaggle')
images = loader.list_images('train')

# Test first image
if images:
    image = loader.load_image(images[0])
    # Save temporarily and test
    import cv2
    cv2.imwrite('temp_image.jpg', image)
    test_single_image('temp_image.jpg')
```

## Viewing Results

### Web Viewer
The simplest way to view results:

```bash
python scripts/run_test.py view
```

Then open `http://localhost:8000` in your browser.

### Direct File Access
All results are saved as image files you can open directly:
- Open `data/test_output/grid_*.png` - See detected grid lines
- Open `data/test_output/*_signals.png` - See digitized signals

## Understanding the Output

### Quality Metrics
- **Overall Score** (0-1): Combined quality metric
- **Mean SNR** (dB): Signal-to-noise ratio
- **Grid Score** (0-1): Quality of grid detection
- **Clarity Score** (0-1): Signal clarity
- **Completeness** (0-1): How many leads were successfully extracted

### Visualizations
- **Grid Visualization**: Shows detected horizontal/vertical lines with polynomial fits
- **Signal Plots**: 12 subplots showing digitized ECG signals for each lead

## Troubleshooting

### No images found
Make sure you have test images available. You can:
1. Use your own ECG images
2. Set up Kaggle API to download competition images
3. Use sample images from the competition

### Import errors
Make sure all dependencies are installed:
```bash
cd functions_python
pip install -r requirements.txt
```

### Visualization not working
If matplotlib has issues, try:
```bash
pip install matplotlib --upgrade
```

## Advanced Testing

### Batch Processing
```python
from functions_python.batch_processor import BatchProcessor

processor = BatchProcessor()
results = processor.process_batch(['img1.jpg', 'img2.jpg', 'img3.jpg'])
ranked = processor.rank_by_quality(results)
best = processor.get_best_images(5)
```

### Custom Visualization
```python
from functions_python.line_visualization import LineVisualizer

visualizer = LineVisualizer()
visualizer.visualize_grid_lines(image, grid_info, filename='custom_viz')
```
