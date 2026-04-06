@echo off
chcp 65001 >nul
title Create Templates on Server
echo ========================================
echo   Create Templates on Server
echo ========================================
echo.
echo Creating required template directory on server...
echo.

ssh root@39.106.41.239 "mkdir -p /var/www/eims/venv/lib/python3.10/site-packages/import_export/templates/admin/import_export"

echo.
echo Template directory created. Now uploading admin.py again...
scp eims_app\admin.py root@39.106.41.239:/var/www/eims/eims_app/admin.py

echo.
echo Restarting server...
ssh root@39.106.41.239 "supervisorctl restart eims"

echo.
echo ========================================
echo   Complete!
echo ========================================
echo.
echo Please refresh browser (Ctrl+F5) and try again.
echo.
pause
