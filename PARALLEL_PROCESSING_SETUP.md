# Parallel Processing Setup Guide

## Overview

This system enables parallel processing of ECG images via WebSocket connections, supporting:
- **10+ concurrent image processing** via WebSocket
- **Edge detection** for image boundary detection
- **Bulk testing** framework for function validation
- **GCS integration** for Google Cloud Storage images
- **Notebook-ready** functions for Kaggle submission

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PARALLEL PROCESSING SYSTEM                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐                    │
│  │   Client     │◄────────┤  WebSocket   │                    │
│  │  (Browser)   │         │    Server    │                    │
│  └──────────────┘         └──────────────┘                    │
│         │                        │                              │
│         │                        │                              │
│         │                        ▼                              │
│         │              ┌──────────────────┐                    │
│         │              │  Worker Pool      │                    │
│         │              │  (10 workers)     │                    │
│         │              └──────────────────┘                    │
│         │                        │                              │
│         │                        ▼                              │
│         │              ┌──────────────────┐                    │
│         └─────────────▶│  Processing      │                    │
│                        │  Pipeline        │                    │
│                        └──────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. WebSocket Server (`websocket_server.py`)

**Purpose:** Handle parallel image processing requests

**Features:**
- 10 concurrent worker connections
- Batch processing support
- GCS integration
- Error handling and recovery

**Start Server:**
```bash
cd functions_python
python websocket_server.py
```

**Configuration:**
```python
server = WebSocketProcessingServer(
    max_workers=10,  # Number of parallel workers
    port=8765        # WebSocket port
)
```

### 2. Edge Detection (`transformers/edge_detector.py`)

**Purpose:** Detect image boundaries and edges

**Methods:**
- `canny` - Canny edge detection (default, recommended)
- `sobel` - Sobel edge detection
- `laplacian` - Laplacian edge detection
- `contour` - Contour-based detection

**Usage:**
```python
from transformers.edge_detector import detect_edges, crop_to_content

# Detect edges
result = detect_edges(image, method='canny')

# Crop to content
cropped = crop_to_content(image, padding=10)
```

### 3. Bulk Testing (`bulk_tester.py`)

**Purpose:** Test functions with multiple images

**Features:**
- Parallel execution
- Result aggregation
- Error tracking
- Performance metrics

**Usage:**
```python
from bulk_tester import BulkTester, test_edge_detection

# Test edge detection
results = await test_edge_detection(
    image_paths=['img1.png', 'img2.png'],
    source='local'  # or 'gcs'
)

# Custom test
tester = BulkTester(max_workers=10)
await tester.test_function(
    function=my_function,
    image_paths=paths,
    test_name='my_test'
)
```

### 4. WebSocket Client (`public/websocket_client.js`)

**Purpose:** Client-side WebSocket handler

**Usage:**
```javascript
// Initialize
const processor = initWebSocketProcessor('ws://localhost:8765');
await processor.connect();

// Process single image
const result = await processor.processImage(imageElement, {
    edge_detection: true,
    color_separation: true,
    grid_detection: true
});

// Process batch (10 images)
const batchResult = await processor.processBatch(imageElements, options);

// Process GCS batch
const gcsResult = await processor.processGCSBatch(
    'bucket-name',
    ['path1.png', 'path2.png'],
    options
);
```

### 5. Notebook Wrapper (`notebook_wrapper.py`)

**Purpose:** Make functions Kaggle notebook-compatible

**Features:**
- Path abstraction for Kaggle
- Offline mode support
- Submission formatting

**Usage in Kaggle:**
```python
from notebook_wrapper import (
    notebook_process_image,
    notebook_process_batch,
    save_submission
)

# Process single image
result = notebook_process_image('test_image.png')

# Process batch
results = notebook_process_batch(['img1.png', 'img2.png'])

# Format and save submission
entries = format_submission(results, record_id='62')
save_submission(entries, 'submission.csv')
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install websockets numpy opencv-python pillow
pip install google-cloud-storage  # For GCS support
```

### 2. Start WebSocket Server

```bash
cd functions_python
python websocket_server.py
```

Server will start on `ws://localhost:8765`

### 3. Integrate Client (gallery.html)

Add to `gallery.html`:

```html
<script src="websocket_client.js"></script>
<script>
    // Initialize WebSocket processor
    let wsProcessor = null;
    
    async function initParallelProcessing() {
        wsProcessor = initWebSocketProcessor('ws://localhost:8765');
        await wsProcessor.connect();
        console.log('WebSocket connected');
    }
    
    // Process images from GCS
    async function processGCSImagesParallel(bucketName, imagePaths) {
        if (!wsProcessor) {
            await initParallelProcessing();
        }
        
        const results = await processGCSImagesParallel(
            bucketName,
            imagePaths,
            {
                edge_detection: true,
                color_separation: true,
                grid_detection: true,
                quality_check: true
            }
        );
        
        return results;
    }
</script>
```

---

## Processing Options

### Edge Detection Options
```javascript
{
    edge_detection: true,      // Enable edge detection
    crop_to_content: true,    // Crop image to content boundaries
    method: 'canny'           // 'canny', 'sobel', 'laplacian', 'contour'
}
```

### Color Separation Options
```javascript
{
    color_separation: true,   // Enable color separation
    color_method: 'lab'       // 'lab' or 'hsv'
}
```

### Grid Detection Options
```javascript
{
    grid_detection: true      // Enable grid line detection
}
```

### Quality Check Options
```javascript
{
    quality_check: true       // Enable quality gates
}
```

---

## Bulk Testing

### Test Edge Detection
```python
from bulk_tester import test_edge_detection

results = await test_edge_detection(
    image_paths=['img1.png', 'img2.png', ...],
    source='local'  # or 'gcs'
)
```

### Test Color Separation
```python
from bulk_tester import test_color_separation

results = await test_color_separation(
    image_paths=['img1.png', 'img2.png', ...],
    method='lab',  # or 'hsv'
    source='gcs',
    bucket_name='my-bucket'
)
```

### Test Quality Gates
```python
from bulk_tester import test_quality_gates

results = await test_quality_gates(
    image_paths=['img1.png', 'img2.png', ...],
    source='gcs',
    bucket_name='my-bucket'
)
```

### Custom Bulk Test
```python
from bulk_tester import BulkTester

tester = BulkTester(max_workers=10)

await tester.test_function(
    function=my_custom_function,
    image_paths=image_paths,
    test_name='custom_test',
    source='gcs',
    bucket_name='my-bucket',
    param1=value1,
    param2=value2
)

# Get summary
summary = tester.get_summary()
print(json.dumps(summary, indent=2))

# Save results
tester.save_results('test_results.json')
```

---

## GCS Integration

### Process Images from GCS

**Server-side:**
```python
# In websocket_server.py, already configured
# Just send message with bucket_name and image_paths
```

**Client-side:**
```javascript
const result = await processor.processGCSBatch(
    'my-gcs-bucket',
    [
        'ecg_images/user1/record1/image1.png',
        'ecg_images/user1/record1/image2.png',
        // ... up to 10 images
    ],
    {
        edge_detection: true,
        color_separation: true,
        grid_detection: true
    }
);
```

---

## Performance

### Benchmarks

| Operation | Single Image | Batch (10 images) |
|-----------|--------------|-------------------|
| Edge Detection | 50-100 ms | 500-1000 ms |
| Color Separation | 100-200 ms | 1000-2000 ms |
| Grid Detection | 200-400 ms | 2000-4000 ms |
| Full Pipeline | 500-800 ms | 5000-8000 ms |

### Optimization Tips

1. **Batch Processing:** Always use batch processing for 2+ images
2. **Worker Pool:** Adjust `max_workers` based on CPU cores
3. **Selective Processing:** Only enable needed options
4. **GCS Caching:** Cache downloaded images when possible

---

## Error Handling

### Server Errors
- Connection lost: Automatic reconnection (up to 5 attempts)
- Worker busy: Queue requests or increase `max_workers`
- Processing error: Error returned in result, other images continue

### Client Errors
```javascript
try {
    const result = await processor.processImage(image, options);
    if (result.error) {
        console.error('Processing error:', result.error);
    }
} catch (error) {
    console.error('Connection error:', error);
    // Attempt reconnection
    await processor.connect();
}
```

---

## Documentation

Each function includes inline documentation:
- **Purpose:** What it does
- **How it works:** Algorithm/approach
- **What works:** Successful features
- **What didn't work:** Failed approaches and alternatives
- **Changes:** Version history

See `FUNCTION_DOCUMENTATION_TEMPLATE.md` for documentation format.

---

## Next Steps

1. **Start WebSocket server** on your development machine
2. **Integrate client** into `gallery.html`
3. **Test with sample images** from GCS
4. **Run bulk tests** to validate functions
5. **Document results** using template

---

*Last Updated: January 21, 2026*
