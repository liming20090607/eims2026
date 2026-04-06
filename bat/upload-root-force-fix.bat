@echo off
chcp 65001 >nul
title Root Force Fix Script
echo ========================================
echo   Upload Root Force Fix Script
echo ========================================
echo.
scp E:\EIMS2026\bat\root-force-fix.sh admin@39.106.41.239:/tmp/root-force-fix.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS!
    echo.
    echo Login and run:
    echo bash /tmp/root-force-fix.sh
    echo.
) else (
    echo.
    echo FAILED!
)

pause
