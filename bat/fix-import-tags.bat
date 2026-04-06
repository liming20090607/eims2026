@echo off
chcp 65001 >nul
title Fix Import Export Tags
echo ========================================
echo   Fix Import Export Tags
echo ========================================
echo.
echo Adding import_export to INSTALLED_APPS...
echo.

ssh root@39.106.41.239 "cd /var/www/eims; grep -n \"'import_export'\" settings.py || (sed -i \"/INSTALLED_APPS = \[/a\    'import_export',\" settings.py); supervisorctl restart eims"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Fixed!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Press Ctrl+F5 to hard refresh browser
    echo   2. Click [IMPORT] button again
    echo   3. Import page should work now!
    echo.
) else (
    echo.
    echo ========================================
    echo   Failed!
    echo ========================================
    echo.
    echo Please check network and try again.
)

pause
