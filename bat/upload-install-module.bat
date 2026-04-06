@echo off
chcp 65001 >nul
title Install Module Script
echo ========================================
echo   Upload Install Module Script
echo ========================================
echo.
scp E:\EIMS2026\bat\install-module.sh root@39.106.41.239:/tmp/install-module.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS!
    echo.
    echo Login and run:
    echo bash /tmp/install-module.sh
    echo.
) else (
    echo.
    echo FAILED!
)

pause
