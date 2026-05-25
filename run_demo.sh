#!/usr/bin/env bash
set -e

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

echo "Running demo..."
python3 novel.py demo
python3 novel.py report

echo ""
echo "Demo complete. Open reports/index.html"
