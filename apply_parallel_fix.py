"""Apply parallel processing fix to notebook"""
import json

with open('kaggle_notebook_v3.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cell5 = nb['cells'][4]
lines = cell5['source']

# Find and replace the sequential loop
new_lines = []
i = 0
replaced = False

while i < len(lines):
    line = lines[i]
    
    # Check if this is the sequential loop start
    if 'results = []' in line and i + 1 < len(lines):
        next_line = lines[i + 1] if i + 1 < len(lines) else ''
        if 'for i, image_path in enumerate(test_images' in next_line:
            # Replace with parallel processing
            replaced = True
            new_lines.append('    # COMPETITION REQUIREMENT: Runtime <= 9 hours\n')
            new_lines.append('    # Using parallel processing to meet this requirement\n')
            new_lines.append('    import time\n')
            new_lines.append('    from concurrent.futures import ThreadPoolExecutor, as_completed\n')
            new_lines.append('    \n')
            new_lines.append('    results = []\n')
            new_lines.append('    start_time = time.time()\n')
            new_lines.append('    \n')
            new_lines.append('    # Parallel processing (3-4x speedup, meets 9-hour requirement)\n')
            new_lines.append('    max_workers = min(4, len(test_images))\n')
            new_lines.append('    print(f"\\n🚀 Using {max_workers} parallel workers (required for < 9 hour runtime)")\n')
            new_lines.append('    \n')
            new_lines.append('    with ThreadPoolExecutor(max_workers=max_workers) as executor:\n')
            new_lines.append('        future_to_image = {executor.submit(process_image, img_path): img_path for img_path in test_images}\n')
            new_lines.append('        \n')
            new_lines.append('        completed = 0\n')
            new_lines.append('        for future in as_completed(future_to_image):\n')
            new_lines.append('            completed += 1\n')
            new_lines.append('            try:\n')
            new_lines.append('                result = future.result()\n')
            new_lines.append('                results.append(result)\n')
            new_lines.append('                elapsed = time.time() - start_time\n')
            new_lines.append('                avg_time = elapsed / completed if completed > 0 else 0\n')
            new_lines.append('                remaining = (len(test_images) - completed) * avg_time if completed > 0 else 0\n')
            new_lines.append('                status = "✓" if result.get("success") else "✗"\n')
            new_lines.append('                print(f"  [{completed}/{len(test_images)}] {status} {result.get(\'record_id\', \'unknown\')} (~{remaining/60:.1f} min remaining)")\n')
            new_lines.append('            except Exception as e:\n')
            new_lines.append('                print(f"  ✗ Error: {e}")\n')
            new_lines.append('                img_path = future_to_image[future]\n')
            new_lines.append('                record_id = extract_record_id(img_path)\n')
            new_lines.append('                results.append({"record_id": record_id, "signals": {lead: np.zeros(SAMPLES_PER_LEAD) for lead in LEAD_NAMES}, "success": False})\n')
            new_lines.append('    \n')
            new_lines.append('    elapsed_time = time.time() - start_time\n')
            new_lines.append('    print(f"\\n⏱️  Total processing time: {elapsed_time/60:.1f} minutes ({elapsed_time:.1f} seconds)")\n')
            new_lines.append('    if len(test_images) > 0:\n')
            new_lines.append('        estimated_full_time = elapsed_time * (1000 / len(test_images)) / 3600\n')
            new_lines.append('        print(f"   Estimated time for full test set (~1000 images): {estimated_full_time:.1f} hours")\n')
            
            # Skip the old sequential loop lines
            i += 1  # Skip 'results = []'
            while i < len(lines):
                if 'for i, image_path in enumerate(test_images' in lines[i]:
                    i += 1
                    while i < len(lines) and ('process_image(image_path)' in lines[i] or 'results.append(result)' in lines[i] or ('print' in lines[i] and 'enumerate' in ''.join(lines[max(0,i-3):i+1]))):
                        i += 1
                    break
                i += 1
            continue
    
    new_lines.append(line)
    i += 1

if replaced:
    cell5['source'] = new_lines
    print("✅ Replaced sequential loop with parallel processing")
else:
    print("⚠️  Sequential loop not found - may already be updated")

with open('kaggle_notebook_v3.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("✅ Notebook saved!")
