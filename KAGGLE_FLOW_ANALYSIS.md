# Kaggle Flow Functions & Parallel Processing Analysis

## 📋 Functions in Kaggle Flow

### Main Processing Pipeline Functions

1. **`process_image_for_submission(image_path, options)`** (`notebook_wrapper.py`)
   - Processes a single ECG image
   - Steps: Edge detection → Color separation → Grid detection → Quality check
   - Returns formatted results for submission

2. **`process_batch_for_submission(image_paths, options)`** (`notebook_wrapper.py`)
   - Processes multiple images
   - **Current: Sequential (one at a time)**
   - Returns list of results

3. **`notebook_process_batch(image_paths)`** (`notebook_wrapper.py`)
   - Wrapper for batch processing (notebook-friendly)
   - **Current: Sequential**

### API Endpoints (Cloud Run)

4. **`/process-batch`** (`main.py` line 1079)
   - HTTP endpoint for batch processing
   - **Current: Sequential processing** (loop through images one by one)
   - Max 10 images per batch
   - Steps: Edge detection, Color separation, Grid detection, Quality check

5. **`/detect-edges`** (`main.py` line 1012)
   - Single image edge detection
   - Methods: canny, sobel, laplacian, contour

6. **`/isolate-colors`** (`main.py` line 667)
   - Color isolation (separate grid from traces)
   - Methods: opencv, pillow, skimage

7. **`/batch-isolate-colors`** (`main.py` line 844)
   - Batch color isolation
   - **Current: Sequential**

### Processing Steps (Pipeline)

8. **Edge Detection** (`transformers/edge_detector.py`)
   - Detect image boundaries
   - Optional crop to content

9. **Color Separation** (`transformers/color_separation.py`)
   - Separate ECG traces from grid
   - Methods: LAB, HSV

10. **Grid Detection** (`transformers/multi_scale_grid_detector.py`)
    - Detect 1mm and 5mm grid lines
    - Multi-scale detection

11. **Quality Gates** (`transformers/quality_gates.py`)
    - Check blur, resolution, contrast
    - Pass/fail validation

---

## ⚠️ Current State: **NOT PARALLEL**

### Sequential Processing Found

**`/process-batch` endpoint** (main.py:1118-1201):
```python
for i, image_base64 in enumerate(images_base64):
    # Process one image at a time
    result = process_single_image(...)
    results.append(result)
```

**`process_batch_for_submission`** (notebook_wrapper.py:194):
```python
for image_path in image_paths:
    result = process_image_for_submission(image_path, options)
    results.append(result)
```

**`BatchProcessor.process_batch`** (batch_processor.py:51):
```python
for image_path in tqdm(image_paths, desc="Processing images"):
    result = self._process_single_image(image_path)
    results.append(result)
```

---

## ✅ Parallel Processing Components Available

### 1. **`bulk_tester.py`** - Has parallel execution
```python
from concurrent.futures import ProcessPoolExecutor, as_completed
# Creates tasks for parallel execution
# Executes in parallel (limit concurrency)
```

### 2. **`websocket_server.py`** - WebSocket parallel processing
```python
# Supports 10+ concurrent connections
# Process all images in parallel
async def process_batch(self, websocket, data: Dict):
    # Process all images in parallel
```

### 3. **`multi_method_processor.py`** - Uses ProcessPoolExecutor
```python
from concurrent.futures import ProcessPoolExecutor, as_completed
# Apply all transformation methods in parallel
```

---

## 🔧 How to Enable Parallel Processing for 9 Images

### Option 1: Update `/process-batch` Endpoint

Modify `functions_python/main.py` line 1079:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

@app.route('/process-batch', methods=['POST'])
def process_batch_endpoint():
    # ... existing code ...
    
    def process_single_image_wrapper(i, image_base64):
        """Wrapper for parallel execution"""
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
            
            # Process image (same logic as before)
            result = {
                'index': i,
                'success': True,
                'steps': {}
            }
            
            # ... processing steps ...
            
            return result
        except Exception as e:
            return {
                'index': i,
                'success': False,
                'error': str(e)
            }
    
    # Process in parallel (up to 9 workers)
    results = []
    with ThreadPoolExecutor(max_workers=9) as executor:
        futures = {
            executor.submit(process_single_image_wrapper, i, img): i 
            for i, img in enumerate(images_base64)
        }
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    # Sort by index to maintain order
    results.sort(key=lambda x: x['index'])
    
    return jsonify({
        'success': True,
        'count': len(results),
        'results': results
    })
```

### Option 2: Use Existing `bulk_tester.py`

Create a new endpoint that uses `BulkTester`:

```python
from bulk_tester import BulkTester

@app.route('/process-batch-parallel', methods=['POST'])
def process_batch_parallel():
    data = request.json
    images_base64 = data.get('images', [])
    
    tester = BulkTester()
    # Use existing parallel processing
    results = tester.test_function(
        function_name='process_image_for_submission',
        images=images_base64,
        max_workers=9
    )
    
    return jsonify(results)
```

---

## 📊 Performance Comparison

### Current (Sequential):
- 9 images × 2 seconds/image = **18 seconds**

### With Parallel (9 workers):
- 9 images ÷ 9 workers = **~2 seconds total**

**Speedup: ~9x faster**

---

## ✅ Recommendation

**Update `/process-batch` endpoint** to use `ThreadPoolExecutor` with `max_workers=9` to process all 9 images simultaneously.

This will:
- ✅ Process all 9 images at the same time
- ✅ Maintain API compatibility
- ✅ Return results in order
- ✅ Handle errors gracefully

---

## 🚀 Next Steps

1. Update `functions_python/main.py` `/process-batch` endpoint
2. Test with 9 images
3. Deploy to Cloud Run
4. Update gallery.html to use parallel batch processing
