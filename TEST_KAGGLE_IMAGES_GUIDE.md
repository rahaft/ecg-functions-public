# Testing Kaggle Images with SNR Calculation

This guide explains how to test your digitization pipeline on Kaggle competition images and calculate Signal-to-Noise Ratio (SNR) against ground truth.

## Overview

The `test_kaggle_with_snr.py` script:
1. ✅ Loads test images from Kaggle competition
2. ✅ Processes them through your digitization pipeline
3. ✅ Loads ground truth signals from competition data
4. ✅ Calculates SNR using the competition's alignment method
5. ✅ Generates a results report

## Prerequisites

### 1. Kaggle Competition Data

You need access to the competition data:
- **Images**: ECG images from the train set (test set doesn't have ground truth)
- **Ground Truth**: Signal data in `train.parquet` or `train.csv` format

### 2. Data Structure

The script looks for data in these locations:

**In Kaggle Notebook:**
```
/kaggle/input/physionet-ecg-image-digitization/
├── train/
│   ├── 62.jpg
│   ├── 63.jpg
│   └── ...
└── train.parquet  (or train.csv)
```

**Locally:**
```
./input/physionet-ecg-image-digitization/
├── train/
│   ├── 62.jpg
│   └── ...
└── train.parquet
```

### 3. Ground Truth Format

Ground truth should be in one of these formats:

**Option 1: Parquet/CSV with ID column**
```csv
id,value
'62_0_I',0.123
'62_1_I',0.234
'62_0_II',0.345
...
```

**Option 2: Parquet/CSV with separate columns**
```csv
record_id,sample,lead,value
62,0,I,0.123
62,1,I,0.234
62,0,II,0.345
...
```

## Usage

### Basic Usage

```bash
# Process first 5 images
python test_kaggle_with_snr.py --limit 5

# Process specific record
python test_kaggle_with_snr.py --record-id 62

# Process 10 images and save to custom file
python test_kaggle_with_snr.py --limit 10 --output my_results.csv
```

### In Kaggle Notebook

```python
# In your Kaggle notebook cell
!python test_kaggle_with_snr.py --limit 5
```

## How SNR is Calculated

The script uses the **competition's alignment method**:

1. **Time Alignment**: Finds optimal horizontal shift (up to ±0.2 seconds) via cross-correlation
2. **Vertical Alignment**: Removes DC offset between signals
3. **Power Calculation**: 
   - Signal power = sum of squared ground truth values
   - Noise power = sum of squared errors
4. **SNR Formula**: `SNR (dB) = 10 × log₁₀(signal_power / noise_power)`
5. **Aggregation**: Powers summed across all 12 leads before calculating SNR

## Output

The script generates:
- **Console output**: Progress and SNR values for each image
- **CSV file**: Results with record_id, image_path, SNR, and leads_extracted

Example output:
```
Processing: /kaggle/input/.../train/62.jpg
Record ID: 62
SNR: 15.23 dB

Summary
============================================================
Processed: 5 images
SNR calculated for: 5 images
Mean SNR: 14.56 dB
Min SNR: 12.34 dB
Max SNR: 16.78 dB

Results saved to: test_results.csv
```

## Troubleshooting

### "No images found"

**Solution:**
1. Check that images are in the correct directory
2. Verify path structure matches expected format
3. In Kaggle: Ensure competition data is added to notebook

### "Ground truth not found"

**Solution:**
1. Verify `train.parquet` or `train.csv` exists
2. Check that record IDs match between images and ground truth
3. Verify ground truth file format (ID parsing)

### "Pipeline not available"

**Solution:**
1. Ensure `functions_python` directory is in Python path
2. Install required dependencies:
   ```bash
   pip install numpy scipy pandas opencv-python pillow
   ```

### Low or Negative SNR

**Possible causes:**
- Signal extraction issues
- Calibration problems
- Misaligned signals
- Missing or incorrect ground truth

**Debug:**
- Check extracted signals visually
- Verify calibration parameters
- Compare predicted vs ground truth signals

## Integration with Submission

After testing, you can generate submission files:

```python
from test_kaggle_submission import generate_from_signals

# Use signals from test results
result = process_image_and_calculate_snr('image.jpg', '62')
signals = result['predicted_signals']

# Generate submission
generate_from_signals('62', signals, 'submission.csv')
```

## Expected SNR Values

Based on competition evaluation:

| SNR (dB) | Quality | Interpretation |
|----------|---------|---------------|
| < 0 | Very poor | Signals don't match |
| 0-10 | Poor | Basic structure extracted |
| 10-20 | Moderate | Good digitization |
| 20-30 | Good | High quality |
| > 30 | Excellent | Near-perfect |

**Target**: Aim for SNR > 15 dB for competitive results.

## Next Steps

1. **Test on multiple images** to get average SNR
2. **Compare different methods** (edge detection, color separation, etc.)
3. **Optimize parameters** based on SNR feedback
4. **Generate submission** once SNR is acceptable
5. **Submit to Kaggle** and compare with leaderboard

## Notes

- **Train set only**: Test set doesn't have ground truth, so use train images for validation
- **Offline requirement**: In Kaggle submission, all code must work offline
- **Time limit**: Processing must complete within 9 hours
- **Sampling rate**: Ensure signals are resampled to 500 Hz (5000 samples for 10 seconds)
