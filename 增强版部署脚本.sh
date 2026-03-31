#!/bin/bash
# EIMS 阿里云一键部署脚本（增强版）
# 使用方法：bash deploy.sh

set -e  # 遇到错误立即停止

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量（可使用默认值或手动输入）
DB_NAME="eims_db"
DB_USER="eims_user"
DB_PASSWORD=""
DJANGO_SECRET=""
PROJECT_DIR="/home/eims"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}EIMS 系统一键部署脚本 (增强版)${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# 交互式配置
echo -e "${YELLOW}【配置】数据库密码（直接回车使用随机密码）:${NC}"
read -p "> " DB_PASSWORD_INPUT
if [ -z "$DB_PASSWORD_INPUT" ]; then
    DB_PASSWORD=$(openssl rand -base64 12)
    echo -e "${GREEN}✓ 生成随机数据库密码：${DB_PASSWORD}${NC}"
else
    DB_PASSWORD="$DB_PASSWORD_INPUT"
fi

echo ""
echo -e "${YELLOW}【配置】项目目录 [默认：${PROJECT_DIR}]:${NC}"
read -p "> " PROJECT_DIR_INPUT
if [ -n "$PROJECT_DIR_INPUT" ]; then
    PROJECT_DIR="$PROJECT_DIR_INPUT"
fi

echo ""
echo -e "${YELLOW}【配置】Django SECRET_KEY（直接回车使用随机密钥）:${NC}"
read -p "> " DJANGO_SECRET_INPUT
if [ -z "$DJANGO_SECRET_INPUT" ]; then
    DJANGO_SECRET=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    echo -e "${GREEN}✓ 生成随机 SECRET_KEY: ${DJANGO_SECRET}${NC}"
else
    DJANGO_SECRET="$DJANGO_SECRET_INPUT"
fi

echo ""

# 检查是否在正确的项目目录
if [ ! -f "manage.py" ]; then
    echo -e "${RED}✗ 错误：请在项目根目录下执行此脚本（包含 manage.py 的目录）${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 当前目录：$(pwd)${NC}"
echo ""

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Step 1: 配置 MySQL 数据库${NC}"
echo -e "${BLUE}=========================================${NC}"

# 检查 MySQL 是否运行
if ! systemctl is-active --quiet mysql && ! systemctl is-active --quiet mysqld; then
    echo -e "${RED}✗ MySQL 服务未运行，请先启动 MySQL${NC}"
    echo "命令：systemctl start mysql 或 systemctl start mysqld"
    exit 1
fi

echo "创建数据库和用户..."
mysql -u root << EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

echo -e "${GREEN}✓ 数据库创建成功${NC}"
echo "  数据库名：${DB_NAME}"
echo "  用户名：${DB_USER}"
echo "  密码：${DB_PASSWORD}"
echo ""

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Step 2: 安装 Python 依赖${NC}"
echo -e "${BLUE}=========================================${NC}"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境创建完成${NC}"
else
    echo -e "${GREEN}✓ 虚拟环境已存在${NC}"
fi

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip --quiet

# 安装依赖
echo "安装项目依赖..."
pip install -r requirements.txt --quiet

# 安装生产环境依赖
echo "安装生产环境依赖..."
pip install gunicorn django-widget-tweaks --quiet

echo -e "${GREEN}✓ 依赖安装完成${NC}"
echo ""

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Step 3: 创建 .env 配置文件${NC}"
echo -e "${BLUE}=========================================${NC}"

# 获取服务器 IP
SERVER_IP=$(hostname -I | awk '{print $1}')
if [ -z "$SERVER_IP" ]; then
    SERVER_IP="127.0.0.1"
fi

cat > .env << EOF
# Django 生产环境配置
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=${DJANGO_SECRET}
DJANGO_ALLOWED_HOSTS=${SERVER_IP},localhost,127.0.0.1

# 数据库配置
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=localhost
DB_PORT=3306

# 文件配置
MEDIA_URL=/media/
MEDIA_ROOT=${PROJECT_DIR}/media
STATIC_URL=/static/
STATIC_ROOT=${PROJECT_DIR}/staticfiles
EOF

echo -e "${GREEN}✓ 配置文件创建完成${NC}"
echo "  服务器 IP: ${SERVER_IP}"
echo "  允许访问的主机：${SERVER_IP}, localhost, 127.0.0.1"
echo ""

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Step 4: 数据库迁移${NC}"
echo -e "${BLUE}=========================================${NC}"

# 应用迁移
echo "应用数据库迁移..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

echo -e "${GREEN}✓ 数据库迁移完成${NC}"
echo ""

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Step 5: 创建 Gunicorn 系统服务${NC}"
echo -e "${BLUE}=========================================${NC}"

# 检查项目目录
REAL_PROJECT_DIR=$(pwd)

cat > /etc/systemd/system/eims.service << EOF
[Unit]
Description=EIMS Django Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=${REAL_PROJECT_DIR}
ExecStart=${REAL_PROJECT_DIR}/venv/bin/gunicorn \\
    --access-logfile - \\
    --workers 3 \\
    --bind unix:${REAL_PROJECT_DIR}/eims.sock \\
    wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重载 systemd
systemctl daemon-reload

# 启动并启用服务
systemctl start eims
systemctl enable eims

echo -e "${GREEN}✓ Gunicorn 服务创建并启动${NC}"
echo "  工作目录：${REAL_PROJECT_DIR}"
echo "  Worker 数量：3"
echo ""

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Step 6: 安装并配置 Nginx${NC}"
echo -e "${BLUE}=========================================${NC}"

# 检查 Nginx 是否已安装
if ! command -v nginx &> /dev/null; then
    echo "Nginx 未安装，开始安装..."
    apt update --quiet
    apt install nginx -y --quiet
    echo -e "${GREEN}✓ Nginx 安装完成${NC}"
else
    echo -e "${GREEN}✓ Nginx 已安装${NC}"
fi

# 创建 Nginx 配置
cat > /etc/nginx/sites-available/eims << EOF
server {
    listen 80;
    server_name ${SERVER_IP};

    # 日志配置
    access_log /var/log/nginx/eims-access.log;
    error_log /var/log/nginx/eims-error.log;

    # 静态文件
    location /static/ {
        alias ${REAL_PROJECT_DIR}/staticfiles/;
    }
    
    # 媒体文件
    location /media/ {
        alias ${REAL_PROJECT_DIR}/media/;
    }

    # 主应用
    location / {
        include proxy_params;
        proxy_pass http://unix:${REAL_PROJECT_DIR}/eims.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启用站点（先备份默认配置）
if [ -f /etc/nginx/sites-enabled/default ]; then
    echo "备份默认 Nginx 配置..."
    mv /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.bak
fi

# 创建软链接
ln -sf /etc/nginx/sites-available/eims /etc/nginx/sites-enabled/

# 测试配置
echo "测试 Nginx 配置..."
nginx -t

# 重启 Nginx
systemctl restart nginx
systemctl enable nginx

echo -e "${GREEN}✓ Nginx 配置完成${NC}"
echo "  监听端口：80"
echo "  服务器名称：${SERVER_IP}"
echo ""

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Step 7: 创建超级管理员${NC}"
echo -e "${BLUE}=========================================${NC}"
echo "请设置管理员账号信息:"
echo "（提示：用户名建议使用 admin，邮箱可留空，密码需输入两次）"
echo ""
python manage.py createsuperuser

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "✅ 访问地址："
echo "   首页：http://${SERVER_IP}/"
echo "   Admin 后台：http://${SERVER_IP}/admin/"
echo ""
echo "📋 重要信息记录:"
echo "   数据库名：${DB_NAME}"
echo "   数据库用户：${DB_USER}"
echo "   数据库密码：${DB_PASSWORD}"
echo ""
echo -e "${YELLOW}⚠️ 重要提示:${NC}"
echo "1. 已将 .env 文件保存在项目目录，请及时备份并修改密码"
echo "2. 在阿里云控制台安全组开放 80 端口（HTTP）"
echo "3. 建议配置 HTTPS 加密（使用 certbot 免费证书）"
echo "4. 定期备份数据库（参考 backup_db.sh 脚本）"
echo ""
echo "🔍 服务状态查看:"
echo "   systemctl status eims      # Gunicorn 状态"
echo "   systemctl status nginx     # Nginx 状态"
echo ""
echo "📝 日志查看:"
echo "   tail -f /var/log/nginx/error.log    # Nginx 错误日志"
echo "   journalctl -u eims -f               # Gunicorn 日志"
echo ""
echo "🔄 常用命令:"
echo "   systemctl restart eims     # 重启应用"
echo "   systemctl restart nginx    # 重启 Nginx"
echo "   bash backup_db.sh          # 备份数据库"
echo ""
echo "💡 如需重新运行部署脚本，直接执行：bash deploy.sh"
echo ""
