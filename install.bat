@echo off
chcp 65001 >nul
echo ============================================
for /f "delims=" %%v in ('type VERSION') do echo   Novel Pipeline - Write Engine %%v
echo   Reader Pull + Voice Pack + Meme Pack Guards
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not installed or not in PATH.
    echo   Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python installed
python --version

:: Install dependencies
if exist requirements.txt (
    echo [INFO] Installing dependencies from requirements.txt...
    pip install -r requirements.txt -q
    echo [OK] Dependencies installed
) else (
    echo [WARN] requirements.txt not found, skipping pip install
)

:: Install pytest if needed
python -c "import pytest" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing pytest...
    pip install pytest -q
)
echo [OK] pytest available

:: Create directories
echo [INFO] Creating directories...
if not exist src\guards mkdir src\guards
if not exist novels mkdir novels
if not exist exports mkdir exports
if not exist exports\reports mkdir exports\reports
echo [OK] Directories ready

:: Copy config
if not exist config.json (
    if exist config.example.json (
        echo [INFO] Creating config.json from example...
        copy config.example.json config.json >nul
        echo [OK] config.json created
    ) else (
        echo [WARN] No config.example.json found — config.json may be needed
    )
) else (
    echo [OK] config.json exists
)

:: Init DB
echo [INFO] Initializing database...
python scripts/init_db.py --config config.json 2>nul
if %errorlevel% equ 0 (
    echo [OK] Database initialized
) else (
    echo [WARN] Database init may have failed, continuing...
)

:: Import demo skeleton
if exist examples\demo_novel\outline_skeleton.json (
    echo [INFO] Importing demo outline skeleton...
    python scripts/import_outline_skeleton.py --config config.json --input examples\demo_novel\outline_skeleton.json 2>nul
    echo [OK] Demo skeleton imported
)

:: Import voice packs
echo [INFO] Importing voice packs...
python scripts/import_voice_packs.py --config config.json --input-dir voice_packs 2>nul
echo [OK] Voice packs imported

:: Run status check
echo.
echo [INFO] Running environment check...
python novel.py status

echo.
echo ============================================
echo   Installation complete!
echo   Run: run_demo.bat     Quick demo
echo   Run: run_status.bat   Environment status
echo   Run: run_report.bat   View reports
echo   Run: pytest tests/ -v Run full test suite
echo ============================================
pause
