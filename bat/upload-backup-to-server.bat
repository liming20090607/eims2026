@echo off
chcp 65001 >nul
title Upload Backup File to Server
echo ========================================
echo   Upload Backup File to Server
echo ========================================
echo.

echo Uploading backup_before_phase4.json to server...
scp -C "E:\EIMS2026\backup_before_phase4.json" root@39.106.41.239:/root/

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Upload Successful!
    echo ========================================
    echo.
    echo NOW:
    echo   Run restore-user-groups.bat to restore data
    echo.
) else (
    echo.
    echo ========================================
    echo   Upload Failed!
    echo ========================================
    echo.
    echo Please check SSH connection and try again.
)

pause
