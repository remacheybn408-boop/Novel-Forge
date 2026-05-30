@echo off
chcp 65001 >nul
title Novel Pipeline - 一键安装启动
cd /d "%~dp0"

:check_python
python --version >nul 2>&1
if %errorlevel% equ 0 goto check_node
echo   Python 未安装，正在自动安装...
winget install Python.Python.3.12 --silent --accept-package-agreements >nul 2>&1
if %errorlevel% equ 0 (
    echo   安装完成，请关闭窗口后重新双击运行。
    pause
    exit
)
echo   自动安装失败，请手动输入: winget install Python.Python.3.12
pause
exit /b 1

:check_node
node --version >nul 2>&1
if %errorlevel% equ 0 goto install_deps
echo   Node.js 未安装，正在自动安装...
winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements >nul 2>&1
if %errorlevel% equ 0 (
    echo   安装完成，请关闭窗口后重新双击运行。
    pause
    exit
)
echo   自动安装失败，请手动输入: winget install OpenJS.NodeJS.LTS
pause
exit /b 1

:install_deps
echo   安装 Python 依赖...
pip install -r requirements.txt -r requirements-api.txt -q 2>nul
echo   安装前端依赖...
cd frontend
call npm install --silent 2>nul
cd ..
if not exist config.json (
    if exist config.example.json copy config.example.json config.json >nul
)
python novel.py init 2>nul
echo   启动...
python start.py
pause
