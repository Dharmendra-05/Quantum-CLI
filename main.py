#!/usr/bin/env python3
"""
Quantum-CLI: Thin backward-compatible runner.
For full installation and CLI use: pip install -e . then run 'quantum'.
"""

import sys
from pathlib import Path

# Ensure src/ is on sys.path if running directly from repo root without editable install
_SRC_ROOT = Path(__file__).resolve().parent / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from quantum_cli.cli.main import main

if __name__ == "__main__":
    main()
