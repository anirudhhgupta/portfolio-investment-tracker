#!/usr/bin/env python3
"""
Portfolio Extraction Script
Convenience script to run portfolio extraction from project root
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from extractors.portfolio_extractor import main

if __name__ == "__main__":
    main()