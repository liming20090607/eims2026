#!/bin/bash

echo "======================================"
echo "EIMS 系统生产环境部署脚本
echo "======================================"
echo ""

# 检查是否 root
if [ "$EUID" -ne 0 ]; then 
  echo "❌ 请使用 root 用户或 sudo 执行"
  exit 1
fi

# 配置变量（请修改为您的实际信息）
DOMAIN="yourdomain.com"     # ← 修改为您的域名
EMAIL="your@email.com"      # ← 修改为您的邮箱
PROJECT_PATH="/var/www/eims"
PYTHON_VENV="$PROJECT_PATH/venv"

echo "📋 配置信息："
echo "  域名：$DOMAIN"
echo "  邮箱：$EMAIL"
echo "  项目路径：$PROJECT_PATH"
echo ""

# 确认配置
read -p "确认配置是否正确？(y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "请修改脚本中的配置后重新运行"
    exit 1
fi

echo ""
echo "======================================"
echo "开始部署 EIMS 系统...
echo "======================================"
echo ""

# 1. 更新系统和安装依赖
echo "[1/12] 更新系统并安装依赖..."
yum update -y
yum install -y epel-release
yum install -y python3 python3-pip python3-venv
yum install -y nginx git vim
yum install -y certbot python3-certbot-nginx
echo "✅ 依赖安装完成"
echo ""

# 2. 创建项目目录
echo "[2/12] 创建项目目录..."
mkdir -p $PROJECT_PATH
mkdir -p /var/log/django
mkdir -p /var/log/gunicorn
cd $PROJECT_PATH
echo "✅ 目录创建完成"
echo ""

# 3. 上传/克隆代码
echo "[3/12] 准备代码..."
# 方式 1: 从 Git 克隆（如果有）
# git clone https://github.com/yourusername/EIMS2026.git .
# git checkout main

# 方式 2: 手动上传（已存在则跳过）
if [ -f "manage.py" ]; then
    echo "✅ 代码已存在"
else
    echo "⚠️ 请手动上传代码到 $PROJECT_PATH"
    echo "   可以使用 scp 命令或 FTP 工具"
    exit 1
fi
echo ""

# 4. 创建虚拟环境
echo "[4/12] 创建 Python 虚拟环境..."
python3 -m venv $PYTHON_VENV
source $PYTHON_VENV/bin/activate
echo "✅ 虚拟环境创建完成"
echo ""

# 5. 安装 Python 依赖
echo "[5/12] 安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
echo "✅ 依赖安装完成"
echo ""

# 6. 配置环境变量
echo "[6/12] 配置环境变量..."
cat > $PROJECT_PATH/.env << EOF
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,39.106.41.239
DATABASE_URL=sqlite:///db.sqlite3
EOF
echo "✅ 环境变量配置完成"
echo ""

# 7. 数据库迁移
echo "[7/12] 数据库迁移..."
python manage.py migrate
python manage.py collectstatic --noinput
echo "✅ 数据库迁移完成"
echo ""

# 8. 创建超级用户（可选）
echo "[8/12] 创建超级用户..."
read -p "是否现在创建 Django 超级用户？(y/n): " create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi
echo ""

# 9. 创建 Gunicorn 服务
echo "[9/12] 创建 Gunicorn systemd 服务..."
cat > /etc/systemd/system/eims.service << EOF
[Unit]
Description=EIMS Gunicorn instance
After=network.target

[Service]
User=root
Group=nginx
WorkingDirectory=$PROJECT_PATH
ExecStart=$PYTHON_VENV/bin/gunicorn --workers 3 --bind unix:$PROJECT_PATH/eims.sock \\
    wsgi:application

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable eims
systemctl start eims
echo "✅ Gunicorn 服务创建完成"
echo ""

# 10. 配置 Nginx
echo "[10/12] 配置 Nginx..."
cat > /etc/nginx/conf.d/eims.conf << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location / {
        proxy_pass http://unix:$PROJECT_PATH/eims.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static/ {
        alias $PROJECT_PATH/static/;
    }
    
    location /media/ {
        alias $PROJECT_PATH/media/;
    }
}
EOF

nginx -t
systemctl restart nginx
echo "✅ Nginx 配置完成"
echo ""

# 11. 申请 SSL 证书
echo "[11/12] 申请 SSL 证书..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --redirect --non-interactive
echo "✅ SSL 证书申请完成"
echo ""

# 12. 配置防火墙
echo "[12/12] 配置防火墙..."
if systemctl is-active --quiet firewalld; then
    firewall-cmd --zone=public --add-port=80/tcp --permanent
    firewall-cmd --zone=public --add-port=443/tcp --permanent
    firewall-cmd --reload
    echo "✅ 防火墙配置完成"
else
    echo "⚠️  firewalld 未运行，跳过"
fi
echo ""

# 验证服务状态
echo "======================================"
echo "验证服务状态...
echo "======================================"
echo ""

echo "Gunicorn 状态:"
systemctl status eims --no-pager -l
echo ""

echo "Nginx 状态:"
systemctl status nginx --no-pager -l
echo ""

echo "SSL 证书信息:"
certbot certificates
echo ""

# 完成
echo "======================================"
echo "✅ 部署完成！
echo "======================================"
echo ""
echo "📊 配置信息："
echo "  域名：$DOMAIN"
echo "  访问地址：https://$DOMAIN"
echo "  证书位置：/etc/letsencrypt/live/$DOMAIN/"
echo "  证书有效期：90 天（自动续期）"
echo ""
echo " 常用命令："
echo "  查看日志：tail -f /var/log/django/error.log"
echo "  重启服务：systemctl restart eims nginx"
echo "  续期证书：certbot renew"
echo ""
echo "⚠️  下一步："
echo "  1. 配置 DNS 解析（A 记录）"
echo "  2. 网站首页添加备案号"
echo "  3. 配置公安联网备案"
echo ""
