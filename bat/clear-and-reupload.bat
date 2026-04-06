@echo off
chcp 65001 >nul
title Clear Server Data and Re-upload
echo ========================================
echo   Clear Server Data and Re-upload
echo ========================================
echo.
echo This will:
echo   1. Clear all data on server
echo   2. Export data from local database
echo   3. Upload and restore to server
echo.
pause

echo.
echo Step 1: Export local data...
echo.

:: 导出本地数据
call venv\Scripts\activate.bat
python manage.py dumpdata --format json --indent 2 --exclude auth.permission --exclude contenttypes --exclude admin.logentry --exclude admin.additionalemailinputfield --exclude sessions > local_backup_full.json

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Local data exported to: local_backup_full.json
    echo.
    echo File size:
    dir local_backup_full.json
    echo.
) else (
    echo.
    echo Failed to export local data!
    pause
    exit /b 1
)

echo.
echo Step 2: Upload backup to server...
echo.
scp local_backup_full.json root@39.106.41.239:/var/www/eims/

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Backup uploaded successfully!
    echo.
) else (
    echo.
    echo Failed to upload backup!
    pause
    exit /b 1
)

echo.
echo Step 3: Clear server data and restore...
echo.
echo Login to SSH and run the restore script...
echo.
echo Commands to execute on server:
echo   cd /var/www/eims
echo   source venv/bin/activate
echo   python3 manage.py flush --no-input
echo   python3 manage.py loaddata local_backup_full.json
echo.

pause
