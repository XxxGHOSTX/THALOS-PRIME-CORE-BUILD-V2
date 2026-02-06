#!/bin/bash
# Quick setup script

echo "THALOS PRIME Setup"
python3 -m pip install --user -r dependencies.txt
chmod +x run_thalos.py
echo "Done! Run: python3 run_thalos.py --mode cli"
