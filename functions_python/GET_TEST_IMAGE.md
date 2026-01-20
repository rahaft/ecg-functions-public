# How to Get a Test ECG Image

## Option 1: Download from Gallery (Easiest)

1. **Go to the gallery**: https://hv-ecg.web.app/gallery.html
2. **Right-click any image** → "Save image as..." or "Copy image"
3. **Save it** to your `functions_python` folder
4. **Test it**:
   ```bash
   python test_transformations.py saved_image.png
   ```

## Option 2: Use Public GCS URL

Since your buckets are public, you can download directly using a browser or curl:

### Get Image URL from Gallery
1. Open gallery: https://hv-ecg.web.app/gallery.html
2. Right-click an image → "Copy image address"
3. The URL will look like: `https://storage.googleapis.com/ecg-competition-data-X/kaggle-data/physionet-ecg/XXXXX.png`
4. Download it:
   ```bash
   # Using PowerShell
   Invoke-WebRequest -Uri "IMAGE_URL" -OutFile "test_image.png"
   
   # Or use browser to download
   ```

## Option 3: Use Sample Image (Already Created)

You already have a sample image from the test:
- `sample_ecg.png` - Simple test image (low quality scores expected)

Test it:
```bash
python test_transformations.py sample_ecg.png
```

## Option 4: Set Up GCS Authentication (For Direct Download)

If you want to download directly from Python:

1. **Set up authentication** (see GCS_QUICK_START.md):
   ```bash
   # Set environment variable
   $env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
   ```

2. **Then run**:
   ```bash
   python download_test_image.py
   ```

## Quick Test Command

Once you have an image file in `functions_python` folder:

```bash
# Test with any image
python test_transformations.py your_image.png

# Test with sample (already exists)
python test_transformations.py sample_ecg.png
```

## Recommended: Use Gallery Method

**Easiest way:**
1. Open https://hv-ecg.web.app/gallery.html
2. Right-click any ECG image
3. Save it to `functions_python` folder
4. Run: `python test_transformations.py saved_image.png`

This gives you a real ECG image with proper grid lines for testing!
