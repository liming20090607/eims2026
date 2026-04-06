@echo off
chcp 65001 >nul
title Upload Database Check Script
echo ========================================
echo   Upload Database Check Script
echo ========================================
echo.
scp E:\EIMS2026\bat\check-db-data.sh root@39.106.41.239:/tmp/check-db-data.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS!
    echo.
    echo Login and run:
    echo bash /tmp/check-db-data.sh
    echo.
) else (
    echo.
    echo FAILED!
)

pause
