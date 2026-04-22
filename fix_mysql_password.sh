#!/bin/bash
# MySQL 密码修复脚本 - 自动修复云服务器数据库连接问题

set -e

echo "========================================="
echo "MySQL 数据库连接修复工具"
echo "========================================="
echo ""

# 配置变量
MYSQL_PASSWORD="mysql2026!"  # 本地使用的密码
MYSQL_USER="root"
MYSQL_HOST="localhost"

echo "📋 当前配置信息："
echo "  MySQL 用户: $MYSQL_USER"
echo "  MySQL 主机: $MYSQL_HOST"
echo "  预期密码: $MYSQL_PASSWORD"
echo ""

# 步骤 1: 检查 MySQL 服务状态
echo "[步骤 1/5] 检查 MySQL 服务状态..."
echo "-----------------------------------------"
if systemctl is-active --quiet mysql || systemctl is-active --quiet mysqld; then
    echo "✅ MySQL 服务正在运行"
else
    echo "❌ MySQL 服务未运行"
    echo "正在启动 MySQL 服务..."
    systemctl start mysql || systemctl start mysqld
    sleep 2
    echo "✅ MySQL 服务已启动"
fi
echo ""

# 步骤 2: 测试当前密码是否有效
echo "[步骤 2/5] 测试 MySQL root 密码..."
echo "-----------------------------------------"
if mysql -u root -p"$MYSQL_PASSWORD" -e "SELECT 1;" &>/dev/null; then
    echo "✅ 当前密码 '$MYSQL_PASSWORD' 可以正常登录"
    echo ""
    echo "🎉 密码验证成功！问题可能是其他原因，请检查："
    echo "   1. settings.py 中的数据库配置"
    echo "   2. .env 文件中的 DB_PASSWORD 设置"
    echo "   3. 数据库是否存在"
    exit 0
else
    echo "❌ 当前密码 '$MYSQL_PASSWORD' 无法登录"
    echo ""
    echo "🔧 正在重置 MySQL root 密码..."
fi
echo ""

# 步骤 3: 重置 MySQL root 密码
echo "[步骤 3/5] 重置 MySQL root 密码..."
echo "-----------------------------------------"

# 方法 1: 使用 skip-grant-tables 重置密码
echo "正在停止 MySQL 服务..."
systemctl stop mysql || systemctl stop mysqld
sleep 2

echo "以安全模式启动 MySQL..."
mysqld_safe --skip-grant-tables &
sleep 3

echo "重置 root 密码..."
mysql -u root <<EOF
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '$MYSQL_PASSWORD';
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$MYSQL_PASSWORD';
FLUSH PRIVILEGES;
EOF

echo "关闭安全模式..."
kill $(cat /var/run/mysqld/mysqld.pid 2>/dev/null || echo "") 2>/dev/null || true
sleep 2

echo "正常启动 MySQL..."
systemctl start mysql || systemctl start mysqld
sleep 3

echo "✅ MySQL root 密码已重置为: $MYSQL_PASSWORD"
echo ""

# 步骤 4: 验证新密码
echo "[步骤 4/5] 验证新密码..."
echo "-----------------------------------------"
if mysql -u root -p"$MYSQL_PASSWORD" -e "SELECT 1;" &>/dev/null; then
    echo "✅ 新密码验证成功！"
else
    echo "❌ 密码重置失败，请手动检查"
    exit 1
fi
echo ""

# 步骤 5: 检查数据库是否存在
echo "[步骤 5/5] 检查必需的数据库..."
echo "-----------------------------------------"
DATABASES=("eims" "eims_root" "eims_dingce" "eims_shengchang" "eims_jiachengda")

for db in "${DATABASES[@]}"; do
    if mysql -u root -p"$MYSQL_PASSWORD" -e "USE $db;" &>/dev/null; then
        echo "✅ 数据库 '$db' 存在"
    else
        echo "⚠️  数据库 '$db' 不存在"
        echo "   正在创建数据库 '$db'..."
        mysql -u root -p"$MYSQL_PASSWORD" -e "CREATE DATABASE $db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        echo "✅ 数据库 '$db' 已创建"
    fi
done
echo ""

# 步骤 6: 确保 .env 文件中的密码正确
echo "[额外步骤] 检查 .env 文件配置..."
echo "-----------------------------------------"
ENV_FILE="/var/www/eims/.env"
if [ -f "$ENV_FILE" ]; then
    if grep -q "DB_PASSWORD=" "$ENV_FILE"; then
        # 更新密码
        sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=\"$MYSQL_PASSWORD\"/" "$ENV_FILE"
        echo "✅ .env 文件中的 DB_PASSWORD 已更新"
    else
        echo "DB_PASSWORD=\"$MYSQL_PASSWORD\"" >> "$ENV_FILE"
        echo "✅ .env 文件中已添加 DB_PASSWORD"
    fi
else
    echo "⚠️  .env 文件不存在，正在创建..."
    cat > "$ENV_FILE" <<EOF
DB_NAME="eims"
DB_USER="root"
DB_PASSWORD="$MYSQL_PASSWORD"
DB_HOST="localhost"
DB_PORT="3306"
EOF
    echo "✅ .env 文件已创建"
fi
echo ""

# 总结
echo "========================================="
echo "✅ MySQL 修复完成！"
echo "========================================="
echo ""
echo "📊 修复摘要："
echo "  - MySQL root 密码已重置为: $MYSQL_PASSWORD"
echo "  - 所有必需数据库已检查/创建"
echo "  - .env 文件已更新"
echo ""
echo "🚀 下一步操作："
echo "  1. 重启 Gunicorn 服务:"
echo "     sudo systemctl restart gunicorn"
echo "  2. 或者重启整个服务器:"
echo "     sudo reboot"
echo ""
echo "  3. 访问网站测试:"
echo "     http://39.106.41.239/login/"
echo ""
echo "========================================="
