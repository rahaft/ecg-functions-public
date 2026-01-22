# Function Documentation Template

Use this template to document each function/process in the ECG digitization pipeline.

---

## Function Name: [Function Name]

### Purpose
[What this function does and why it exists]

### Location
- **File:** `path/to/file.py`
- **Class/Module:** `ClassName` or `module_name`
- **Function:** `function_name()`

### Dependencies
- **Required:** `numpy`, `cv2`, etc.
- **Optional:** `optional_library`
- **Notebook-ready:** Yes/No

### Function Signature
```python
def function_name(param1: type, param2: type = default) -> return_type:
    """
    Brief description.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description
    """
```

### How It Works

#### Algorithm/Approach
1. Step 1 description
2. Step 2 description
3. Step 3 description

#### Key Components
- **Component 1:** Description
- **Component 2:** Description

#### Processing Flow
```
Input → Step 1 → Step 2 → Step 3 → Output
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `param1` | `type` | `default` | Description |
| `param2` | `type` | `default` | Description |

### Returns

| Field | Type | Description |
|-------|------|-------------|
| `field1` | `type` | Description |
| `field2` | `type` | Description |

### Usage Example

```python
# Example code
result = function_name(param1, param2)
print(result)
```

### What Works ✅

- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

### What Didn't Work ❌

- **Issue 1:** Description
  - **Why:** Explanation
  - **Alternative:** What was tried instead

- **Issue 2:** Description
  - **Why:** Explanation
  - **Alternative:** What was tried instead

### Changes Made 🔄

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | YYYY-MM-DD | Initial implementation | - |
| v1.1 | YYYY-MM-DD | Added feature X | To improve Y |
| v1.2 | YYYY-MM-DD | Fixed bug Z | Issue reported |

### Performance

- **Average execution time:** X ms
- **Memory usage:** Y MB
- **Scalability:** Handles up to Z images in parallel

### Edge Cases Handled

- Case 1: Description of how it's handled
- Case 2: Description of how it's handled

### Known Limitations

- Limitation 1: Description
- Limitation 2: Description

### Testing

#### Unit Tests
- [ ] Test case 1
- [ ] Test case 2

#### Integration Tests
- [ ] Integration with component X
- [ ] Integration with component Y

#### Bulk Testing
```python
# Bulk test example
from bulk_tester import BulkTester

tester = BulkTester()
await tester.test_function(
    function=function_name,
    image_paths=['img1.png', 'img2.png'],
    test_name='function_name_test'
)
```

### Related Functions

- `related_function_1()` - Description
- `related_function_2()` - Description

### References

- Paper/article link
- Documentation link
- Related code

---

## Example: Edge Detection

### Purpose
Detect image boundaries and edges for ECG image preprocessing. Used to crop unnecessary borders and improve processing accuracy.

### Location
- **File:** `functions_python/transformers/edge_detector.py`
- **Class:** `EdgeDetector`
- **Function:** `detect_edges()`, `crop_to_content()`

### Dependencies
- **Required:** `numpy`, `cv2`
- **Notebook-ready:** Yes

### How It Works

#### Algorithm
1. Convert image to grayscale
2. Apply Canny edge detection with adaptive thresholds
3. Apply morphological operations to clean up edges
4. Find contours and bounding box

#### Key Components
- **Canny Edge Detection:** Primary edge detection method
- **Morphological Operations:** Clean up edge map
- **Contour Detection:** Find image boundaries

### What Works ✅

- Canny edge detection with adaptive thresholds
- Morphological cleanup of edge maps
- Bounding box detection for cropping

### What Didn't Work ❌

- **Simple thresholding:** Too sensitive to noise
  - **Why:** ECG images have varying contrast
  - **Alternative:** Switched to adaptive Canny with morphological operations

- **Sobel edge detection alone:** Too many false edges
  - **Why:** Grid lines interfere with edge detection
  - **Alternative:** Combined with morphological operations

### Changes Made 🔄

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-01-21 | Initial implementation | - |
| v1.1 | 2026-01-21 | Added adaptive thresholding | Improve edge detection accuracy |
| v1.2 | 2026-01-21 | Added morphological operations | Clean up edge maps |

### Performance

- **Average execution time:** 50-100 ms per image
- **Memory usage:** ~10 MB per image
- **Scalability:** Can process 10+ images in parallel

---

*Template Version: 1.0*  
*Last Updated: January 21, 2026*
