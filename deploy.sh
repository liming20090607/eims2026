#!/bin/bash
# EIMS 阿里云快速部署脚本
# 使用方法：bash deploy.sh

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="eims"
PROJECT_DIR="/var/www/eims"
PYTHON_VENV="venv"
GUNICORN_WORKERS=3

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}EIMS 阿里云自动部署脚本${NC}"
echo -e "${GREEN}======================================${NC}"

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}请使用 sudo 运行此脚本${NC}"
  exit 1
fi

# 1. 安装依赖
echo -e "${YELLOW}[1/8] 安装系统依赖...${NC}"
apt update
apt install -y python3 python3-pip python3-venv git nginx mysql-server libmysqlclient-dev

# 2. 创建项目目录
echo -e "${YELLOW}[2/8] 创建项目目录...${NC}"
mkdir -p $PROJECT_DIR
chown -R $USER:$USER $PROJECT_DIR

# 3. 配置 MySQL
echo -e "${YELLOW}[3/8] 配置 MySQL 数据库...${NC}"
read -p "请输入数据库密码：" -s DB_PASSWORD
echo
read -p "请输入数据库名称 (默认 eims): " DB_NAME
DB_NAME=${DB_NAME:-eims}

mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${PROJECT_NAME}_user'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '${PROJECT_NAME}_user'@'localhost';
FLUSH PRIVILEGES;
EOF

echo -e "${GREEN}✓ 数据库创建成功${NC}"

# 4. 创建日志目录
echo -e "${YELLOW}[4/8] 创建日志目录...${NC}"
mkdir -p /var/log/gunicorn
chown -R $USER:$USER /var/log/gunicorn

# 5. 创建 Systemd 服务
echo -e "${YELLOW}[5/8] 创建 Systemd 服务...${NC}"
cat > /etc/systemd/system/${PROJECT_NAME}.service <<EOF
[Unit]
Description=EIMS Django Application
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/$PYTHON_VENV/bin/gunicorn --workers $GUNICORN_WORKERS --bind 127.0.0.1:8000 wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# 6. 配置 Nginx
echo -e "${YELLOW}[6/8] 配置 Nginx...${NC}"
read -p "请输入域名（留空使用 IP）：" DOMAIN_NAME

if [ -z "$DOMAIN_NAME" ]; then
    SERVER_NAME="_"
else
    SERVER_NAME="$DOMAIN_NAME"
fi

cat > /etc/nginx/sites-available/${PROJECT_NAME} <<EOF
server {
    listen 80;
    server_name $SERVER_NAME;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$http_x_forwarded_proto;
    }
}
EOF

ln -sf /etc/nginx/sites-available/${PROJECT_NAME} /etc/nginx/sites-enabled/

# 7. 启动服务
echo -e "${YELLOW}[7/8] 启动服务...${NC}"
systemctl daemon-reload
systemctl start ${PROJECT_NAME}
systemctl enable ${PROJECT_NAME}
systemctl restart nginx
systemctl enable nginx

# 8. 配置防火墙
echo -e "${YELLOW}[8/8] 配置防火墙...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 'Nginx Full'
    ufw allow OpenSSH
    echo -e "${GREEN}✓ UFW 防火墙已配置${NC}"
else
    echo -e "${YELLOW}⚠ 未检测到 UFW，请手动配置防火墙${NC}"
fi

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${YELLOW}下一步操作：${NC}"
echo "1. 上传项目代码到：$PROJECT_DIR"
echo "2. 进入项目目录：cd $PROJECT_DIR"
echo "3. 创建虚拟环境：python3 -m venv venv"
echo "4. 激活虚拟环境：source venv/bin/activate"
echo "5. 安装依赖：pip install -r requirements.txt"
echo "6. 配置 .env 文件"
echo "7. 数据库迁移：python manage.py migrate"
echo "8. 收集静态文件：python manage.py collectstatic --noinput"
echo "9. 创建管理员：python manage.py createsuperuser"
echo "10. 重启服务：systemctl restart $PROJECT_NAME"
echo ""
echo -e "${YELLOW}服务状态查看：systemctl status $PROJECT_NAME${NC}"
echo -e "${YELLOW}Nginx 状态查看：systemctl status nginx${NC}"
echo -e "${YELLOW}日志查看：tail -f /var/log/gunicorn/error.log${NC}"
echo ""
echo -e "${GREEN}访问地址：http://$SERVER_NAME${NC}"
