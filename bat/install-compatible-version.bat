@echo off
chcp 65001 >nul
title Install Compatible Version
echo ========================================
echo   Install Compatible Version
echo ========================================
echo.
echo Installing django-import-export 2.0 (compatible with SQLite 3.26)...
echo.

echo Please run these commands on server:
echo.
echo   ssh root@39.106.41.239
echo   cd /var/www/eims
echo   source venv/bin/activate
echo   pip install django-import-export==2.0.2
echo   find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
echo   supervisorctl restart eims
echo.

echo.
echo Or run this one-liner:
echo ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; pip install django-import-export==2.0.2; find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; supervisorctl restart eims"
echo.

pause
