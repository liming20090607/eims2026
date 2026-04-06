@echo off
chcp 65001 >nul
title Check Logs Script
echo ========================================
echo   Upload Check Logs Script
echo ========================================
echo.
scp E:\EIMS2026\bat\check-logs.sh admin@39.106.41.239:/tmp/check-logs.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS!
    echo.
    echo Login and run:
    echo bash /tmp/check-logs.sh
    echo.
    echo Then copy the output to get help
) else (
    echo.
    echo FAILED!
)

pause
