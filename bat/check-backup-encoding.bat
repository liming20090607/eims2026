@echo off
chcp 65001 >nul
title Check Backup File Encoding
echo ========================================
echo   Check Backup File Encoding
echo ========================================
echo.
echo Checking backup file encoding...
echo.

:: 检查文件类型
ssh root@39.106.41.239 "file /var/www/eims/backup_before_phase4.json"

echo.
echo Checking first bytes (hex dump)...
ssh root@39.106.41.239 "xxd /var/www/eims/backup_before_phase4.json | head -5"

echo.
echo Trying to convert encoding...
ssh root@39.106.41.239 "cd /var/www/eims; iconv -f gbk -t utf-8 backup_before_phase4.json > backup_utf8.json 2>&1"

echo.
echo If conversion successful, new file created: backup_utf8.json
echo.

pause
