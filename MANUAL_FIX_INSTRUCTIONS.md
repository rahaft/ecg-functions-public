# Manual Fix Instructions for Version 3 Notebook

## Critical Fix Needed: Parallel Processing

The notebook still has **sequential processing** which will likely exceed 9 hours. You need to replace it with **parallel processing**.

## What to Fix

### Location: Cell 5 (the submission code cell)

### Find This Code:
```python
    # Process images
    print(f"\n{'=' * 70}")
    print(f"Processing {len(test_images)} image(s)...")
    print(f"{'=' * 70}")
    results = []
    for i, image_path in enumerate(test_images, 1):
        print(f"\n[{i}/{len(test_images)}] ", end="")
        result = process_image(image_path)
        results.append(result)
```

### Replace With This Code:
```python
    # Process images
    print(f"\n{'=' * 70}")
    print(f"Processing {len(test_images)} image(s)...")
    print(f"{'=' * 70}")
    
    # COMPETITION REQUIREMENT: Runtime <= 9 hours
    # Using parallel processing to meet this requirement
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = []
    start_time = time.time()
    
    # Parallel processing (3-4x speedup, meets 9-hour requirement)
    max_workers = min(4, len(test_images))
    print(f"\n🚀 Using {max_workers} parallel workers (required for < 9 hour runtime)")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_image = {executor.submit(process_image, img_path): img_path for img_path in test_images}
        
        completed = 0
        for future in as_completed(future_to_image):
            completed += 1
            try:
                result = future.result()
                results.append(result)
                elapsed = time.time() - start_time
                avg_time = elapsed / completed if completed > 0 else 0
                remaining = (len(test_images) - completed) * avg_time if completed > 0 else 0
                status = "✓" if result.get("success") else "✗"
                print(f"  [{completed}/{len(test_images)}] {status} {result.get('record_id', 'unknown')} (~{remaining/60:.1f} min remaining)")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                img_path = future_to_image[future]
                record_id = extract_record_id(img_path)
                results.append({"record_id": record_id, "signals": {lead: np.zeros(SAMPLES_PER_LEAD) for lead in LEAD_NAMES}, "success": False})
    
    elapsed_time = time.time() - start_time
    print(f"\n⏱️  Total processing time: {elapsed_time/60:.1f} minutes ({elapsed_time:.1f} seconds)")
    if len(test_images) > 0:
        estimated_full_time = elapsed_time * (1000 / len(test_images)) / 3600
        print(f"   Estimated time for full test set (~1000 images): {estimated_full_time:.1f} hours")
```

## Steps

1. Open `kaggle_notebook_v3.ipynb` in your editor
2. Find Cell 5 (the submission code cell)
3. Locate the sequential loop (starts with `results = []` and `for i, image_path in enumerate`)
4. Replace it with the parallel processing code above
5. Save the notebook

## Verification

After fixing, search for `ThreadPoolExecutor` in the notebook - it should be found in Cell 5.

---

## How to Test Expected Score

### Quick Answer

**Test on TRAIN images** (they have ground truth), not test images (no ground truth).

### Command

```bash
python test_kaggle_with_snr.py --limit 10
```

**What it does:**
1. Processes **train images** (input)
2. Loads **ground truth** from `train.parquet`
3. Compares prediction vs ground truth
4. Calculates **SNR** (your expected score)

**Output:**
```
Mean SNR: 14.56 dB    ← This is your expected competition score
```

### Why Train Images?

- **Train images** = Have image + ground truth → Can calculate score
- **Test images** = Have image only, NO ground truth → Cannot calculate score

You use train images to estimate what score you'll get on test images.

---

## Summary

1. **Fix notebook:** Replace sequential loop with parallel processing (see above)
2. **Test score:** Run `python test_kaggle_with_snr.py --limit 10` on train images
3. **Upload:** Upload fixed notebook to Kaggle
4. **Submit:** Once score looks good!
