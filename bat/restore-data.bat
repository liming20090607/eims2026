@echo off
chcp 65001 >nul
title Restore Database from Backup
echo ========================================
echo   Restore Database from Backup
echo ========================================
echo.
echo Restoring data from backup_before_phase4.json...
echo.
ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; python3 manage.py loaddata backup_before_phase4.json"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Data Restore COMPLETED!
    echo ========================================
    echo.
    echo Now checking database...
    echo.
    ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; python3 manage.py shell << 'EOF'
from eims_app import models
from django.contrib.auth.models import User

print('=' * 60)
print('  数据库恢复状态')
print('=' * 60)
print(f'  员工花名册：{models.Employee.objects.count()} 条')
print(f'  部门列表：{models.Department.objects.count()} 条')
print(f'  通知公告：{models.Notice.objects.count()} 条')
print(f'  用户数量：{User.objects.count()} 条')
print('=' * 60)

# 检查 Project 模型
try:
    print(f'  项目台账：{models.Project.objects.count()} 条')
except:
    print('  项目台账：模型未找到')

print('')
print('数据恢复成功!')
print('=' * 60)
EOF
"
) else (
    echo.
    echo ========================================
    echo   Restore FAILED!
    echo ========================================
    echo.
    echo Please check the error message above.
)

pause
