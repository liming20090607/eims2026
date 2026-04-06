@echo off
chcp 65001 >nul
title Force Restart Script
echo ========================================
echo   Upload Force Restart Script
echo ========================================
echo.
scp E:\EIMS2026\bat\force-restart.sh admin@39.106.41.239:/tmp/force-restart.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS!
    echo.
    echo Next: Login SSH and run:
    echo bash /tmp/force-restart.sh
    echo.
) else (
    echo.
    echo FAILED!
)

pause
