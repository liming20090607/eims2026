#!/bin/bash
# 彻底修复 INSTALLED_APPS 重复问题

echo "========================================"
echo "  修复 INSTALLED_APPS 重复问题"
echo "========================================"
echo ""

cd /var/www/eims

echo "1. 查看当前 INSTALLED_APPS 配置:"
echo ""
sed -n '/INSTALLED_APPS = \[/,/\]/p' settings.py
echo ""

echo "2. 统计 import_export 出现次数:"
grep -c "import_export" settings.py
echo ""

echo "3. 删除所有 import_export 行:"
sed -i '/import_export/d' settings.py
echo "   ✓ 已删除所有 import_export"
echo ""

echo "4. 重新添加一次 import_export:"
sed -i "/INSTALLED_APPS = \[/a\    'import_export'," settings.py
echo "   ✓ 已添加 import_export"
echo ""

echo "5. 验证结果:"
echo ""
sed -n '/INSTALLED_APPS = \[/,/\]/p' settings.py
echo ""

echo "6. 统计 import_export 数量:"
grep -c "import_export" settings.py
echo ""

echo "7. 清除缓存:"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "   ✓ 缓存已清除"
echo ""

echo "8. 测试 Django 配置:"
source venv/bin/activate
python manage.py check
echo ""

echo "9. 重启服务:"
supervisorctl stop eims
sleep 2
supervisorctl start eims
sleep 5
supervisorctl status eims

echo ""
echo "========================================"
echo "  修复完成!"
echo "========================================"
