@echo off
echo Converting UI files...
python "%~dp0convert_ui_to_py.py"
if %errorlevel% neq 0 (
    echo UI conversion failed
    pause
    exit /b 1
)
