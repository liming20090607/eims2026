@echo off
chcp 65001 >nul
title Upload Repair Script
echo ========================================
echo   Upload Repair Script to Server
echo ========================================
echo.
echo Server: 39.106.41.239
echo User: admin
echo.
echo ========================================
echo.
echo Uploading script...
echo.

scp E:\EIMS2026\bat\server-repair-admin.sh admin@39.106.41.239:/tmp/server-repair.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Script uploaded.
    echo.
    echo Next steps:
    echo 1. Login: ssh admin@39.106.41.239
    echo 2. Run: bash /tmp/server-repair.sh
    echo 3. Choose option 1
    echo.
) else (
    echo.
    echo FAILED! Please try manually:
    echo scp E:\EIMS2026\bat\server-repair-admin.sh admin@39.106.41.239:/tmp/server-repair.sh
    echo.
)

pause
