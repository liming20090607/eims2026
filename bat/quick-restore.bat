@echo off
chcp 65001 >nul
title Quick Restore Data
echo ========================================
echo   Quick Restore Data from Backup
echo ========================================
echo.
echo This will restore data from backup_before_phase4.json
echo.
echo Login to SSH and run restore...
echo.

:: SSH 执行恢复命令
ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; python3 manage.py loaddata backup_before_phase4.json --verbosity 2"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   SUCCESS! Data restored!
    echo ========================================
    echo.
) else (
    echo.
    echo ========================================
    echo   Error occurred during restore
    echo ========================================
    echo.
)

pause
