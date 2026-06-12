@echo off
cd /d "%~dp0"

where uv >nul 2>&1
if errorlevel 1 goto no_uv

echo Starting Novel Forge Web...
uv run --with-requirements requirements-api.txt python start.py
if errorlevel 1 goto failed
exit /b 0

:no_uv
echo [FAIL] uv was not found.
echo Install uv from https://docs.astral.sh/uv/
pause
exit /b 1

:failed
echo [FAIL] Startup failed.
echo Check logs\web-api.log and logs\web-frontend.log
pause
exit /b 1
