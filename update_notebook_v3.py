"""Update notebook v3 with parallel processing for 9-hour requirement"""
import json

# Load notebook
with open('kaggle_notebook_v3.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find Cell 5 (index 4, 0-based)
cell5 = nb['cells'][4]
cell5_source = ''.join(cell5['source'])

# Old sequential loop
old_loop = """    results = []
    for i, image_path in enumerate(test_images, 1):
        print(f"\\n[{i}/{len(test_images)}] ", end="")
        result = process_image(image_path)
        results.append(result)"""

# New parallel processing loop
new_loop = """    # OPTIMIZED: Parallel processing for < 9 hour runtime requirement
    import time
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import multiprocessing
    
    results = []
    start_time = time.time()
    
    # Try parallel processing first (faster, meets 9-hour requirement)
    try:
        max_workers = min(4, len(test_images), multiprocessing.cpu_count())
        print(f"\\n🚀 Using {max_workers} parallel workers (required for < 9 hour runtime)")
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
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
        print(f"\\n⏱️  Total processing time: {elapsed_time/60:.1f} minutes ({elapsed_time:.1f} seconds)")
        
    except Exception as e:
        # Fallback to sequential if parallel fails
        print(f"\\n⚠️  Parallel processing failed: {e}")
        print("   Falling back to sequential processing...")
        results = []
        for i, image_path in enumerate(test_images, 1):
            print(f"\\n[{i}/{len(test_images)}] ", end="")
            result = process_image(image_path)
            results.append(result)"""

# Replace in cell 5
if old_loop in cell5_source:
    cell5_source = cell5_source.replace(old_loop, new_loop)
    cell5['source'] = cell5_source.split('\n')
    print("✅ Updated Cell 5 with parallel processing")
else:
    print("⚠️  Could not find exact match for sequential loop")
    print("   Checking if already updated...")
    if "ProcessPoolExecutor" in cell5_source:
        print("   ✅ Already has parallel processing!")
    else:
        print("   ❌ Sequential loop still present")

# Save updated notebook
with open('kaggle_notebook_v3.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("✅ Notebook updated and saved!")
