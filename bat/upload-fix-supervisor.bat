@echo off
chcp 65001 >nul
title Fix Supervisor Script
echo ========================================
echo   Upload Fix Supervisor Script
echo ========================================
echo.
scp E:\EIMS2026\bat\fix-supervisor.sh admin@39.106.41.239:/tmp/fix-supervisor.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS!
    echo.
    echo Login and run:
    echo bash /tmp/fix-supervisor.sh
    echo.
) else (
    echo.
    echo FAILED!
)

pause
