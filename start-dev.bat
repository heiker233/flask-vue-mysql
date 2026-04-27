@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-dev.ps1"
set "exit_code=%ERRORLEVEL%"

if not "%exit_code%"=="0" (
    echo.
    echo Start failed with exit code %exit_code%.
    pause
)

exit /b %exit_code%
