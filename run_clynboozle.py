#!/usr/bin/env python3
"""
ClynBoozle Application Launcher

This script provides a convenient way to launch the ClynBoozle application
with proper Python path setup and error handling.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
app_root = Path(__file__).parent
src_path = app_root / "src"
sys.path.insert(0, str(src_path))

try:
    from clynboozle.main import main

    if __name__ == "__main__":
        # Check for debug flag
        debug_mode = "--debug" in sys.argv or "-d" in sys.argv
        exit_code = main(debug=debug_mode)
        sys.exit(exit_code)

except ImportError as e:
    print(f"Error importing ClynBoozle: {e}")
    print("Make sure you've installed the required dependencies with:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error starting ClynBoozle: {e}")
    sys.exit(1)
