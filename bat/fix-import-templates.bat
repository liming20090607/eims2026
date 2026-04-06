@echo off
chcp 65001 >nul
title Fix Import-Export Templates
echo ========================================
echo   Fix Import-Export Templates
echo ========================================
echo.
echo Creating template directories on server...
echo.

ssh root@39.106.41.239 "mkdir -p /var/www/eims/templates/admin/import_export; cp -r /var/www/eims/venv/lib/python3.10/site-packages/import_export/templates/admin/import_export/* /var/www/eims/templates/admin/import_export/"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Templates Copied!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Press Ctrl+F5 to hard refresh browser
    echo   2. Visit: http://39.106.41.239:8000/admin/eims_app/employee/
    echo   3. You should see [Import] button!
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
