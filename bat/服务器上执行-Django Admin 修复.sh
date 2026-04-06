#!/bin/bash

echo "======================================"
echo "修复 Django Admin 后台显示异常"
echo "适用于：Django 4.2.7"
echo "======================================"
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 错误：请使用 root 用户或 sudo 运行此脚本"
    exit 1
fi

echo "📋 本脚本将执行以下操作："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 验证 settings.py 配置"
echo "2. 检查 Django 版本"
echo "3. 清空并重新收集静态文件"
echo "4. 重启 Gunicorn 服务"
echo "5. 验证服务状态"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "是否继续？(y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ 已取消"
    exit 1
fi

# 进入项目目录
cd /var/www/eims

echo ""
echo "======================================"
echo "步骤 1: 检查 Django 版本"
echo "======================================"
source venv/bin/activate
python -m django --version

echo ""
echo "======================================"
echo "步骤 2: 验证 settings.py 配置"
echo "======================================"

# 检查 ADMIN_SITE_HEADER
if grep -q "ADMIN_SITE_HEADER" settings.py; then
    echo "✅ ADMIN_SITE_HEADER 配置存在"
    grep "ADMIN_SITE_HEADER" settings.py
else
    echo "⚠️  ADMIN_SITE_HEADER 配置不存在"
fi

# 检查 USE_DARK_THEME（不应存在）
if grep -q "USE_DARK_THEME" settings.py; then
    echo "⚠️  警告：发现不兼容的 USE_DARK_THEME 配置！"
    echo "   这可能导致 Admin 样式问题"
else
    echo "✅ 未发现不兼容的 USE_DARK_THEME 配置"
fi

# 验证 settings.py 语法
echo ""
echo "验证 settings.py 语法..."
python -c "import settings; print('✅ settings.py 语法正确')" 2>&1

if [ $? -ne 0 ]; then
    echo "❌ settings.py 有语法错误！"
    exit 1
fi

echo ""
echo "======================================"
echo "步骤 3: 清空并重新收集静态文件"
echo "======================================"

echo "清空旧的静态文件..."
python manage.py collectstatic --clear --noinput

if [ $? -eq 0 ]; then
    echo "✅ 已清空静态文件"
else
    echo "❌ 清空静态文件失败"
    exit 1
fi

echo ""
echo "重新收集静态文件..."
python manage.py collectstatic --noinput

if [ $? -eq 0 ]; then
    echo "✅ 静态文件收集完成"
else
    echo "❌ 静态文件收集失败"
    exit 1
fi

# 检查静态文件
echo ""
echo "检查静态文件目录..."
if [ -f staticfiles/admin/css/base.css ]; then
    echo "✅ Admin CSS 文件存在"
    ls -la staticfiles/admin/css/base.css
else
    echo "❌ Admin CSS 文件不存在！"
fi

echo ""
echo "静态文件目录大小："
du -sh staticfiles/

echo ""
echo "======================================"
echo "步骤 4: 设置权限"
echo "======================================"

chown -R admin:admin staticfiles
chmod -R 755 staticfiles

echo "✅ 权限已设置"
ls -ld staticfiles

echo ""
echo "======================================"
echo "步骤 5: 重启 Gunicorn 服务"
echo "======================================"

supervisorctl restart eims

if [ $? -eq 0 ]; then
    echo "✅ Gunicorn 服务已重启"
else
    echo "❌ Gunicorn 服务重启失败"
    exit 1
fi

echo ""
echo "等待服务启动..."
sleep 3

echo ""
echo "======================================"
echo "步骤 6: 查看服务状态"
echo "======================================"

supervisorctl status eims

echo ""
echo "查看进程..."
ps aux | grep gunicorn | grep -v grep

echo ""
echo "查看监听端口..."
netstat -tlnp | grep 8000 || echo "未找到 8000 端口监听"

echo ""
echo "======================================"
echo "步骤 7: 检查日志（最后 20 行）"
echo "======================================"

journalctl -u eims -n 20 --no-pager | tail -20

echo ""
echo "======================================"
echo "✅ 修复完成！"
echo "======================================"
echo ""
echo "📋 下一步操作："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 访问 Admin 后台："
echo "   http://39.106.41.239/admin/"
echo ""
echo "2. 强制刷新浏览器缓存："
echo "   Windows: Ctrl + F5"
echo "   Mac: Cmd + Shift + R"
echo ""
echo "3. 检查以下内容："
echo "   ✅ 页面样式正常显示"
echo "   ✅ 顶部标题显示'协同 AI 办公系统'"
echo "   ✅ 左侧导航栏正常"
echo "   ✅ 表单样式正常"
echo "   ✅ 无黑块或乱码"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 显示配置摘要
echo "📊 配置摘要："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Django 版本：$(python -m django --version)"
echo "Python 路径：$(which python)"
echo "项目目录：$(pwd)"
echo "静态文件目录：$(pwd)/staticfiles"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "💡 提示："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "如果样式仍然丢失，请尝试："
echo "1. 清除浏览器缓存"
echo "2. 使用无痕模式访问"
echo "3. 检查 Nginx 配置（如果使用）"
echo "4. 查看详细日志："
echo "   sudo journalctl -u eims -n 100"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
