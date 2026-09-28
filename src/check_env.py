"""
Temporary environment check script.
Verifies that all required packages can be imported.
This file can be deleted after Stage 1 verification.
"""

import sys

print("=" * 55)
print("ENVIRONMENT CHECK")
print("=" * 55)
print(f"Python version : {sys.version.split()[0]}")
print(f"Executable     : {sys.executable}")
print("-" * 55)

# Try importing every required package
packages = {
    "pandas": "pandas",
    "numpy": "numpy",
    "sklearn": "scikit-learn",
    "imblearn": "imbalanced-learn",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "joblib": "joblib",
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "pydantic": "pydantic",
}

all_ok = True
for module_name, package_name in packages.items():
    try:
        module = __import__(module_name)
        version = getattr(module, "__version__", "unknown")
        print(f"[OK]   {package_name:<20} version {version}")
    except ImportError:
        print(f"[FAIL] {package_name:<20} NOT INSTALLED")
        all_ok = False

print("-" * 55)
if all_ok:
    print("SUCCESS: All packages are installed correctly.")
else:
    print("ERROR: Some packages are missing. Re-run:")
    print("pip install pandas numpy scikit-learn imbalanced-learn matplotlib seaborn joblib fastapi uvicorn pydantic")
print("=" * 55)