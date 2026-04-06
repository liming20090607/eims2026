# 阿里云免费 SSL 证书部署指南

**目标**：使用阿里云免费 SSL 证书消除浏览器"不安全"警告  
**适用**：已有域名，正在备案中  
**优势**：浏览器完全信任，无警告提示

---

## 🎯 方案概述

### **为什么选择阿里云 SSL 证书？**

| 特性 | Let's Encrypt | 阿里云免费证书 |
|------|--------------|----------------|
| **有效期** | 90 天 | 1 年 |
| **信任度** | ✅ 完全信任 | ✅ 完全信任 |
| **自动续期** | ✅ 自动 | ❌ 手动 |
| **IP 支持** | ❌ 不支持 | ✅ 支持 |
| **申请难度** | ⭐⭐ | ⭐⭐⭐ |
| **适用场景** | 有域名 | 有域名/IP |

---

## 📋 前提条件

### **必须满足**

- ✅ 已注册域名（您的域名）
- ✅ 域名已完成 ICP 备案
- ✅ 阿里云服务器（ECS）
- ✅ SSH 可以登录服务器

---

## 🚀 快速部署流程

### **步骤 1：申请阿里云 SSL 证书**

#### **1.1 登录阿里云控制台**

访问：https://www.aliyun.com

**导航**：
```
产品与服务 → 安全 → SSL 证书
```

---

#### **1.2 选择免费证书**

**操作**：
1. 点击"免费证书"
2. 点击"立即购买"（0 元）
3. 选择证书类型：**DV SSL**
4. 选择品牌：**Digicert** 或 **GeoTrust**

---

#### **1.3 填写申请信息**

**证书信息**：
```
域名类型：单域名
域名：yourdomain.com（您的域名）
```

**联系人信息**：
```
姓名：您的姓名
邮箱：您的邮箱
手机：您的手机
```

**提交审核**：
- ✅ 自动审核（通常 5-10 分钟）
- ✅ 短信验证（按提示操作）

---

#### **1.4 下载证书**

**审核通过后**：
1. 进入"证书控制台"
2. 找到已签发的证书
3. 点击"下载"
4. 选择证书格式：**Nginx**

**下载的文件**：
```
证书文件：
  - yourdomain.com.key（私钥）
  - yourdomain.com.pem（证书）
```

---

### **步骤 2：上传证书到服务器**

#### **方式 1：使用 SCP（推荐）** ⭐⭐⭐⭐⭐

**在本地 PowerShell 执行**：
```powershell
# 创建证书目录
ssh root@39.106.41.239 "mkdir -p /etc/nginx/ssl"

# 上传证书文件
scp yourdomain.com.pem root@39.106.41.239:/etc/nginx/ssl/cert.pem
scp yourdomain.com.key root@39.106.41.239:/etc/nginx/ssl/key.pem
```

---

#### **方式 2：使用 FTP 工具** ⭐⭐⭐⭐

**使用工具**：
- WinSCP
- FileZilla
- Xftp

**操作步骤**：
1. 连接服务器：`39.106.41.239`
2. 用户：`root`
3. 密码：您的密码
4. 上传到：`/etc/nginx/ssl/`

---

#### **方式 3：手动复制** ⭐⭐⭐

**SSH 登录服务器**：
```bash
# 创建目录
mkdir -p /etc/nginx/ssl

# 使用 vim 创建证书文件
cd /etc/nginx/ssl
vi cert.pem
```

**操作**：
1. 在本地打开 `.pem` 文件
2. 复制全部内容
3. 在 vim 中按 `i` 进入插入模式
4. 粘贴内容
5. 按 `ESC`，输入 `:wq` 保存退出

**同样操作上传 `.key` 文件**。

---

### **步骤 3：配置 Nginx**

#### **3.1 编辑 Nginx 配置**

**SSH 登录服务器**：
```bash
# 编辑配置
vi /etc/nginx/nginx.conf

# 或编辑独立配置文件
vi /etc/nginx/conf.d/eims.conf
```

---

#### **3.2 添加 HTTPS 配置**

**完整配置**：

```nginx
# HTTP 服务器 - 强制跳转到 HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 服务器
server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    # SSL 证书路径
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

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

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

---

#### **3.3 测试配置**

```bash
# 测试 Nginx 配置
nginx -t
```

**预期输出**：
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

#### **3.4 重启 Nginx**

```bash
# 重启 Nginx
systemctl restart nginx

# 查看状态
systemctl status nginx
```

---

### **步骤 4：配置 Django 生产环境**

#### **4.1 修改 settings.py**

**添加生产配置**：

```python
# 生产环境配置
DEBUG = False

# 允许的域名
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    '39.106.41.239',
]

# 安全配置
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 静态文件
STATIC_ROOT = '/var/www/eims/static'
MEDIA_ROOT = '/var/www/eims/media'
```

---

#### **4.2 配置环境变量**

**创建 `.env` 文件**：
```bash
# 在项目根目录
vi .env
```

**内容**：
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,39.106.41.239
DATABASE_URL=sqlite:///db.sqlite3
```

---

### **步骤 5：配置防火墙和安全组**

#### **5.1 阿里云安全组**

**操作**：
1. 登录阿里云控制台
2. 云服务器 ECS → 实例
3. 安全组 → 配置规则
4. 添加入站规则：

**规则配置**：
```
端口范围：80/80
授权对象：0.0.0.0/0
协议：TCP
优先级：1

端口范围：443/443
授权对象：0.0.0.0/0
协议：TCP
优先级：1

端口范围：8000/8000
授权对象：127.0.0.1/32
协议：TCP
优先级：1（仅内网访问）
```

---

#### **5.2 服务器防火墙**

```bash
# 检查防火墙状态
systemctl status firewalld

# 如果防火墙开启，添加规则
firewall-cmd --zone=public --add-port=80/tcp --permanent
firewall-cmd --zone=public --add-port=443/tcp --permanent
firewall-cmd --reload

# 或者关闭防火墙（开发环境）
systemctl stop firewalld
systemctl disable firewalld
```

---

### **步骤 6：验证 HTTPS**

#### **6.1 测试 HTTPS 访问**

```bash
# 测试 HTTPS
curl -I https://yourdomain.com
```

**预期输出**：
```
HTTP/2 200 
server: nginx
```

---

#### **6.2 测试 HTTP 跳转**

```bash
# 测试 HTTP 跳转
curl -I http://yourdomain.com
```

**预期输出**：
```
HTTP/1.1 301 Moved Permanently
Location: https://yourdomain.com/
```

---

#### **6.3 浏览器验证**

**访问**：
```
https://yourdomain.com
```

**检查**：
- ✅ 浏览器显示安全锁图标
- ✅ 无"不安全"警告
- ✅ 证书信息正确
- ✅ 网站内容正常

---

## 🎯 完整部署脚本

### **一键部署脚本** `/root/deploy_ssl.sh`

```bash
#!/bin/bash

echo "======================================"
echo "阿里云 SSL 证书一键部署
echo "======================================"
echo ""

# 检查是否 root
if [ "$EUID" -ne 0 ]; then 
  echo "❌ 请使用 root 用户或 sudo 执行"
  exit 1
fi

# 配置变量
DOMAIN="yourdomain.com"  # 修改为您的域名
CERT_PATH="/etc/nginx/ssl"

echo "域名：$DOMAIN"
echo "证书路径：$CERT_PATH"
echo ""

# 确认
read -p "确认证书文件已上传到 $CERT_PATH？(y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "请先上传证书文件：
    echo "  scp cert.pem root@39.106.41.239:$CERT_PATH/cert.pem
    echo "  scp key.pem root@39.106.41.239:$CERT_PATH/key.pem
    exit 1
fi

echo ""
echo "======================================"
echo "配置 Nginx...
echo "======================================"
echo ""

# 创建 Nginx 配置
cat > /etc/nginx/conf.d/https.conf << EOF
# HTTP 强制跳转
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS 服务器
server {
    listen 443 ssl;
    server_name $DOMAIN www.$DOMAIN;

    # SSL 证书
    ssl_certificate $CERT_PATH/cert.pem;
    ssl_certificate_key $CERT_PATH/key.pem;

    # SSL 优化
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Django 代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 静态文件
    location /static/ {
        alias /var/www/eims/static/;
    }

    # 媒体文件
    location /media/ {
        alias /var/www/eims/media/;
    }

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
}
EOF

# 测试配置
echo "测试 Nginx 配置..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx 配置成功"
    
    # 重启 Nginx
    echo "重启 Nginx..."
    systemctl restart nginx
    
    # 验证
    echo ""
    echo "验证 HTTPS 访问..."
    sleep 2
    
    curl -I https://$DOMAIN 2>/dev/null | head -1
    
    echo ""
    echo "======================================"
    echo "✅ HTTPS 部署完成！
    echo "======================================"
    echo ""
    echo "访问地址：https://$DOMAIN"
    echo "证书位置：$CERT_PATH"
    echo ""
else
    echo "❌ Nginx 配置失败"
    exit 1
fi
```

---

### **使用脚本**

```bash
# 1. 创建脚本
vi /root/deploy_ssl.sh

# 2. 粘贴上面的内容，保存退出

# 3. 赋予执行权限
chmod +x /root/deploy_ssl.sh

# 4. 执行
./deploy_ssl.sh
```

---

## 📊 部署效果对比

### **部署前** ❌

```
访问：http://39.106.41.239:8000
浏览器：⚠️ 不安全
用户信任：低
```

---

### **部署后** ✅

```
访问：https://yourdomain.com
浏览器：🔒 安全锁图标
用户信任：高
```

---

## ⚠️ 常见问题

### **问题 1: 证书上传失败**

**解决**：
```bash
# 检查目录权限
ls -ld /etc/nginx/ssl

# 修改权限
chmod 755 /etc/nginx/ssl

# 重新上传
```

---

### **问题 2: Nginx 启动失败**

**排查**：
```bash
# 查看错误日志
tail -f /var/log/nginx/error.log

# 检查配置
nginx -t

# 检查端口占用
netstat -tlnp | grep :443
```

---

### **问题 3: HTTPS 无法访问**

**排查步骤**：
```bash
# 1. 检查 DNS
ping yourdomain.com

# 2. 检查证书
ls -l /etc/nginx/ssl/

# 3. 检查 Nginx
systemctl status nginx

# 4. 检查防火墙
firewall-cmd --list-ports

# 5. 检查安全组（阿里云控制台）
```

---

### **问题 4: 浏览器仍然提示不安全**

**可能原因**：
- ❌ 证书域名不匹配
- ❌ 证书已过期
- ❌ 混合内容（HTTP 资源）

**解决**：
```bash
# 1. 检查证书
openssl x509 -in /etc/nginx/ssl/cert.pem -text -noout

# 2. 检查有效期
openssl x509 -in /etc/nginx/ssl/cert.pem -dates

# 3. 查看浏览器控制台
F12 → Console → 查看错误
```

---

## 🔧 证书管理

### **查看证书信息**

```bash
# 查看证书详情
openssl x509 -in /etc/nginx/ssl/cert.pem -text -noout

# 查看有效期
openssl x509 -in /etc/nginx/ssl/cert.pem -dates -noout
```

---

### **证书续期**

**阿里云免费证书**：
- ⏰ 有效期：1 年
- 📅 到期前 30 天可申请续期
- ✅ 续期流程与申请相同

**续期步骤**：
1. 登录阿里云控制台
2. SSL 证书 → 我的证书
3. 找到到期证书
4. 点击"续费"
5. 重新下载证书
6. 上传到服务器
7. 重启 Nginx

---

### **证书备份**

```bash
# 备份证书
mkdir -p /root/ssl_backup
cp /etc/nginx/ssl/*.pem /root/ssl_backup/
cp /etc/nginx/ssl/*.key /root/ssl_backup/

# 下载备份到本地
scp root@39.106.41.239:/root/ssl_backup/* ./ssl_backup/
```

---

## 📈 性能优化

### **Nginx SSL 优化**

```nginx
# 开启 OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# 会话票证
ssl_session_tickets off;

# 更安全的加密套件
ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';
```

---

### **Django 安全配置**

```python
# settings.py
DEBUG = False

# 强制 HTTPS
SECURE_SSL_REDIRECT = True

# Cookie 安全
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 其他安全头
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 🎉 完成检查清单

### **部署验证**

- [ ] ✅ 证书已上传
- [ ] ✅ Nginx 已配置
- [ ] ✅ HTTPS 访问正常
- [ ] ✅ HTTP 自动跳转
- [ ] ✅ 浏览器显示安全锁
- [ ] ✅ 无"不安全"警告
- [ ] ✅ 证书信息正确
- [ ] ✅ 网站功能正常

---

### **文档整理**

- [ ] ✅ 部署文档已归档
- [ ] ✅ 证书信息已记录
- [ ] ✅ 续期时间已标记
- [ ] ✅ 运维手册已编写

---

## 📞 快速命令参考

```bash
# 上传证书
scp cert.pem root@39.106.41.239:/etc/nginx/ssl/
scp key.pem root@39.106.41.239:/etc/nginx/ssl/

# 配置 Nginx
vi /etc/nginx/conf.d/https.conf

# 测试配置
nginx -t

# 重启 Nginx
systemctl restart nginx

# 验证 HTTPS
curl -I https://yourdomain.com

# 查看证书
openssl x509 -in /etc/nginx/ssl/cert.pem -text -noout
```

---

## 🎯 总结

### **部署流程**

1. ✅ 申请阿里云免费 SSL 证书
2. ✅ 下载证书（Nginx 格式）
3. ✅ 上传到服务器
4. ✅ 配置 Nginx
5. ✅ 重启服务
6. ✅ 验证 HTTPS

**时间**：约 30 分钟

---

### **效果**

✅ **消除"不安全"警告**  
✅ **浏览器显示安全锁**  
✅ **用户完全信任**  
✅ **SEO 优化提升**  

---

**位置**：`E:\EIMS2026\阿里云 SSL 证书部署指南.md`  
**状态**：✅ 配置完成  
**下一步**：申请证书 → 上传 → 配置 → 验证！

---

**使用阿里云免费 SSL 证书，彻底消除浏览器警告！** 🚀🔒
