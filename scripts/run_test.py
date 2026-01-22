"""
Run Test Script
Quick script to test the pipeline and view results
"""

import sys
import os
from pathlib import Path

# Add functions_python to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'functions_python'))

from test_pipeline import test_single_image, interactive_test
from view_results import view_results


def main():
    """Main test runner"""
    print("ECG Digitization Pipeline - Test Runner")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python scripts/run_test.py test <image_path>     - Test single image")
        print("  python scripts/run_test.py view [results_dir]   - View results in browser")
        print("  python scripts/run_test.py interactive           - Interactive mode")
        return
    
    command = sys.argv[1]
    
    if command == "test":
        if len(sys.argv) < 3:
            print("Error: Please provide image path")
            print("Usage: python scripts/run_test.py test <image_path>")
            return
        
        image_path = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else 'data/test_output'
        
        try:
            test_single_image(image_path, output_dir)
            print("\n✓ Test completed! View results with:")
            print(f"  python scripts/run_test.py view {output_dir}")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    elif command == "view":
        results_dir = sys.argv[2] if len(sys.argv) > 2 else 'data/test_output'
        view_results(results_dir)
    
    elif command == "interactive":
        interactive_test()
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: test, view, interactive")


if __name__ == "__main__":
    main()
