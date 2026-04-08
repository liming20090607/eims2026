#!/bin/bash
# MySQL root密码设置脚本
# 此脚本在云服务器上执行

set -e

echo "========================================="
echo "MySQL root 用户密码设置"
echo "========================================="
echo ""

# 设置您想要的简单密码
NEW_PASSWORD="root123"

echo "即将设置的MySQL root密码: ${NEW_PASSWORD}"
echo "注意: 这是一个简单的密码，仅用于开发和测试环境"
echo "生产环境请使用强密码！"
echo ""

read -p "确认设置密码？(y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "步骤 1: 检查MySQL服务状态"
echo "-----------------------------------------"
systemctl status mysqld | head -10

echo ""
echo "步骤 2: 尝试登录MySQL（无需密码）"
echo "-----------------------------------------"
if mysql -u root -e "SELECT 1;" 2>/dev/null; then
    echo "✓ 可以直接登录MySQL（无需密码）"
    
    echo ""
    echo "步骤 3: 设置root密码"
    echo "-----------------------------------------"
    mysql -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '${NEW_PASSWORD}';
FLUSH PRIVILEGES;
EOF
    echo "✓ 密码设置成功"
    
else
    echo "无法直接登录，尝试其他方式..."
    
    echo ""
    echo "步骤 2.1: 尝试使用系统认证登录"
    echo "-----------------------------------------"
    if mysql -u root -e "SELECT 1;" 2>/dev/null; then
        echo "✓ 使用系统认证登录成功"
        
        mysql -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '${NEW_PASSWORD}';
FLUSH PRIVILEGES;
EOF
        echo "✓ 密码设置成功"
        
    else
        echo "需要重置MySQL root密码"
        echo ""
        echo "请按照以下步骤手动操作："
        echo ""
        echo "1. 停止MySQL服务："
        echo "   systemctl stop mysqld"
        echo ""
        echo "2. 以跳过权限表方式启动MySQL："
        echo "   mysqld_safe --skip-grant-tables &"
        echo ""
        echo "3. 登录MySQL并重置密码："
        echo "   mysql -u root"
        echo "   FLUSH PRIVILEGES;"
        echo "   ALTER USER 'root'@'localhost' IDENTIFIED BY '${NEW_PASSWORD}';"
        echo "   FLUSH PRIVILEGES;"
        echo "   exit;"
        echo ""
        echo "4. 重启MySQL服务："
        echo "   systemctl restart mysqld"
        echo ""
        echo "5. 测试新密码："
        echo "   mysql -u root -p${NEW_PASSWORD}"
        echo ""
        exit 1
    fi
fi

echo ""
echo "步骤 4: 验证新密码"
echo "-----------------------------------------"
if mysql -u root -p${NEW_PASSWORD} -e "SELECT 'Password test successful!' as result;" 2>/dev/null; then
    echo "✓ 密码验证成功"
else
    echo "✗ 密码验证失败，请检查"
    exit 1
fi

echo ""
echo "步骤 5: 创建EIMS数据库（如果不存在）"
echo "-----------------------------------------"
mysql -u root -p${NEW_PASSWORD} <<EOF
CREATE DATABASE IF NOT EXISTS eims DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF
echo "✓ 数据库已创建"

echo ""
echo "步骤 6: 显示数据库列表"
echo "-----------------------------------------"
mysql -u root -p${NEW_PASSWORD} -e "SHOW DATABASES;"

echo ""
echo "========================================="
echo "✓ MySQL配置完成！"
echo "========================================="
echo ""
echo "数据库信息："
echo "  主机: localhost"
echo "  端口: 3306"
echo "  数据库名: eims"
echo "  用户名: root"
echo "  密码: ${NEW_PASSWORD}"
echo ""
echo "测试连接："
echo "  mysql -u root -p${NEW_PASSWORD} eims"
echo ""
