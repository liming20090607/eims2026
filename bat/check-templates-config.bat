@echo off
chcp 65001 >nul
title Check TEMPLATES Configuration
echo ========================================
echo   Check TEMPLATES Configuration
echo ========================================
echo.

ssh root@39.106.41.239 "grep -A 25 'TEMPLATES = \[' /var/www/eims/settings.py"

pause
