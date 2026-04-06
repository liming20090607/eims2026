@echo off
chcp 65001 >nul
title Fix ROOT_URLCONF and Database Script
echo ========================================
echo   Upload Fix ROOT_URLCONF Script
echo ========================================
echo.
scp E:\EIMS2026\bat\fix-root-urlconf.sh root@39.106.41.239:/tmp/fix-root-urlconf.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS!
    echo.
    echo Login and run:
    echo bash /tmp/fix-root-urlconf.sh
    echo.
    echo This script will:
    echo   1. Fix ROOT_URLCONF
    echo   2. Run database migrations
    echo   3. Restart Gunicorn
    echo.
) else (
    echo.
    echo FAILED!
)

pause
