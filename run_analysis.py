"""
Quick Launch Script for Music Rights Analyzer
==============================================

This is a convenience script to run the analyzer from the project root.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import and run main
from main import main

if __name__ == "__main__":
    main()
