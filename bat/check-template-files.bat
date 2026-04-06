@echo off
chcp 65001 >nul
title Check Template Files
echo ========================================
echo   Check Template Files
echo ========================================
echo.

ssh root@39.106.41.239 "ls -la /var/www/eims/templates/admin/import_export/"

pause
