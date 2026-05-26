"""Root launcher for the WebUI backend.
Run from the unzipped project root with: python server.py
"""
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parent
WEBUI = ROOT / "webui"
SERVER = WEBUI / "server.py"

if not SERVER.exists():
    print("ERROR: cannot find webui/server.py")
    print(f"Current folder: {ROOT}")
    sys.exit(1)

sys.path.insert(0, str(WEBUI))
runpy.run_path(str(SERVER), run_name="__main__")
