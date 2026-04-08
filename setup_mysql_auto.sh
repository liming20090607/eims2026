#!/bin/bash
# MySQL root 密码自动设置脚本（非交互模式）
# 此脚本在云服务器上自动执行，无需手动确认

set -e

echo "========================================="
echo "MySQL root 用户密码自动设置"
echo "========================================="
echo ""

# 设置密码
NEW_PASSWORD="root123"

echo "正在设置 MySQL root 密码: ${NEW_PASSWORD}"
echo "注意: 这是一个简单的密码，仅用于开发和测试环境"
echo ""

echo "步骤 1: 检查 MySQL 服务状态"
echo "-----------------------------------------"
if systemctl is-active --quiet mysqld || systemctl is-active --quiet mysql; then
    echo "✓ MySQL 服务正在运行"
else
    echo "MySQL 服务未运行，正在启动..."
    systemctl start mysqld 2>/dev/null || systemctl start mysql 2>/dev/null || true
    sleep 2
fi

echo ""
echo "步骤 2: 设置 root 密码"
echo "-----------------------------------------"

# 尝试直接设置密码（无需当前密码）
if mysql -u root -e "SELECT 1;" 2>/dev/null; then
    echo "可以直接登录 MySQL（无需密码）"
    
    # 检查 MySQL 版本，使用不同的语法
    MYSQL_VERSION=$(mysql -u root -e "SELECT VERSION();" 2>/dev/null | tail -1)
    echo "MySQL 版本: ${MYSQL_VERSION}"
    
    if [[ "$MYSQL_VERSION" == "5.7"* ]] || [[ "$MYSQL_VERSION" == "5.6"* ]]; then
        # MySQL 5.x 使用 SET PASSWORD
        mysql -u root <<EOF
SET PASSWORD FOR 'root'@'localhost' = PASSWORD('${NEW_PASSWORD}');
FLUSH PRIVILEGES;
EOF
    else
        # MySQL 8.x 使用 ALTER USER
        mysql -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '${NEW_PASSWORD}';
FLUSH PRIVILEGES;
EOF
    fi
    echo "✓ 密码设置成功"
    
elif mysql -u root -e "SELECT 1;" 2>/dev/null; then
    echo "使用系统认证登录"
    
    mysql -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '${NEW_PASSWORD}';
FLUSH PRIVILEGES;
EOF
    echo "✓ 密码设置成功"
    
else
    echo "需要重置 MySQL root 密码"
    echo "正在执行密码重置流程..."
    
    # 尝试找到 MySQL 配置文件
    MYSQL_CNF=$(find /etc -name "*.cnf" 2>/dev/null | grep -E "(my.cnf|mysql.cnf)" | head -1)
    
    if [ -z "$MYSQL_CNF" ]; then
        echo "未找到 MySQL 配置文件，尝试其他方式..."
        MYSQL_CNF="/etc/my.cnf"
    fi
    
    echo "使用配置文件: ${MYSQL_CNF}"
    
    # 停止 MySQL
    systemctl stop mysqld 2>/dev/null || systemctl stop mysql 2>/dev/null || service mysqld stop 2>/dev/null || service mysql stop 2>/dev/null || true
    sleep 2
    
    # 备份原配置文件
    cp "${MYSQL_CNF}" "${MYSQL_CNF}.bak" 2>/dev/null || true
    
    # 添加跳过权限表配置
    echo "" >> "${MYSQL_CNF}"
    echo "[mysqld]" >> "${MYSQL_CNF}"
    echo "skip-grant-tables" >> "${MYSQL_CNF}"
    
    # 启动 MySQL
    systemctl start mysqld 2>/dev/null || systemctl start mysql 2>/dev/null || service mysqld start 2>/dev/null || service mysql start 2>/dev/null || true
    sleep 3
    
    # 登录并重置密码
    mysql -u root <<EOF
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '${NEW_PASSWORD}';
FLUSH PRIVILEGES;
EOF
    
    # 恢复原配置文件
    if [ -f "${MYSQL_CNF}.bak" ]; then
        mv "${MYSQL_CNF}.bak" "${MYSQL_CNF}"
    else
        # 删除添加的配置
        sed -i '/skip-grant-tables/d' "${MYSQL_CNF}"
    fi
    
    # 重启 MySQL
    systemctl restart mysqld 2>/dev/null || systemctl restart mysql 2>/dev/null || service mysqld restart 2>/dev/null || service mysql restart 2>/dev/null || true
    sleep 3
    
    echo "✓ 密码重置成功"
fi

echo ""
echo "步骤 3: 验证新密码"
echo "-----------------------------------------"
if mysql -u root -p${NEW_PASSWORD} -e "SELECT 'Password test successful!' as result;" 2>/dev/null; then
    echo "✓ 密码验证成功"
else
    echo "✗ 密码验证失败"
    exit 1
fi

echo ""
echo "步骤 4: 创建 EIMS 数据库"
echo "-----------------------------------------"
mysql -u root -p${NEW_PASSWORD} <<EOF
CREATE DATABASE IF NOT EXISTS eims DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF
echo "✓ 数据库已创建"

echo ""
echo "步骤 5: 显示数据库列表"
echo "-----------------------------------------"
mysql -u root -p${NEW_PASSWORD} -e "SHOW DATABASES;"

echo ""
echo "========================================="
echo "✓ MySQL 配置完成！"
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
