#!/bin/bash
# EIMS MySQL 快速配置脚本
# 用于在服务器上快速配置 MySQL 数据库

echo "======================================"
echo "EIMS MySQL 快速配置工具"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
  echo -e "${RED}错误：请使用 sudo 或 root 用户运行此脚本${NC}"
  exit 1
fi

# 提示输入数据库信息
read -p "请输入数据库名称 [eims_db]: " DB_NAME
DB_NAME=${DB_NAME:-eims_db}

read -p "请输入数据库用户名 [eims_user]: " DB_USER
DB_USER=${DB_USER:-eims_user}

read -sp "请输入数据库密码：" DB_PASSWORD
echo ""

read -sp "请确认密码：" DB_PASSWORD_CONFIRM
echo ""

if [ "$DB_PASSWORD" != "$DB_PASSWORD_CONFIRM" ]; then
    echo -e "${RED}错误：两次输入的密码不一致${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}即将执行以下操作:${NC}"
echo "1. 创建数据库：$DB_NAME"
echo "2. 创建用户：$DB_USER"
echo "3. 授予权限"
echo ""

read -p "是否继续？[y/N]: " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}已取消${NC}"
    exit 0
fi

# 执行 MySQL 命令
mysql -u root <<EOF
-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（如果不存在）
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';

-- 授予权限
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 显示结果
SELECT '数据库创建成功！' AS result;
SELECT CONCAT('数据库名：', '$DB_NAME') AS info;
SELECT CONCAT('用户名：', '$DB_USER') AS info;
SELECT '密码：已设置' AS info;
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ MySQL 数据库配置完成！${NC}"
    echo ""
    echo "请在 .env 文件中更新以下配置："
    echo "----------------------------------------"
    echo "DB_NAME=\"$DB_NAME\""
    echo "DB_USER=\"$DB_USER\""
    echo "DB_PASSWORD=\"$DB_PASSWORD\""
    echo "DB_HOST=\"localhost\""
    echo "DB_PORT=\"3306\""
    echo "----------------------------------------"
    echo ""
else
    echo ""
    echo -e "${RED}✗ MySQL 配置失败，请检查 MySQL 服务状态${NC}"
    exit 1
fi
