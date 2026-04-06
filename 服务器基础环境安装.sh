#!/bin/bash

echo "======================================"
echo "EIMS 服务器快速部署脚本
echo "======================================"
echo ""

# 检查是否 root
if [ "$EUID" -ne 0 ]; then 
  echo "❌ 请使用 root 用户或 sudo 执行"
  exit 1
fi

# 检测系统
echo "检测系统..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    echo "✅ 系统：$OS"
else
    echo "❌ 无法检测系统类型"
    exit 1
fi

echo ""
echo "======================================"
echo "安装开发工具...
echo "======================================"
echo ""

case $OS in
    centos|rhel|almalinux|rocky)
        echo "[1/5] 安装 EPEL 仓库..."
        yum install epel-release -y
        
        echo "[2/5] 安装 Python 开发工具..."
        yum install -y python3 python3-pip python3-devel
        yum install -y gcc gcc-c++ make
        yum install -y git vim wget curl
        yum install -y nginx
        
        echo "[3/5] 安装 Certbot..."
        yum install -y certbot python3-certbot-nginx
        ;;
        
    ubuntu|debian)
        echo "[1/5] 更新软件包..."
        apt-get update
        
        echo "[2/5] 安装 Python 开发工具..."
        apt-get install -y python3 python3-pip python3-dev
        apt-get install -y gcc g++ make
        apt-get install -y git vim wget curl
        apt-get install -y nginx
        
        echo "[3/5] 安装 Certbot..."
        apt-get install -y certbot python3-certbot-nginx
        ;;
        
    *)
        echo "❌ 不支持的系统：$OS"
        exit 1
        ;;
esac

echo ""
echo "[4/5] 安装 Django 和 Gunicorn..."
pip3 install django gunicorn python-dotenv pillow

echo ""
echo "[5/5] 验证安装..."
python3 --version
pip3 --version
django-admin --version
nginx -v
certbot --version

echo ""
echo "======================================"
echo "✅ 基础环境安装完成！
echo "======================================"
echo ""
echo "下一步："
echo "  1. 上传项目代码到 /var/www/eims"
echo "  2. 配置域名（如果有）"
echo "  3. 执行完整部署脚本"
echo ""
