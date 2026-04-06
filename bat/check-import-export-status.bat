@echo off
chcp 65001 >nul
title Check Import-Export Installation
echo ========================================
echo   Check Import-Export Installation
echo ========================================
echo.
echo Checking if django-import-export is installed...
echo.

ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; pip show django-import-export"

echo.
echo ========================================
echo Checking Python path and imports...
echo ========================================
echo.

ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; python3 -c 'from import_export.admin import ImportExportModelAdmin; print(\"SUCCESS: import-export is working!\")'"

echo.
echo ========================================
echo Restarting server to apply changes...
echo ========================================
echo.

ssh root@39.106.41.239 "supervisorctl restart eims"

echo.
echo Done! Please refresh your browser (Ctrl+F5) and check again.
echo.

pause
