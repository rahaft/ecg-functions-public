# Testing Guide: How to Test Output and Get SNR

## Quick Answer

**To test output and get SNR:**

1. **For estimated SNR (works with any image):**
   - Use the pipeline's built-in quality metrics
   - Already calculated in `result['metadata']['quality']['mean_snr']`

2. **For actual SNR (requires train images with ground truth):**
   - Use `test_kaggle_with_snr.py` script
   - Requires train images (test images have no ground truth)

3. **Simple testing in notebook:**
   - Use `TEST_AND_VALIDATE.py` (copy into a cell)

---

## Method 1: Quick Test in Notebook (Simplest)

### Step 1: Add Test Cell

Copy `TEST_AND_VALIDATE.py` into a new cell in your Kaggle notebook.

### Step 2: Test an Image

```python
# Test a single image
result = quick_test('/kaggle/input/physionet-ecg-image-digitization/train/62.jpg')
```

**Output:**
- Shows extracted signals (12 plots)
- Displays estimated SNR from pipeline
- Shows per-lead SNR values

### Step 3: Get SNR Value

```python
# Get SNR estimate
snr = result['mean_snr']
print(f"Estimated SNR: {snr:.2f} dB")
```

---

## Method 2: Use Built-in Quality Metrics

The pipeline already calculates SNR estimate in `calculate_quality_metrics()`:

```python
# Process image
digitizer = ECGDigitizer()
result = digitizer.process_image('image.jpg')

# Get SNR
quality = result['metadata']['quality']
mean_snr = quality['mean_snr']  # Overall SNR
min_snr = quality['min_snr']     # Worst lead SNR
lead_snrs = quality['lead_snrs'] # Per-lead SNR

print(f"Mean SNR: {mean_snr:.2f} dB")
print(f"Min SNR: {min_snr:.2f} dB")
```

**Note:** This is an **estimated SNR** based on signal characteristics, not comparison to ground truth.

---

## Method 3: Calculate Actual SNR vs Ground Truth

### Requirements:
- **Train images** (test images have no ground truth)
- **Ground truth file** (`train.parquet` or `train.csv`)

### Option A: Use Test Script

```bash
# In Kaggle notebook
!python test_kaggle_with_snr.py --limit 5
```

This will:
1. Process train images
2. Load ground truth
3. Calculate actual SNR using competition method
4. Save results to CSV

### Option B: Use Test Function in Notebook

```python
# Copy TEST_AND_VALIDATE.py into a cell first

# Process image
result = test_single_image('train/62.jpg', show_plot=False)

# Calculate actual SNR vs ground truth
gt_path = '/kaggle/input/physionet-ecg-image-digitization/train.parquet'
record_id = '62'  # Extract from filename
actual_snr = calculate_snr_vs_ground_truth(
    result['signals'], 
    gt_path, 
    record_id
)

print(f"Actual SNR: {actual_snr:.2f} dB")
```

---

## Understanding SNR Values

### Estimated SNR (from pipeline)
- Based on signal characteristics
- No ground truth required
- Useful for relative comparison
- May not match actual competition score

### Actual SNR (vs ground truth)
- Uses competition's evaluation method
- Requires ground truth data
- Matches competition scoring
- Only works with train images

### SNR Interpretation

| SNR (dB) | Quality | Meaning |
|----------|---------|---------|
| < 0 | Very poor | Signals don't match |
| 0-10 | Poor | Basic structure extracted |
| 10-20 | Moderate | Good digitization |
| 20-30 | Good | High quality |
| > 30 | Excellent | Near-perfect |

**Target:** Aim for SNR > 15 dB for competitive results.

---

## Test Images vs Train Images

### Test Images
- ❌ **NO ground truth available**
- ✅ Can process and extract signals
- ✅ Can get estimated SNR from pipeline
- ❌ Cannot calculate actual SNR
- ✅ Use for final submission

### Train Images
- ✅ **Have ground truth**
- ✅ Can process and extract signals
- ✅ Can get estimated SNR from pipeline
- ✅ **Can calculate actual SNR**
- ✅ Use for validation and testing

---

## Quick Test Examples

### Example 1: Test Single Image (Estimated SNR)

```python
# In your notebook
from pathlib import Path

# Process image
image_path = '/kaggle/input/physionet-ecg-image-digitization/train/62.jpg'
digitizer = ECGDigitizer()
result = digitizer.process_image(image_path)

# Get SNR
snr = result['metadata']['quality']['mean_snr']
print(f"Estimated SNR: {snr:.2f} dB")
```

### Example 2: Test Multiple Images

```python
# Test multiple images
test_images = [
    '/kaggle/input/physionet-ecg-image-digitization/train/62.jpg',
    '/kaggle/input/physionet-ecg-image-digitization/train/63.jpg',
    '/kaggle/input/physionet-ecg-image-digitization/train/64.jpg',
]

snr_values = []
for img_path in test_images:
    result = digitizer.process_image(img_path)
    snr = result['metadata']['quality']['mean_snr']
    snr_values.append(snr)
    print(f"{Path(img_path).name}: {snr:.2f} dB")

print(f"\nMean SNR: {np.mean(snr_values):.2f} dB")
```

### Example 3: Visualize Signals

```python
# Process and plot
result = digitizer.process_image('train/62.jpg')

# Plot all leads
import matplotlib.pyplot as plt

fig, axes = plt.subplots(4, 3, figsize=(15, 12))
axes = axes.flatten()

for idx, lead_data in enumerate(result['leads']):
    ax = axes[idx]
    signal = np.array(lead_data['values'])
    time = np.arange(len(signal)) / 500  # 500 Hz sampling rate
    
    ax.plot(time, signal)
    ax.set_title(f"Lead {lead_data['name']}")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (mV)")

plt.tight_layout()
plt.show()
```

---

## Troubleshooting

### "No ground truth found"
- **Solution:** Use train images, not test images
- Test images don't have ground truth

### "Pipeline not available"
- **Solution:** Make sure `ECGDigitizer` is defined in previous cells
- Run cells 1-4 before testing

### Low SNR values
- Check signal extraction quality
- Verify calibration parameters
- Check if leads are detected correctly
- Compare visually with ground truth

### SNR calculation fails
- Verify ground truth file exists
- Check record ID matches between image and ground truth
- Ensure ground truth format is correct

---

## Files Available

1. **`TEST_AND_VALIDATE.py`** - Simple test functions for notebook
2. **`test_kaggle_with_snr.py`** - Full test script with SNR calculation
3. **`TEST_KAGGLE_IMAGES_GUIDE.md`** - Detailed guide for test script

---

## Next Steps

1. **Test on train images** to validate your pipeline
2. **Calculate actual SNR** to see how you compare to ground truth
3. **Optimize parameters** based on SNR feedback
4. **Generate submission** once SNR is acceptable
5. **Submit to Kaggle** and compare with leaderboard

---

## Summary

- ✅ **Estimated SNR:** Already in pipeline output (`result['metadata']['quality']['mean_snr']`)
- ✅ **Actual SNR:** Use `test_kaggle_with_snr.py` with train images
- ✅ **Quick test:** Use `TEST_AND_VALIDATE.py` in notebook
- ⚠️ **Test images:** No ground truth - can't calculate actual SNR
- ✅ **Train images:** Have ground truth - can calculate actual SNR
