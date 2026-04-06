@echo off
chcp 65001 >nul
title Quick Restart Script
echo ========================================
echo   Upload Quick Restart Script
echo ========================================
echo.
scp E:\EIMS2026\bat\quick-restart.sh admin@39.106.41.239:/tmp/quick-restart.sh

if %ERRORLEVEL% EQU 0 (
    echo SUCCESS!
    echo.
    echo Login and run:
    echo bash /tmp/quick-restart.sh
) else (
    echo FAILED!
)

pause
