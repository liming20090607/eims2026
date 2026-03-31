#!/bin/bash

# ========================================
# EIMS 阿里云服务器快速部署脚本
# ========================================

echo "========================================"
echo "  EIMS 阿里云服务器快速部署脚本"
echo "========================================"
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
  echo "❌ 请使用 root 用户运行此脚本"
  echo "使用方法：sudo bash deploy.sh"
  exit 1
fi

echo "✅ 开始部署..."
echo ""

# 第 1 步：安装系统依赖
echo "📦 第 1 步：安装系统依赖..."
yum update -y
yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel git nginx epel-release supervisor wget

echo "✅ 系统依赖安装完成"
echo ""

# 第 2 步：安装 Python 3.14
echo "🐍 第 2 步：安装 Python 3.14..."

cd /usr/local/src
if [ ! -f "Python-3.14.3.tgz" ]; then
  echo "正在下载 Python 3.14.3..."
  wget https://www.python.org/ftp/python/3.14.3/Python-3.14.3.tgz
fi

echo "正在解压编译 Python..."
tar -xzf Python-3.14.3.tgz
cd Python-3.14.3
./configure --enable-optimizations
make -j$(nproc)
make altinstall

echo "✅ Python 3.14 安装完成"
echo ""

# 第 3 步：创建项目目录
echo "📁 第 3 步：创建项目目录..."
mkdir -p /var/www/eims
cd /var/www/eims

echo "✅ 项目目录创建完成"
echo ""

# 第 4 步：克隆代码
echo "📥 第 4 步：克隆项目代码..."
git clone https://gitee.com/liming20090607/eims2026.git .

echo "✅ 代码克隆完成"
echo ""

# 第 5 步：创建虚拟环境
echo "🔧 第 5 步：创建虚拟环境..."
/usr/local/bin/python3.14 -m venv venv

echo "✅ 虚拟环境创建完成"
echo ""

# 第 6 步：安装 Python 依赖
echo "📦 第 6 步：安装 Python 依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn mysqlclient

echo "✅ Python 依赖安装完成"
echo ""

# 第 7 步：创建日志目录
echo "📝 第 7 步：创建日志目录..."
mkdir -p /var/log/gunicorn
chown -R $USER:$USER /var/log/gunicorn

echo "✅ 日志目录创建完成"
echo ""

# 第 8 步：创建 Gunicorn 配置
echo "⚙️ 第 8 步：创建 Gunicorn 配置..."
cat > /var/www/eims/gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
timeout = 120
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
EOF

echo "✅ Gunicorn 配置创建完成"
echo ""

# 第 9 步：创建 Supervisor 配置
echo "🔧 第 9 步：创建 Supervisor 配置..."
cat > /etc/supervisor.d/eims.conf << 'EOF'
[program:eims]
command=/var/www/eims/venv/bin/gunicorn -c /var/www/eims/gunicorn.conf.py wsgi:application
directory=/var/www/eims
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gunicorn/supervisor.log
EOF

echo "✅ Supervisor 配置创建完成"
echo ""

# 第 10 步：创建 Nginx 配置
echo "🌐 第 10 步：创建 Nginx 配置..."
cat > /etc/nginx/conf.d/eims.conf << 'EOF'
server {
    listen 80;
    server_name _;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/eims/staticfiles/;
    }

    location /media/ {
        alias /var/www/eims/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

echo "✅ Nginx 配置创建完成"
echo ""

# 第 11 步：启动服务
echo "🚀 第 11 步：启动服务..."
supervisorctl reread
supervisorctl update
supervisorctl start eims

nginx -t
systemctl reload nginx

echo "✅ 服务启动完成"
echo ""

# 总结
echo "========================================"
echo "  🎉 部署完成！"
echo "========================================"
echo ""
echo "📝 下一步操作："
echo ""
echo "1. 配置 MySQL 数据库："
echo "   yum install -y mysql-community-server"
echo "   systemctl start mysqld"
echo ""
echo "2. 修改 settings.py："
echo "   - 配置数据库连接"
echo "   - 设置 ALLOWED_HOSTS"
echo "   - 关闭 DEBUG"
echo ""
echo "3. 运行数据库迁移："
echo "   cd /var/www/eims"
echo "   source venv/bin/activate"
echo "   python manage.py makemigrations"
echo "   python manage.py migrate"
echo "   python manage.py createsuperuser"
echo "   python manage.py collectstatic --noinput"
echo ""
echo "4. 配置阿里云安全组："
echo "   - 开放端口 80"
echo "   - 开放端口 443（可选）"
echo ""
echo "5. 访问网站："
echo "   http://你的服务器 IP"
echo ""
echo "========================================"
echo ""
echo "📖 详细文档：/var/www/eims/阿里云部署指南.md"
echo ""
