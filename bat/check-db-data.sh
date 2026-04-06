#!/bin/bash
# Check Database Data Status

echo "========================================"
echo "  检查数据库数据状态"
echo "========================================"
echo ""

cd /var/www/eims
source venv/bin/activate

echo "1. 数据统计"
echo "----------------------------------------"
python3 manage.py shell << 'EOF'
from eims_app import models
from django.contrib.auth.models import User

print(f'项目台账：{models.Project.objects.count()} 条')
print(f'员工花名册：{models.Employee.objects.count()} 条')
print(f'部门列表：{models.Department.objects.count()} 条')
print(f'通知公告：{models.Notice.objects.count()} 条')
print(f'用户数量：{User.objects.count()} 条')
print('')

# 检查是否为空
if models.Project.objects.count() == 0:
    print('⚠️  项目台账为空!')
if models.Employee.objects.count() == 0:
    print('⚠️  员工花名册为空!')
if models.Department.objects.count() == 0:
    print('⚠️  部门列表为空!')
if models.Notice.objects.count() == 0:
    print('⚠️  通知公告为空!')
EOF

echo ""
echo "2. 查找数据库文件"
echo "----------------------------------------"
find /var/www/eims -name "*.sqlite3" -o -name "*.db" 2>/dev/null | while read file; do
    echo "文件：$file"
    ls -lh "$file"
done

echo ""
echo "3. 查找备份文件"
echo "----------------------------------------"
find /var/www/eims -name "*.json" -type f 2>/dev/null | head -10 | while read file; do
    echo "文件：$file"
    ls -lh "$file"
done

echo ""
echo "4. 数据库配置"
echo "----------------------------------------"
grep -A 5 "DATABASES" /var/www/eims/settings.py | head -10

echo ""
echo "========================================"
echo "检查完成"
echo "========================================"
