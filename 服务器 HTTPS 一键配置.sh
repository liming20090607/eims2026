#!/bin/bash

echo "======================================"
echo "阿里云服务器 HTTPS 一键配置
echo "======================================"
echo ""

# 检查是否 root
if [ "$EUID" -ne 0 ]; then 
  echo "❌ 请使用 root 用户或 sudo 执行"
  exit 1
fi

# 检测系统类型
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ 无法检测系统类型"
    exit 1
fi

echo "✅ 检测到系统：$OS"
echo ""

# 读取域名
read -p "请输入您的域名（例如：example.com）: " DOMAIN
read -p "请输入邮箱地址： " EMAIL

echo ""
echo "======================================"
echo "开始配置 HTTPS...
echo "======================================"
echo ""

# 根据系统类型安装
case $OS in
    centos|rhel|almalinux|rocky)
        echo "[1/6] 安装 EPEL 仓库..."
        yum install epel-release -y
        
        echo "[2/6] 安装 Certbot..."
        yum install certbot python3-certbot-nginx -y
        ;;
    ubuntu|debian)
        echo "[1/6] 更新软件包..."
        apt-get update
        
        echo "[2/6] 安装 Certbot..."
        apt-get install certbot python3-certbot-nginx -y
        ;;
    *)
        echo "❌ 不支持的系统：$OS"
        echo "请使用 CentOS/RHEL 或 Ubuntu/Debian"
        exit 1
        ;;
esac

# 验证安装
echo "[3/6] 验证 Certbot 安装..."
certbot --version

# 配置 Nginx
echo "[4/6] 测试 Nginx 配置..."
nginx -t

# 申请证书
echo "[5/6] 申请 SSL 证书..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --redirect

# 配置防火墙
echo "[6/6] 配置防火墙..."
if systemctl is-active --quiet firewalld; then
    firewall-cmd --zone=public --add-port=80/tcp --permanent
    firewall-cmd --zone=public --add-port=443/tcp --permanent
    firewall-cmd --reload
fi

echo ""
echo "======================================"
echo "✅ HTTPS 配置完成！
echo "======================================"
echo ""
echo " 配置信息："
echo "  域名：$DOMAIN"
echo "  邮箱：$EMAIL"
echo "  访问地址：https://$DOMAIN"
echo "  证书位置：/etc/letsencrypt/live/$DOMAIN/"
echo ""
echo "⏰ 证书有效期：90 天（自动续期）"
echo ""
echo "📝 下一步："
echo "  1. 浏览器访问 https://$DOMAIN 测试"
echo "  2. 检查浏览器是否显示安全锁图标"
echo "  3. 查看证书详情：certbot certificates"
echo ""
