@echo off
chcp 65001 >nul
echo ============================================
for /f "delims=" %%v in ('type VERSION') do echo   Novel Pipeline - Write Engine %%v
echo   Reports
echo ============================================
echo.

python novel.py report

pause
