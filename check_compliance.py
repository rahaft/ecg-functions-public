"""
Standalone Compliance Checker
Quick check for existing codebase (functions_python/)

Usage:
    python check_compliance.py
"""

import sys
from pathlib import Path

# Add src to path so we can import
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.compliance import check_directory, print_results

if __name__ == '__main__':
    print("🔍 Checking compliance in functions_python/ directory...\n")
    
    # Check functions_python directory
    functions_python_dir = Path(__file__).parent / 'functions_python'
    
    if not functions_python_dir.exists():
        print(f"❌ Error: Directory not found: {functions_python_dir}")
        sys.exit(1)
    
    results = check_directory(functions_python_dir)
    print_results(results, verbose=True)
    
    # Exit with error code if violations found
    sys.exit(1 if results else 0)
