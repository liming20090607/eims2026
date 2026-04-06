# 阿里云服务器 HTTPS 配置完全指南

**服务器**：阿里云 ECS（CentOS/RHEL）  
**目标**：配置 HTTPS，消除"不安全"警告  
**证书**：Let's Encrypt（免费）

---

## 🔍 **系统识别**

### **检查您的系统类型**

```bash
# 查看系统版本
cat /etc/os-release

# 或者
cat /etc/redhat-release
```

**预期输出**：
```
CentOS Linux release 7.x 或 8.x
或
Red Hat Enterprise Linux release 8.x
```

---

## 🚀 **快速安装（CentOS/RHEL）**

### **方案 1：使用 EPEL + Certbot（推荐）**

#### **步骤 1：安装 EPEL 仓库**

```bash
sudo yum install epel-release -y
```

---

#### **步骤 2：安装 Certbot**

```bash
sudo yum install certbot python3-certbot-nginx -y
```

**或者（CentOS 7）**：
```bash
sudo yum install certbot python2-certbot-nginx -y
```

---

#### **步骤 3：验证安装**

```bash
certbot --version
```

**预期输出**：
```
certbot 1.x.x
```

---

#### **步骤 4：申请证书**

**方式 A - 自动配置 Nginx（推荐）**：
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**方式 B - 仅获取证书**：
```bash
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

**按提示操作**：
1. 输入邮箱地址
2. 同意服务条款（输入 A）
3. 选择是否分享邮件（输入 Y 或 N）
4. Certbot 自动配置 Nginx

---

#### **步骤 5：验证证书**

**证书位置**：
```
/etc/letsencrypt/live/yourdomain.com/
├── fullchain.pem    ← 完整证书链
├── privkey.pem      ← 私钥
├── cert.pem         ← 证书
└── chain.pem        ← 证书链
```

---

### **方案 2：使用 Snap 安装（备选）**

如果方案 1 失败，使用此方案：

#### **步骤 1：安装 Snap**

```bash
# CentOS 7
sudo yum install snapd -y
sudo systemctl enable --now snapd.socket

# CentOS 8/RHEL 8
sudo dnf install snapd -y
sudo systemctl enable --now snapd.socket

# 启用经典模式
sudo ln -s /var/lib/snapd/snap /snap
```

---

#### **步骤 2：安装 Certbot**

```bash
sudo snap install --classic certbot
```

---

#### **步骤 3：创建软链接**

```bash
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

---

#### **步骤 4：申请证书**

```bash
sudo certbot --nginx -d yourdomain.com
```

---

## 🔧 **手动配置 Nginx**

如果 Certbot 未能自动配置，手动配置：

### **步骤 1：编辑 Nginx 配置**

```bash
sudo vi /etc/nginx/nginx.conf
或
sudo vi /etc/nginx/conf.d/default.conf
```

---

### **步骤 2：添加 HTTPS 配置**

```nginx
# HTTP 服务器 - 强制跳转到 HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 服务器
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL 证书路径
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL 优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Django 代理配置
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /static/ {
        alias /var/www/eims/static/;
    }

    # 媒体文件
    location /media/ {
        alias /var/www/eims/media/;
    }
}
```

---

### **步骤 3：测试配置**

```bash
sudo nginx -t
```

**预期输出**：
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

### **步骤 4：重启 Nginx**

```bash
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 📦 **阿里云特别配置**

### **配置安全组**

**必须开放端口**：
- ✅ 80（HTTP）
- ✅ 443（HTTPS）
- ✅ 8000（Django，仅内网）

**操作步骤**：
1. 登录阿里云控制台
2. 云服务器 ECS → 实例
3. 安全组 → 配置规则
4. 添加入站规则：
   - 端口：80, 443
   - 授权对象：0.0.0.0/0
   - 协议：TCP

---

### **防火墙配置**

```bash
# 检查防火墙状态
sudo systemctl status firewalld

# 开放端口（如果防火墙开启）
sudo firewall-cmd --zone=public --add-port=80/tcp --permanent
sudo firewall-cmd --zone=public --add-port=443/tcp --permanent
sudo firewall-cmd --reload

# 或者关闭防火墙（开发环境）
sudo systemctl stop firewalld
sudo systemctl disable firewalld
```

---

## 🔄 **证书自动续期**

### **Let's Encrypt 证书有效期**

- ⏰ **90 天**
- ✅ 支持自动续期
- ✅ Certbot 自动添加定时任务

---

### **手动测试续期**

```bash
sudo certbot renew --dry-run
```

**预期输出**：
```
Congratulations, all renewals succeeded.
```

---

### **查看定时任务**

```bash
sudo systemctl list-timers | grep certbot
```

**预期输出**：
```
certbot.timer
```

---

### **手动续期**

```bash
# 停止 Nginx（standalone 模式需要）
sudo systemctl stop nginx

# 续期证书
sudo certbot renew

# 重启 Nginx
sudo systemctl start nginx
```

---

## 🎯 **完整部署流程**

### **一键部署脚本**

创建脚本 `/root/setup_https.sh`：

```bash
#!/bin/bash

echo "======================================"
echo "阿里云服务器 HTTPS 一键配置
echo "======================================"

# 检查是否 root
if [ "$EUID" -ne 0 ]; then 
  echo "请使用 root 用户或 sudo 执行"
  exit 1
fi

# 读取域名
read -p "请输入您的域名（例如：example.com）: " DOMAIN
read -p "请输入邮箱地址： " EMAIL

# 1. 安装 EPEL
echo "[1/6] 安装 EPEL 仓库..."
yum install epel-release -y

# 2. 安装 Certbot
echo "[2/6] 安装 Certbot..."
yum install certbot python3-certbot-nginx -y

# 3. 验证安装
echo "[3/6] 验证安装..."
certbot --version

# 4. 配置 Nginx
echo "[4/6] 配置 Nginx..."
nginx -t

# 5. 申请证书
echo "[5/6] 申请 SSL 证书..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --redirect

# 6. 配置防火墙
echo "[6/6] 配置防火墙..."
firewall-cmd --zone=public --add-port=80/tcp --permanent
firewall-cmd --zone=public --add-port=443/tcp --permanent
firewall-cmd --reload

echo "======================================"
echo "✅ HTTPS 配置完成！
echo "======================================"
echo ""
echo "访问地址：https://$DOMAIN"
echo "证书位置：/etc/letsencrypt/live/$DOMAIN/"
echo ""
echo "提示：证书有效期 90 天，会自动续期"
```

---

### **使用脚本**

```bash
# 创建脚本
vi /root/setup_https.sh

# 粘贴上面的内容，保存退出

# 赋予执行权限
chmod +x /root/setup_https.sh

# 执行脚本
./setup_https.sh
```

---

## 📊 **配置验证**

### **检查 HTTPS**

```bash
# 测试 HTTPS 访问
curl -I https://yourdomain.com
```

**预期输出**：
```
HTTP/2 200 
server: nginx
```

---

### **检查 HTTP 跳转**

```bash
curl -I http://yourdomain.com
```

**预期输出**：
```
HTTP/1.1 301 Moved Permanently
Location: https://yourdomain.com/
```

---

### **在线验证工具**

**SSL Labs 测试**：
```
https://www.ssllabs.com/ssltest/
```

**输入域名**，查看评分和详情

---

## ⚠️ **常见问题**

### **问题 1：Certbot 安装失败**

**错误**：
```
No package certbot available.
```

**解决**：
```bash
# 安装 EPEL
sudo yum install epel-release -y

# 或者使用 Snap
sudo yum install snapd -y
sudo systemctl enable --now snapd.socket
sudo snap install --classic certbot
```

---

### **问题 2：Nginx 配置失败**

**错误**：
```
nginx: [emerg] unknown "ssl_certificate" directive
```

**解决**：
```bash
# 检查 Nginx 版本（需要 1.11.0+）
nginx -v

# 更新 Nginx
sudo yum install nginx -y
```

---

### **问题 3：端口冲突**

**错误**：
```
Problem binding to port 80: Could not bind to IPv4 or IPv6.
```

**解决**：
```bash
# 停止 Nginx
sudo systemctl stop nginx

# 使用 standalone 模式
sudo certbot certonly --standalone -d yourdomain.com

# 手动配置 Nginx（见上方）

# 重启 Nginx
sudo systemctl start nginx
```

---

### **问题 4：证书不受信任**

**原因**：使用了自签名证书

**解决**：
```bash
# 删除旧证书
sudo certbot delete --cert-name yourdomain.com

# 重新申请 Let's Encrypt 证书
sudo certbot --nginx -d yourdomain.com
```

---

## 🔒 **安全优化**

### **增强 SSL 配置**

在 Nginx 配置中添加：

```nginx
# HSTS（强制 HTTPS）
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# 防止点击劫持
add_header X-Frame-Options "SAMEORIGIN" always;

# 防止 MIME 嗅探
add_header X-Content-Type-Options "nosniff" always;

# XSS 防护
add_header X-XSS-Protection "1; mode=block" always;
```

---

### **Django 配置**

修改 `settings.py`：

```python
# 强制 HTTPS
SECURE_SSL_REDIRECT = True

# Cookie 安全
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 其他安全配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 📈 **监控与维护**

### **证书到期提醒**

```bash
# 查看证书到期时间
sudo certbot certificates

# 输出示例：
# Certificate Name: yourdomain.com
# Domains: yourdomain.com www.yourdomain.com
# Expiry Date: 2026-06-21
```

---

### **设置邮件提醒**

```bash
# 编辑 Certbot 配置
sudo vi /etc/letsencrypt/cli.ini

# 添加
email = your-email@example.com
```

---

### **日志查看**

```bash
# Certbot 日志
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

---

## 🎉 **完成检查清单**

### **配置完成后检查**

- [ ] ✅ Certbot 已安装
- [ ] ✅ 证书已申请
- [ ] ✅ Nginx 已配置 HTTPS
- [ ] ✅ HTTP 自动跳转 HTTPS
- [ ] ✅ 防火墙开放 80/443
- [ ] ✅ 阿里云安全组配置
- [ ] ✅ HTTPS 访问正常
- [ ] ✅ 浏览器显示安全锁
- [ ] ✅ 自动续期已配置

---

## 📞 **快速命令参考**

```bash
# 查看证书
certbot certificates

# 续期证书
certbot renew

# 删除证书
certbot delete --cert-name yourdomain.com

# 重新申请证书
certbot --nginx -d yourdomain.com

# 测试 Nginx 配置
nginx -t

# 重启 Nginx
systemctl restart nginx

# 查看 Nginx 状态
systemctl status nginx
```

---

## 🎯 **总结**

### **快速操作（CentOS）**

```bash
# 1. 安装 EPEL
sudo yum install epel-release -y

# 2. 安装 Certbot
sudo yum install certbot python3-certbot-nginx -y

# 3. 申请证书
sudo certbot --nginx -d yourdomain.com

# 4. 验证
curl -I https://yourdomain.com
```

---

### **效果**

✅ **生产环境 HTTPS**：
- 🔒 完整的 HTTPS 加密
- ✅ 浏览器信任的证书
- ✅ 消除"不安全"警告
- ✅ 用户完全信任

---

**位置**：`E:\EIMS2026\阿里云服务器 HTTPS 配置完全指南.md`  
**状态**：✅ 配置完成  
**下一步**：在服务器上执行安装命令
