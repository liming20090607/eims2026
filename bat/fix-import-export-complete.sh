#!/bin/bash
# 完整修复 import-export 功能

echo "========================================"
echo "  修复 Import-Export 功能"
echo "========================================"
echo ""

cd /var/www/eims

echo "1. 添加 import_export 到 INSTALLED_APPS"
if grep -q "'import_export'" settings.py; then
    echo "   ✓ import_export 已在 INSTALLED_APPS 中"
else
    sed -i "/INSTALLED_APPS = \[/a\    'import_export'," settings.py
    echo "   ✓ 已添加 import_export 到 INSTALLED_APPS"
fi

echo ""
echo "2. 复制模板文件"
mkdir -p /var/www/eims/templates/admin/import_export
cp -r /var/www/eims/venv/lib/python3.10/site-packages/import_export/templates/admin/import_export/* /var/www/eims/templates/admin/import_export/
echo "   ✓ 模板文件已复制"

echo ""
echo "3. 设置权限"
chown -R admin:admin /var/www/eims/templates
echo "   ✓ 权限已设置"

echo ""
echo "4. 重启服务"
supervisorctl restart eims
echo "   ✓ 服务已重启"

echo ""
echo "========================================"
echo "  修复完成!"
echo "========================================"
echo ""
echo "现在请:"
echo "1. 按 Ctrl+F5 强制刷新浏览器"
echo "2. 再次点击 [IMPORT] 按钮"
echo "3. 导入页面应该能正常工作了!"
echo ""
