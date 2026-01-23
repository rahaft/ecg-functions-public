# Submit Your Two Test Images to Kaggle

This guide shows you how to process your two test images and create a Kaggle submission.

## Your Test Images

Based on the images you showed:
- **Image 1**: Record ID `16640_hr` (extracted as `16640`)
- **Image 2**: Record ID `17459 hr` (extracted as `17459`)

## Quick Start

### Option 1: Local Testing (Before Kaggle)

1. **Place your test images in a folder:**
   ```
   test_images/
   ├── 16640_hr.jpg  (or .png)
   └── 17459 hr.jpg  (or .png)
   ```

2. **Run the submission script:**
   ```bash
   python create_kaggle_submission.py --test-dir ./test_images
   ```

3. **Check the output:**
   - Creates `submission.csv` in the current directory
   - Shows processing status for each image
   - Displays row count and file size

### Option 2: In Kaggle Notebook

1. **Upload your code to Kaggle:**
   - Copy `create_kaggle_submission.py` to your notebook
   - Or copy `kaggle_submission_notebook.py` (already configured for Kaggle)

2. **Place test images in:**
   ```
   /kaggle/input/physionet-ecg-image-digitization/test/
   ```

3. **Run in notebook:**
   ```python
   # If using create_kaggle_submission.py
   !python create_kaggle_submission.py --test-dir /kaggle/input/physionet-ecg-image-digitization/test --output /kaggle/working/submission.csv
   
   # Or use kaggle_submission_notebook.py
   exec(open('kaggle_submission_notebook.py').read())
   ```

## What the Script Does

1. **Finds test images** in the specified directory
2. **Extracts record IDs** from filenames:
   - `16640_hr.jpg` → `16640`
   - `17459 hr.jpg` → `17459`
3. **Processes each image** through your digitization pipeline
4. **Extracts signals** for all 12 leads
5. **Generates submission.csv** with format:
   ```csv
   id,value
   '16640_0_I',0.123456
   '16640_1_I',0.234567
   ...
   '17459_0_I',0.123456
   ...
   ```

## Expected Output

```
======================================================================
Kaggle ECG Digitization Submission Generator
======================================================================

1. Looking for test images in: ./test_images
Found 2 test image(s):
  - 16640_hr.jpg
  - 17459 hr.jpg

2. Processing 2 image(s)...

Processing: 16640_hr.jpg
  Record ID: 16640
  Running digitization pipeline...
  Lead I: 5000 samples
  Lead II: 5000 samples
  ...
  Successfully extracted 12 leads

Processing: 17459 hr.jpg
  Record ID: 17459
  ...

3. Generating submission file...

Generating submission file: submission.csv
  Writing record 16640...
  Writing record 17459...

  Total rows written: 120000
  Expected rows: 120000
  File size: 2756.23 KB

======================================================================
Submission Complete!
======================================================================
Submission file: submission.csv
Records processed: 2
  ✓ Record 16640: 12 leads extracted
  ✓ Record 17459: 12 leads extracted
```

## Submission File Format

The generated `submission.csv` will have:
- **Header**: `id,value`
- **Rows**: 120,000 total (2 records × 12 leads × 5,000 samples)
- **ID format**: `'{record}_{sample}_{lead}'`
- **Example**: `'16640_0_I',0.123456`

## Troubleshooting

### "No test images found"
- Check that images are in the correct directory
- Verify file extensions (.jpg, .png, etc.)
- Use `--test-dir` to specify custom path

### "Pipeline not available"
- Make sure `functions_python/digitization_pipeline.py` exists
- Check that all dependencies are installed
- Verify Python path includes `functions_python`

### "Error processing image"
- Check error message for details
- Verify image format is supported
- Ensure image is a valid ECG image

### Missing leads
- Script will fill missing leads with zeros
- Check console output for warnings
- Verify digitization pipeline is working correctly

## Validation

Before submitting, verify:

- [ ] File exists: `submission.csv`
- [ ] File size: ~2-3 MB (for 2 records)
- [ ] Row count: 120,000 rows (2 × 12 × 5000)
- [ ] Header: `id,value`
- [ ] ID format: Quoted, like `'16640_0_I'`
- [ ] All 12 leads present for each record
- [ ] Values are floats with 6 decimal places

## Next Steps

1. **Test locally** with `create_kaggle_submission.py`
2. **Verify output** looks correct
3. **Upload to Kaggle** notebook
4. **Run in Kaggle** environment
5. **Commit and submit** via Kaggle UI

## Files

- `create_kaggle_submission.py` - Main submission script (works locally and in Kaggle)
- `kaggle_submission_notebook.py` - Kaggle-optimized version
- `submission.csv` - Generated submission file (created after running)
