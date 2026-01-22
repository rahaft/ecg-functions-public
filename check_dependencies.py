"""Quick dependency check for live test server"""

print("Checking dependencies for live test server...")
print("-" * 50)

deps = {
    'flask': 'pip install flask',
    'cv2': 'pip install opencv-python',
    'numpy': 'pip install numpy',
    'scipy': 'pip install scipy',
    'matplotlib': 'pip install matplotlib',
    'sklearn': 'pip install scikit-learn',
    'pandas': 'pip install pandas'
}

all_ok = True

for module, install_cmd in deps.items():
    try:
        if module == 'cv2':
            import cv2
            print(f"✓ {module:12} OK (version {cv2.__version__})")
        elif module == 'sklearn':
            import sklearn
            print(f"✓ {module:12} OK")
        else:
            __import__(module)
            print(f"✓ {module:12} OK")
    except ImportError:
        print(f"✗ {module:12} MISSING - Run: {install_cmd}")
        all_ok = False

print("-" * 50)

if all_ok:
    print("\n✅ All dependencies are installed!")
    print("You can start the live test server with:")
    print("  cd functions_python")
    print("  python live_test_server.py")
else:
    print("\n⚠️  Some dependencies are missing.")
    print("Install missing packages, then try again.")
