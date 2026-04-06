@echo off
chcp 65001 >nul
title Fix Supervisor Configuration
echo ========================================
echo   Fix Supervisor Configuration
echo ========================================
echo.
echo Fixing Gunicorn command in Supervisor config...
echo.

ssh root@39.106.41.239 "cat > /etc/supervisor/conf.d/eims.conf << 'EOF'
[program:eims]
command=/var/www/eims/venv/bin/gunicorn --config /var/www/eims/gunicorn.conf.py wsgi:application
directory=/var/www/eims
user=admin
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
numprocs=1
redirect_stderr=true
stdout_logfile=/var/www/eims/logs/gunicorn-out.log
stderr_logfile=/var/www/eims/logs/gunicorn-error.log
environment=DJANGO_SETTINGS_MODULE=\"settings\",PATH=\"/var/www/eims/venv/bin\"
EOF
supervisorctl reread; supervisorctl update; supervisorctl restart eims; sleep 3; supervisorctl status eims"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Configuration Fixed!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Wait 5 seconds
    echo   2. Press F5 to refresh browser
    echo   3. The page should load properly!
    echo.
) else (
    echo.
    echo ========================================
    echo   Fix Failed!
    echo ========================================
    echo.
    echo Please check SSH connection and try again.
)

pause
