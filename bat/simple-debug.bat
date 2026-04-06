@echo off
chcp 65001 >nul
title Simple Debug Import-Export
echo ========================================
echo   Simple Debug Script
echo ========================================
echo.
echo Running simple checks...
echo.

echo Step 1: Test SSH connection
ssh root@39.106.41.239 "echo 'SSH OK'"
if %ERRORLEVEL% NEQ 0 (
    echo SSH failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Check if package is installed
ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; pip list | grep import-export"

echo.
echo Step 3: Test import in Python (with Django settings)
ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; DJANGO_SETTINGS_MODULE=eims_app.settings python3 -c \"import django; django.setup(); from import_export.admin import ImportExportModelAdmin; print('Import OK')\""

echo.
echo Step 4: Check admin.py
echo Looking for ImportExportModelAdmin...
ssh root@39.106.41.239 "cd /var/www/eims; grep -n 'ImportExportModelAdmin' eims_app/admin.py"

echo.
echo Step 5: Check for Resource classes
echo Looking for Resource classes...
ssh root@39.106.41.239 "cd /var/www/eims; grep -n 'class.*Resource' eims_app/admin.py"

echo.
echo ========================================
echo Checks complete!
echo ========================================
echo.
pause
