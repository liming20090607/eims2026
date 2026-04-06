@echo off
chcp 65001 >nul
echo ======================================
echo EIMS Data Migration Tool
echo ======================================
echo.

REM Get project root directory
set PROJECT_ROOT=%~dp0..
cd /d "%PROJECT_ROOT%"

echo Exporting data...
echo Current directory: %CD%
echo.

echo [1/4] Exporting department data...
python manage.py dumpdata eims_app.Department --indent 2 > department_data.json
if %ERRORLEVEL% EQU 0 (
    echo   SUCCESS: Department data exported
    for %%A in (department_data.json) do echo   Size: %%~zA bytes
) else (
    echo   ERROR: Failed to export department data
    pause
    exit /b 1
)

echo.
echo [2/4] Exporting role data...
python manage.py dumpdata eims_app.Role --indent 2 > role_data.json
if %ERRORLEVEL% EQU 0 (
    echo   SUCCESS: Role data exported
    for %%A in (role_data.json) do echo   Size: %%~zA bytes
) else (
    echo   ERROR: Failed to export role data
    pause
    exit /b 1
)

echo.
echo [3/4] Verifying files...
if exist department_data.json (
    echo   OK: department_data.json created
) else (
    echo   ERROR: department_data.json not found
    pause
    exit /b 1
)

if exist role_data.json (
    echo   OK: role_data.json created
) else (
    echo   ERROR: role_data.json not found
    pause
    exit /b 1
)

echo.
echo [4/4] Uploading to server...
echo.
echo Enter server IP (default: 39.106.41.239):
set /p SERVER_IP=
if "%SERVER_IP%"=="" set SERVER_IP=39.106.41.239

echo.
echo Uploading to %SERVER_IP%...
echo.

scp department_data.json root@%SERVER_IP%:/root/
if %ERRORLEVEL% EQU 0 (
    echo   SUCCESS: Department data uploaded
) else (
    echo   ERROR: Upload failed, check SSH connection
    goto :manual
)

scp role_data.json root@%SERVER_IP%:/root/
if %ERRORLEVEL% EQU 0 (
    echo   SUCCESS: Role data uploaded
) else (
    echo   ERROR: Upload failed, check SSH connection
    goto :manual
)

echo.
echo ======================================
echo Export and upload completed!
echo ======================================
echo.
echo Data files:
echo   Local: %CD%
echo   Server: root@%SERVER_IP%:/root/
echo.
echo ======================================
echo Next steps:
echo ======================================
echo.
echo Option 1: Auto import via SSH (Recommended)
echo   Press any key to continue with auto import
echo.
echo Option 2: Manual import
echo   SSH to server and run:
echo     cd /var/www/eims
echo     source venv/bin/activate
echo     python manage.py loaddata /root/department_data.json
echo     python manage.py loaddata /root/role_data.json
echo.

pause >nul
echo.
echo ======================================
echo Connecting to server...
echo ======================================
echo.

ssh root@%SERVER_IP% "cd /var/www/eims; source venv/bin/activate; python manage.py loaddata /root/department_data.json; python manage.py loaddata /root/role_data.json; python manage.py shell -c 'from eims_app.models import Department, Role; print(f\"Imported - Departments: {Department.objects.count()}, Roles: {Role.objects.count()}\")'"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================
    echo Migration completed successfully!
    echo ======================================
) else (
    echo.
    echo ======================================
    echo WARNING: Auto import failed, please import manually
    echo ======================================
    goto :manual
)

echo.
pause
exit /b 0

:manual
echo.
echo ======================================
echo Manual Import Instructions
echo ======================================
echo.
echo 1. SSH to server:
echo    ssh root@%SERVER_IP%
echo.
echo 2. Navigate to project:
echo    cd /var/www/eims
echo.
echo 3. Activate virtual environment:
echo    source venv/bin/activate
echo.
echo 4. Import department data:
echo    python manage.py loaddata /root/department_data.json
echo.
echo 5. Import role data:
echo    python manage.py loaddata /root/role_data.json
echo.
echo 6. Verify:
echo    python manage.py shell -c "from eims_app.models import Department, Role; print('Departments:', Department.objects.count(), 'Roles:', Role.objects.count())"
echo.

pause
