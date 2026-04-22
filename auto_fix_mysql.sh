#!/bin/bash
# 自动测试并修复 MySQL 连接问题
# 在 VS Code 远程终端中运行: bash auto_fix_mysql.sh

echo "=========================================="
echo "🔧 自动测试并修复 MySQL 连接"
echo "=========================================="

# 步骤 1：清空旧的错误日志
echo ""
echo "[1] 清空旧的错误日志..."
echo "" > /var/www/eims/logs/gunicorn_error.log
echo "   ✅ 错误日志已清空"

# 步骤 2：测试登录页面（触发数据库连接）
echo ""
echo "[2] 测试登录页面..."
page_title=$(curl -s http://127.0.0.1:80/login/ | grep -o "<title>.*</title>")
echo "   页面标题: $page_title"

# 步骤 3：等待 3 秒让可能的错误记录到日志
echo ""
echo "[3] 等待 3 秒..."
sleep 3

# 步骤 4：检查新的错误日志
echo ""
echo "[4] 检查新的错误日志..."
error_log=$(tail -30 /var/www/eims/logs/gunicorn_error.log)

if echo "$error_log" | grep -q "OperationalError\|Access denied"; then
    echo "   ❌ 仍然有 MySQL 连接错误！"
    echo ""
    echo "   错误内容:"
    echo "$error_log" | grep -A 5 "OperationalError\|Access denied"
    
    # 步骤 5：检查 settings.py 配置
    echo ""
    echo "[5] 检查 settings.py 配置..."
    grep -A 8 "'default':" /var/www/eims/eims/settings.py | head -10
    
    # 步骤 6：测试 MySQL 直接连接
    echo ""
    echo "[6] 测试 MySQL 直接连接..."
    mysql -u root -p"EIMS2026_mysql" -e "SHOW DATABASES;" 2>&1 | head -15
    
    # 步骤 7：查找所有数据库配置
    echo ""
    echo "[7] 查找所有数据库配置..."
    grep -n "DATABASES\|'NAME'\|'USER'\|'PASSWORD'\|'HOST'\|'PORT'" /var/www/eims/eims/settings.py | head -50
    
    echo ""
    echo "=========================================="
    echo "⚠️  需要手动修复配置"
    echo "=========================================="
    echo ""
    echo "请检查 settings.py 中的数据库配置是否正确"
    
else
    echo "   ✅ 没有新的 MySQL 错误！连接正常。"
    
    # 步骤 8：检查数据库是否存在
    echo ""
    echo "[8] 检查数据库状态..."
    mysql -u root -p"EIMS2026_mysql" -e "
    SHOW DATABASES LIKE 'eims_%';
    SHOW DATABASES LIKE 'root_admin';
    SELECT COUNT(*) as user_count FROM root_admin.auth_user;
    " 2>&1
    
    echo ""
    echo "=========================================="
    echo "✅ MySQL 连接正常！"
    echo "=========================================="
    echo ""
    echo "系统运行正常，可以访问:"
    echo "   http://www.xietongai.com.cn/login/"
    echo ""
    
    # 检查是否有 admin/root 账户
    user_count=$(mysql -u root -p"EIMS2026_mysql" -N -e "SELECT COUNT(*) FROM root_admin.auth_user WHERE username IN ('admin', 'root');" 2>/dev/null)
    
    if [ "$user_count" = "0" ] || [ -z "$user_count" ]; then
        echo "⚠️  注意: 还没有 admin/root 账户"
        echo ""
        echo "创建账户命令:"
        echo "  cd /var/www/eims"
        echo "  venv/bin/python manage.py shell << 'EOF'"
        echo "  from django.contrib.auth.models import User"
        echo "  User.objects.create_superuser('admin', 'admin@eims.com', 'Admin@2026!')"
        echo "  User.objects.create_superuser('root', 'root@eims.com', 'Root@2026!')"
        echo "  EOF"
    else
        echo "✅ admin/root 账户已存在"
    fi
fi

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="
