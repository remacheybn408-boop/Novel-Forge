#!/usr/bin/env bash
set -e

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

python3 novel.py report
echo ""
echo "Report generated. Open reports/index.html"
