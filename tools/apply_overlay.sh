#!/bin/bash
# Usage: bash tools/apply_overlay.sh <OpenTTD source folder> [--check]
set -e
python3 "$(dirname "$0")/apply_overlay.py" "${1:-.}" ${2:+"$2"}
