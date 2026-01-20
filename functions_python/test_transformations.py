"""
Quick test script for transformation methods
Usage: python test_transformations.py <image_path>
"""

import cv2
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from transformers.multi_method_processor import MultiMethodProcessor

def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("ECG Transformation Methods Test")
        print("=" * 60)
        print("\nUsage: python test_transformations.py <image_path>")
        print("\nExample:")
        print("  python test_transformations.py ../test_images/ecg_sample.png")
        print("\nOr test with a sample:")
        print("  python test_transformations.py --sample")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Handle sample flag
    if image_path == '--sample':
        print("Creating sample test image...")
        # Create a simple test image with grid
        image = create_sample_image()
        image_path = 'sample_ecg.png'
        cv2.imwrite(image_path, image)
        print(f"Created: {image_path}")
    
    # Load image
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)
    
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("ECG TRANSFORMATION TEST")
    print("=" * 60)
    print(f"\nImage: {image_path}")
    print(f"Size: {image.shape[1]}x{image.shape[0]} pixels")
    print(f"Channels: {image.shape[2] if len(image.shape) > 2 else 1}")
    
    print("\nProcessing with all transformation methods...")
    print("This may take a few moments...\n")
    
    try:
        # Process with all methods
        processor = MultiMethodProcessor()
        results = processor.process_all_methods(image)
        
        # Display results
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        
        print(f"\nTotal processing time: {results['total_processing_time']:.2f} seconds")
        print(f"Methods tested: {', '.join(results['methods_tested'])}")
        
        if results['best_method']:
            print(f"\n🏆 BEST METHOD: {results['best_method'].upper()}")
        else:
            print("\n⚠️  No method succeeded")
        
        # Display rankings
        print("\n" + "-" * 60)
        print("RANKINGS (sorted by combined score)")
        print("-" * 60)
        print(f"{'Rank':<6} {'Method':<15} {'Score':<8} {'R²':<8} {'RMSE':<10} {'Quality':<12} {'Time':<8}")
        print("-" * 60)
        
        for i, ranking in enumerate(results['rankings']):
            rank_icon = "🏆" if i == 0 else f"{i+1}."
            print(f"{rank_icon:<6} {ranking['method']:<15} "
                  f"{ranking['combined_score']:<8.3f} "
                  f"{ranking['r2']:<8.3f} "
                  f"{ranking['rmse']:<10.2f} "
                  f"{ranking['quality']:<12} "
                  f"{ranking['processing_time']:<8.2f}s")
        
        # Display detailed results for each method
        print("\n" + "-" * 60)
        print("DETAILED RESULTS")
        print("-" * 60)
        
        for method_name, result in results['results'].items():
            print(f"\n{method_name.upper()}:")
            if result.get('success'):
                metrics = result.get('metrics', {})
                print(f"  ✅ Success")
                print(f"  R²: {metrics.get('r2', 0):.3f}")
                print(f"  RMSE: {metrics.get('rmse', 0):.2f} pixels")
                print(f"  MAE: {metrics.get('mae', 0):.2f} pixels")
                print(f"  Max Error: {metrics.get('max_error', 0):.2f} pixels")
                print(f"  Quality: {metrics.get('quality', 'unknown')}")
                print(f"  Processing Time: {result.get('processing_time', 0):.2f}s")
                
                # Save transformed image
                if 'transformed_image' in result:
                    output_path = f"transformed_{method_name}.png"
                    cv2.imwrite(output_path, result['transformed_image'])
                    print(f"  💾 Saved: {output_path}")
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Save best result
        if results['best_method']:
            best_result = results['results'][results['best_method']]
            if best_result.get('success') and 'transformed_image' in best_result:
                output_path = "best_transformation.png"
                cv2.imwrite(output_path, best_result['transformed_image'])
                print(f"\n✅ Best transformation saved to: {output_path}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_sample_image():
    """Create a simple test image with a grid pattern"""
    import numpy as np
    
    width, height = 800, 600
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Draw grid lines (red/pink for ECG style)
    line_color = (200, 100, 100)  # BGR format
    
    # Horizontal lines
    for y in range(0, height, 20):
        cv2.line(image, (0, y), (width, y), line_color, 1)
    
    # Vertical lines
    for x in range(0, width, 20):
        cv2.line(image, (x, 0), (x, height), line_color, 1)
    
    # Thicker lines every 5 (large squares)
    thick_color = (150, 50, 50)
    for y in range(0, height, 100):
        cv2.line(image, (0, y), (width, y), thick_color, 2)
    for x in range(0, width, 100):
        cv2.line(image, (x, 0), (x, height), thick_color, 2)
    
    # Add some "signal" (simulated ECG trace)
    signal_color = (0, 0, 0)
    center_y = height // 2
    points = []
    for x in range(0, width, 2):
        y = center_y + int(30 * np.sin(x / 20) + 20 * np.sin(x / 5))
        points.append((x, y))
    
    for i in range(len(points) - 1):
        cv2.line(image, points[i], points[i+1], signal_color, 2)
    
    return image

if __name__ == '__main__':
    main()
