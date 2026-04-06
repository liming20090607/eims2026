@echo off
chcp 65001 >nul
title Clear All Employee Data
echo ========================================
echo   Clear All Employee Data from Database
echo ========================================
echo.
echo WARNING: This will delete ALL employee records!
echo.

ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; python manage.py clear_employees --confirm; echo ''; echo '=== 验证结果 ==='; python manage.py shell -c 'from eims_app.models import Employee; print(f\"剩余员工数: {Employee.objects.count()}\")'"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Data Cleared Successfully!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Refresh browser (F5)
    echo   2. Employee list should be empty
    echo   3. You can import new data
    echo.
) else (
    echo.
    echo ========================================
    echo   Operation Failed!
    echo ========================================
    echo.
    echo Please check SSH connection and try again.
)

pause
