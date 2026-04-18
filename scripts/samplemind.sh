#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════════
# SampleMind AI — Main Shell Wrapper
# ══════════════════════════════════════════════════════════════════════════════
#
# Convenience wrapper that changes into the project root directory and
# launches the Python CLI entry point (main.py).  All arguments are
# forwarded verbatim, so you can use it the same way as ``python main.py``:
#
#   ./scripts/samplemind.sh                    # interactive menu
#   ./scripts/samplemind.sh analyze song.wav   # quick analysis
#   ./scripts/samplemind.sh --help             # show help
#
# ══════════════════════════════════════════════════════════════════════════════
cd "$(dirname "$0")"
python3 main.py "$@"
