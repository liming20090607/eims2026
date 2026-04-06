@echo off
chcp 65001 >nul
title Quick Fix - Install Compatible Version
echo ========================================
echo   Quick Fix - Install Compatible Version
echo ========================================
echo.
echo This will install django-import-export 2.0.2 on the server.
echo.
echo Executing...
echo.

ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; pip install django-import-export==2.0.2; find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; supervisorctl restart eims"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Installation Complete!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Press Ctrl+F5 to hard refresh browser
    echo   2. Visit: http://39.106.41.239:8000/admin/eims_app/employee/
    echo   3. You should see [导入] button!
    echo.
) else (
    echo.
    echo ========================================
    echo   Installation Failed!
    echo ========================================
    echo.
    echo Please check network and try again.
)

pause
