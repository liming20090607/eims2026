@echo off
chcp 65001 >nul
title Check Django Error
echo ========================================
echo   Upload Django Error Check Script
echo ========================================
echo.
scp E:\EIMS2026\bat\check-django-error.sh root@39.106.41.239:/tmp/check-django-error.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS!
    echo.
    echo Login and run:
    echo bash /tmp/check-django-error.sh
    echo.
    echo Then copy the output
) else (
    echo.
    echo FAILED!
)

pause
