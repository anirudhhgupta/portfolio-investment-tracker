#!/usr/bin/env python3
"""
Dashboard Generation Script
Convenience script to generate local HTML dashboard from project root
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.dashboard import main

if __name__ == "__main__":
    main()