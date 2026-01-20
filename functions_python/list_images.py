"""
List available images for testing transformations
"""

import os
import sys
import glob

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def main():
    print("=" * 60)
    print("AVAILABLE IMAGES FOR TESTING")
    print("=" * 60)
    
    # Find all image files
    image_extensions = ['*.png', '*.jpg', '*.jpeg']
    images = []
    
    for ext in image_extensions:
        images.extend(glob.glob(ext))
        images.extend(glob.glob(ext.upper()))
    
    if not images:
        print("\n❌ No image files found in current directory")
        print("\nTo get a test image:")
        print("1. Go to: https://hv-ecg.web.app/gallery.html")
        print("2. Right-click any ECG image → Save image as...")
        print("3. Save it to this folder (functions_python)")
        print("4. Run: python test_transformations.py your_image.png")
        print("\nOr use the sample:")
        print("   python test_transformations.py --sample")
        return
    
    print(f"\nFound {len(images)} image file(s):\n")
    
    for i, img in enumerate(images, 1):
        size = os.path.getsize(img) / 1024  # KB
        print(f"{i}. {img}")
        print(f"   Size: {size:.1f} KB")
        print(f"   Test: python test_transformations.py {img}\n")
    
    print("=" * 60)
    print("QUICK TEST COMMANDS")
    print("=" * 60)
    
    if images:
        first_image = images[0]
        print(f"\nTest with first image:")
        print(f"  python test_transformations.py {first_image}")
    
    print(f"\nCreate sample image:")
    print(f"  python test_transformations.py --sample")

if __name__ == '__main__':
    main()
