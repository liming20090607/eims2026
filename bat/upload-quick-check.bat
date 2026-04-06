@echo off
chcp 65001 >nul
title Upload Quick Check Script
echo ========================================
echo   Upload Quick Check Script
echo ========================================
echo.
scp E:\EIMS2026\bat\quick-check.sh root@39.106.41.239:/tmp/quick-check.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS!
    echo.
    echo Login to SSH and run:
    echo bash /tmp/quick-check.sh
    echo.
) else (
    echo.
    echo FAILED to upload!
)

pause
