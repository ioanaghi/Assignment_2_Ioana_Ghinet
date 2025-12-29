import os
from pathlib import Path

# Project root is two levels up from logic/
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Binary paths (Hardcoded as per requirements)
PROVER9_BIN = "/home/ioana/Documents/Prover9/LADR-2009-11A/bin/prover9"
MACE4_BIN = "/home/ioana/Documents/Prover9/LADR-2009-11A/bin/mace4"

# Folder for .in templates and generated files
PROVER_DIR = PROJECT_ROOT / "Prover"
GENERATED_DIR = PROVER_DIR / "generated"

# Template paths
SAFE_TEMPLATE = PROVER_DIR / "query_safe_skeleton.in"
MINE_TEMPLATE = PROVER_DIR / "query_mine_skeleton.in"
MACE_TEMPLATE = PROVER_DIR / "mace_skeleton.in"