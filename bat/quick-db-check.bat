@echo off
chcp 65001 >nul
title Quick Database Check
echo ========================================
echo   Quick Database Data Check
echo ========================================
echo.
ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; python3 manage.py shell << 'EOF'
from eims_app import models
from django.contrib.auth.models import User

print('=' * 60)
print('  数据库数据统计')
print('=' * 60)
print(f'  项目台账：{models.Project.objects.count()} 条')
print(f'  员工花名册：{models.Employee.objects.count()} 条')
print(f'  部门列表：{models.Department.objects.count()} 条')
print(f'  通知公告：{models.Notice.objects.count()} 条')
print(f'  用户数量：{User.objects.count()} 条')
print('=' * 60)

# 显示一些示例数据
print('')
print('项目示例:')
for p in models.Project.objects.all()[:3]:
    print(f'  - {p.project_name}')

print('')
print('员工示例:')
for e in models.Employee.objects.all()[:3]:
    print(f'  - {e.name}')

print('')
print('部门示例:')
for d in models.Department.objects.all()[:3]:
    print(f'  - {d.name}')
EOF
"

pause
