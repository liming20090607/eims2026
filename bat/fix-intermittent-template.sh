#!/bin/bash
# 彻底解决间歇性模板加载问题

echo "========================================"
echo "  解决间歇性模板加载问题"
echo "========================================"
echo ""

cd /var/www/eims

echo "1. 停止 Supervisor 服务"
supervisorctl stop eims
sleep 2

echo ""
echo "2. 清除所有 Python 缓存"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null
rm -rf /var/www/eims/__pycache__
echo "   ✓ 缓存已清除"

echo ""
echo "3. 检查模板文件是否存在"
if [ -f "/var/www/eims/templates/admin/import_export/change_list_import_export.html" ]; then
    echo "   ✓ 模板文件存在"
else
    echo "   ✗ 模板文件缺失，重新复制..."
    mkdir -p /var/www/eims/templates/admin/import_export
    cp -r /var/www/eims/venv/lib/python3.10/site-packages/import_export/templates/admin/import_export/* /var/www/eims/templates/admin/import_export/
    chown -R admin:admin /var/www/eims/templates
    echo "   ✓ 模板文件已复制"
fi

echo ""
echo "4. 检查 INSTALLED_APPS"
if grep -q "'import_export'" settings.py; then
    echo "   ✓ import_export 已在 INSTALLED_APPS 中"
else
    sed -i "/INSTALLED_APPS = \[/a\    'import_export'," settings.py
    echo "   ✓ 已添加 import_export"
fi

echo ""
echo "5. 等待 3 秒让所有进程完全停止"
sleep 3

echo ""
echo "6. 启动服务"
supervisorctl start eims
sleep 2

echo ""
echo "7. 检查服务状态"
supervisorctl status eims

echo ""
echo "8. 检查 Gunicorn 进程数"
ps aux | grep gunicorn | grep -v grep | wc -l

echo ""
echo "========================================"
echo "  修复完成!"
echo "========================================"
echo ""
echo "现在请:"
echo "1. 按 Ctrl+F5 强制刷新浏览器 (多刷新几次)"
echo "2. 访问员工管理页面"
echo "3. 点击 [IMPORT] 按钮"
echo ""
