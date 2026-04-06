@echo off
chcp 65001 >nul
title Install WhiteNoise for Static Files
echo ========================================
echo   Install WhiteNoise
echo ========================================
echo.
echo This will install WhiteNoise on the server to serve static files.
echo.

ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; pip install whitenoise; sed -i \"/MIDDLEWARE = \[/a\    'whitenoise.middleware.WhiteNoiseMiddleware',\" settings.py; echo '' >> settings.py; echo '# WhiteNoise Configuration' >> settings.py; echo 'STATICFILES_STORAGE = \"whitenoise.storage.CompressedManifestStaticFilesStorage\"' >> settings.py; python manage.py collectstatic --noinput --clear; supervisorctl restart eims"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   WhiteNoise Installed!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Press Ctrl+F5 to hard refresh browser
    echo   2. Visit: http://39.106.41.239:8000/admin/
    echo   3. You should see the styled admin interface!
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
