# ============================================================================
# PARALLEL PROCESSING CODE - INSERT INTO CELL 5
# ============================================================================
# Replace the sequential loop in Cell 5 with this code
# This meets the competition requirement: Runtime <= 9 hours
# ============================================================================

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

# ============================================================================
# REPLACE THIS SEQUENTIAL CODE:
# ============================================================================
# results = []
# for i, image_path in enumerate(test_images, 1):
#     print(f"\n[{i}/{len(test_images)}] ", end="")
#     result = process_image(image_path)
#     results.append(result)
# ============================================================================
