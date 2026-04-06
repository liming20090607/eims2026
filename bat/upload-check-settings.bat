@echo off
chcp 65001 >nul
title Check Settings Script
echo ========================================
echo   Upload Django Settings Check Script
echo ========================================
echo.
scp E:\EIMS2026\bat\check-settings.sh root@39.106.41.239:/tmp/check-settings.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS!
    echo.
    echo Login and run:
    echo bash /tmp/check-settings.sh
    echo.
    echo Then copy the output
) else (
    echo.
    echo FAILED!
)

pause
