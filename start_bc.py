"""
This file serves as the main application launcher and acts as a wrapper to
handle any build, packaging, or execution issues when running the app as
a PyInstaller-built executable, from the console, or directly via Python.

Use this file to start the application instead of main.py to ensure
consistent behavior across all environments.
"""

import sys

from src.main import main

if __name__ == '__main__':
    sys.exit(main())
