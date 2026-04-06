@echo off
chcp 65001 >nul
title Upload Clear and Restore Script
echo ========================================
echo   Upload Clear and Restore Script
echo ========================================
echo.
scp E:\EIMS2026\bat\clear-server-data.sh root@39.106.41.239:/tmp/clear-server-data.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS!
    echo.
    echo Script uploaded to: /tmp/clear-server-data.sh
    echo.
    echo Next steps:
    echo   1. Run: E:\EIMS2026\bat\clear-and-reupload.bat
    echo   2. SSH login: ssh root@39.106.41.239
    echo   3. Run: bash /tmp/clear-server-data.sh
    echo.
) else (
    echo.
    echo FAILED to upload script!
)

pause
