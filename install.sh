#!/usr/bin/env bash
set -e

echo "============================================"
VER=$(cat VERSION 2>/dev/null || echo "v0.5.5")
echo "  Novel Pipeline - Write Engine $VER"
echo "  Install (Mac / Linux)"
echo "============================================"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 not found. Please install Python 3.10+."
  exit 1
fi

PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[OK] Python $PYVER"

if [ ! -f "config.json" ] && [ -f "config.example.json" ]; then
  cp config.example.json config.json
  echo "[OK] config.json created from config.example.json"
fi

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
python novel.py status

echo ""
echo "============================================"
echo "  Install complete."
echo "  Run: ./run_demo.sh"
echo "============================================"
