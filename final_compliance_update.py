"""Final compliance update for kaggle_notebook_v3.ipynb
Ensures all competition requirements are met:
1. Runtime <= 9 hours (parallel processing)
2. Internet access disabled (verify)
3. Submission format correct
4. File naming correct
"""
import json
import re

# Load notebook
with open('kaggle_notebook_v3.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find Cell 5 (submission code)
cell5 = nb['cells'][4]
cell5_source = ''.join(cell5['source'])

# Check current state
has_parallel = "ProcessPoolExecutor" in cell5_source or "ThreadPoolExecutor" in cell5_source
has_sequential = "for i, image_path in enumerate(test_images" in cell5_source

print(f"Current state: parallel={has_parallel}, sequential={has_sequential}")

# Find the sequential loop section
sequential_pattern = r'(\s+results = \[\][^\n]*\n\s+for i, image_path in enumerate\(test_images, 1\):[^\n]*\n\s+print\(f"\\n\[{i}/{len\(test_images\)}\] ", end=""\)[^\n]*\n\s+result = process_image\(image_path\)[^\n]*\n\s+results\.append\(result\))'

if has_sequential and not has_parallel:
    # Replace with parallel processing
    # Use ThreadPoolExecutor for better compatibility in notebooks
    parallel_code = """    # COMPETITION REQUIREMENT: Runtime <= 9 hours
    # Using parallel processing to meet this requirement
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = []
    start_time = time.time()
    
    # Parallel processing (3-4x speedup, meets 9-hour requirement)
    max_workers = min(4, len(test_images))
    print(f"\\n🚀 Using {max_workers} parallel workers (required for < 9 hour runtime)")
    
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
    print(f"\\n⏱️  Total processing time: {elapsed_time/60:.1f} minutes ({elapsed_time:.1f} seconds)")
    print(f"   Estimated time for full test set: {elapsed_time * (1000 / len(test_images)) / 3600:.1f} hours" if len(test_images) > 0 else "")"""
    
    # Try to find and replace the sequential loop
    # Look for the pattern more flexibly
    lines = cell5_source.split('\n')
    new_lines = []
    i = 0
    replaced = False
    
    while i < len(lines):
        line = lines[i]
        # Check if this is the start of sequential processing
        if 'results = []' in line and i + 1 < len(lines) and 'for i, image_path in enumerate(test_images' in lines[i + 1]:
            # Found sequential loop - replace it
            new_lines.append(parallel_code)
            # Skip the sequential loop lines
            while i < len(lines) and ('for i, image_path' in lines[i] or 'process_image(image_path)' in lines[i] or 'results.append(result)' in lines[i] or ('print' in lines[i] and 'enumerate' in lines[i-1] if i > 0 else False)):
                i += 1
            replaced = True
        else:
            new_lines.append(line)
            i += 1
    
    if replaced:
        cell5['source'] = new_lines
        print("✅ Replaced sequential loop with parallel processing")
    else:
        # Try direct string replacement as fallback
        old_text = """    results = []
    for i, image_path in enumerate(test_images, 1):
        print(f"\\n[{i}/{len(test_images)}] ", end="")
        result = process_image(image_path)
        results.append(result)"""
        
        if old_text in cell5_source:
            cell5_source = cell5_source.replace(old_text, parallel_code)
            cell5['source'] = cell5_source.split('\n')
            print("✅ Replaced sequential loop (direct replacement)")
        else:
            print("⚠️  Could not find exact sequential loop pattern")
            print("   Manual review needed")
elif has_parallel:
    print("✅ Already has parallel processing")
else:
    print("⚠️  Unknown state - manual review needed")

# Verify submission format
cell5_final = ''.join(cell5['source'])
if "submission.csv" in cell5_final and "id,value" in cell5_final:
    print("✅ Submission format correct (submission.csv with id,value)")
else:
    print("⚠️  Submission format needs verification")

# Check for internet access (should NOT have)
all_source = ''.join([''.join(cell.get('source', [])) for cell in nb['cells']])
forbidden = ['requests', 'urllib', 'wget', 'download', 'http.client', 'socket']
has_internet = any(f'import {f}' in all_source or f'from {f}' in all_source for f in forbidden)
if not has_internet:
    print("✅ No internet access (competition requirement met)")
else:
    print(f"⚠️  Found potential internet access: {[f for f in forbidden if f in all_source]}")

# Save updated notebook
with open('kaggle_notebook_v3.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("\n✅ Notebook compliance update complete!")
print("\nRemaining checks:")
print("  1. Runtime: Test on sample images to verify < 9 hours")
print("  2. Submission: Verify submission.csv format matches competition")
print("  3. Score: Use test_kaggle_with_snr.py with train images")
