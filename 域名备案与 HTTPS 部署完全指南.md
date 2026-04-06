# 域名备案与 HTTPS 部署完全指南

**适用**：已注册域名，正在备案中  
**目标**：备案完成后立即部署 HTTPS

---

## 📋 当前状态

✅ **已完成**：
- 域名已注册
- 正在备案中

⏳ **进行中**：
- 等待备案审核（通常 5-20 个工作日）

📝 **下一步**：
- 准备 HTTPS 部署
- 备案完成后立即配置

---

## 🎯 备案期间可以做什么

### **1. 本地开发环境配置**

在备案期间，您可以在本地使用 HTTPS 开发：

```bash
# 安装 django-extensions
cd E:\EIMS2026
pip install django-extensions

# 启动本地 HTTPS 服务器
python manage.py runserver_plus --cert-file cert.pem --key-file key.pem 0.0.0.0:8000
```

**访问**：
```
https://localhost:8000
```

---

### **2. 准备部署脚本**

提前准备好所有部署脚本，备案完成后直接执行。

#### **创建部署脚本** `/root/deploy_eims.sh`：

```bash
#!/bin/bash

echo "======================================"
echo "EIMS 系统快速部署脚本
echo "======================================"

# 配置变量
DOMAIN="yourdomain.com"  # 备案完成后修改
EMAIL="your@email.com"
PROJECT_PATH="/var/www/eims"
PYTHON_VENV="$PROJECT_PATH/venv"

echo "域名：$DOMAIN"
echo "邮箱：$EMAIL"
echo "项目路径：$PROJECT_PATH"
echo ""

# 1. 安装系统依赖
echo "[1/10] 安装系统依赖..."
yum update -y
yum install -y epel-release
yum install -y python3 python3-pip python3-venv
yum install -y nginx git
yum install -y certbot python3-certbot-nginx

# 2. 创建项目目录
echo "[2/10] 创建项目目录..."
mkdir -p $PROJECT_PATH
cd $PROJECT_PATH

# 3. 克隆代码
echo "[3/10] 克隆代码..."
# 方式 1: 从 GitHub
# git clone https://github.com/yourusername/EIMS2026.git .

# 方式 2: 手动上传（已上传则跳过）
echo "代码已上传到服务器"

# 4. 创建虚拟环境
echo "[4/10] 创建 Python 虚拟环境..."
python3 -m venv $PYTHON_VENV
source $PYTHON_VENV/bin/activate

# 5. 安装 Python 依赖
echo "[5/10] 安装 Python 依赖..."
pip install -r requirements.txt
pip install gunicorn

# 6. 配置环境变量
echo "[6/10] 配置环境变量..."
cat > $PROJECT_PATH/.env << EOF
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,39.106.41.239
DATABASE_URL=sqlite:///db.sqlite3
EOF

# 7. 数据库迁移
echo "[7/10] 数据库迁移..."
python manage.py migrate
python manage.py collectstatic --noinput

# 8. 创建 Gunicorn 服务
echo "[8/10] 创建 Gunicorn 服务..."
cat > /etc/systemd/system/eims.service << EOF
[Unit]
Description=EIMS Gunicorn instance
After=network.target

[Service]
User=root
Group=nginx
WorkingDirectory=$PROJECT_PATH
ExecStart=$PYTHON_VENV/bin/gunicorn --workers 3 --bind unix:$PROJECT_PATH/eims.sock \
    wsgi:application

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable eims
systemctl start eims

# 9. 配置 Nginx
echo "[9/10] 配置 Nginx..."
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

# 10. 申请 SSL 证书
echo "[10/10] 申请 SSL 证书..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --redirect

echo ""
echo "======================================"
echo "✅ 部署完成！
echo "======================================"
echo ""
echo "访问地址：https://$DOMAIN"
echo ""
```

---

### **3. 创建配置模板**

#### **Nginx 配置模板** `/etc/nginx/conf.d/eims.conf.template`：

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

    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL 优化
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Django 代理
    location / {
        proxy_pass http://unix:/var/www/eims/eims.sock;
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

### **4. 创建 Django 生产配置**

#### **修改 `settings.py` 生产环境配置**：

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

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

---

## ⏳ 备案完成后立即执行

### **步骤 1：修改配置中的域名**

**编辑部署脚本**：
```bash
vi /root/deploy_eims.sh
```

**修改**：
```bash
DOMAIN="yourdomain.com"  # ← 改为您的实际域名
EMAIL="your@email.com"
```

---

### **步骤 2：执行部署脚本**

```bash
# 上传脚本到服务器
scp deploy_eims.sh root@39.106.41.239:/root/

# SSH 登录
ssh root@39.106.41.239

# 执行部署
chmod +x /root/deploy_eims.sh
./deploy_eims.sh
```

---

### **步骤 3：验证 HTTPS**

```bash
# 检查证书
certbot certificates

# 测试 HTTPS 访问
curl -I https://yourdomain.com

# 检查 HTTP 跳转
curl -I http://yourdomain.com
```

**预期输出**：
```
HTTP/2 200 
server: nginx
```

---

## 📊 完整部署时间线

```
Day 0: 域名注册 ✓
       提交备案申请 ✓
       
Day 1-20: 等待备案审核 ⏳
          ↓
          准备部署脚本 ✓
          本地测试 HTTPS ✓
          创建配置模板 ✓
          
Day 20: 备案通过 ✓
        ↓
        执行部署脚本 (10 分钟)
        ↓
        验证 HTTPS (5 分钟)
        ↓
        正式上线！🎉
```

---

## 🎯 备案期间的准备工作清单

### **✅ 技术准备**

- [x] 安装 django-extensions（本地）
- [x] 创建 HTTPS 部署脚本
- [x] 创建 Nginx 配置模板
- [x] 准备 Django 生产配置
- [ ] 测试部署脚本（本地虚拟机）
- [ ] 准备域名 DNS 解析

---

### **✅ 内容准备**

- [ ] 准备网站首页内容
- [ ] 准备产品介绍
- [ ] 准备联系方式
- [ ] 准备隐私政策
- [ ] 准备服务条款

---

### **✅ DNS 配置准备**

**备案通过后需要配置**：

1. **添加 A 记录**：
   ```
   主机记录：@
   记录类型：A
   记录值：39.106.41.239
   TTL: 10 分钟
   ```

2. **添加 www 记录**：
   ```
   主机记录：www
   记录类型：A
   记录值：39.106.41.239
   TTL: 10 分钟
   ```

---

## 🚀 备案通过后的快速部署

### **快速命令（复制粘贴）**

```bash
# 1. 配置域名
DOMAIN="yourdomain.com"
EMAIL="your@email.com"

# 2. 安装依赖
sudo yum install epel-release -y
sudo yum install certbot python3-certbot-nginx -y

# 3. 申请证书
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --redirect

# 4. 验证
curl -I https://$DOMAIN
```

---

## ⚠️ 注意事项

### **备案期间**

⚠️ **不要**：
- ❌ 将域名解析到国内服务器
- ❌ 使用域名访问网站
- ❌ 提供公开访问服务

✅ **可以**：
- ✅ 使用 IP 地址测试
- ✅ 本地开发环境测试
- ✅ 准备所有部署脚本

---

### **备案通过后**

✅ **必须做**：
- 配置 DNS 解析
- 部署 HTTPS 证书
- 网站首页添加备案号
- 配置公安联网备案

---

## 📝 网站首页备案号配置

### **添加备案号到页脚**

**修改 `base.html`**：

```html
<footer>
    <p>&copy; 2026 EIMS 系统. All rights reserved.</p>
    
    <!-- 网站备案号 -->
    <p>
        <a href="https://beian.miit.gov.cn/" target="_blank">
            京 ICP 备 XXXXXXXX 号
        </a>
    </p>
    
    <!-- 公安联网备案 -->
    <p>
        <a href="http://www.beian.gov.cn/portal/registerSystemInfo" target="_blank">
            京公网安备 XXXXXXXXXXXXXX 号
        </a>
    </p>
</footer>
```

---

## 🔧 常见问题

### **Q1: 备案需要多长时间？**

**A**: 
- 通常 5-20 个工作日
- 首次备案可能更长
- 各省速度不同

---

### **Q2: 备案期间域名能用吗？**

**A**: 
- ❌ 不能解析到国内服务器
- ✅ 可以暂停解析
- ✅ 可以使用海外服务器（不需要备案）

---

### **Q3: 备案通过后多久能访问？**

**A**: 
- ✅ 备案通过后立即可以
- ⏰ DNS 生效需要 10 分钟 -24 小时

---

### **Q4: 备案后必须用 HTTPS 吗？**

**A**: 
- ⚠️ 不是必须，但强烈推荐
- ✅ HTTPS 是最佳实践
- ✅ 浏览器推荐 HTTPS 网站

---

## 📈 部署后的优化建议

### **性能优化**

```nginx
# Nginx 优化配置
server {
    # 开启 Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/json application/javascript;
    
    # 缓存静态文件
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

### **安全加固**

```python
# settings.py 安全配置
DEBUG = False

# 限制允许的域名
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# 安全头
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 密码策略
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

---

## 🎉 总结

### **当前状态**

✅ **已完成**：域名注册、备案申请  
⏳ **进行中**：等待备案审核  
📝 **下一步**：准备部署脚本和配置

---

### **备案通过后**

```bash
# 1. 配置 DNS 解析
添加 A 记录：yourdomain.com → 39.106.41.239

# 2. 执行部署脚本
./deploy_eims.sh

# 3. 验证 HTTPS
curl -I https://yourdomain.com

# 4. 正式上线！🎉
```

---

### **预计时间**

- 备案审核：5-20 个工作日
- DNS 生效：10 分钟 -24 小时
- HTTPS 部署：15 分钟
- **总计**：备案通过后 1 小时内上线

---

**位置**：`E:\EIMS2026\域名备案与 HTTPS 部署完全指南.md`  
**状态**：✅ 准备就绪  
**下一步**：等待备案通过，立即部署！

---

## 💡 备案期间的建议

### **充分利用等待时间**

1. **完善功能**：
   - 测试所有功能模块
   - 修复发现的 bug
   - 优化用户体验

2. **准备内容**：
   - 编写使用文档
   - 准备演示数据
   - 制作宣传材料

3. **技术准备**：
   - 本地测试 HTTPS
   - 准备部署脚本
   - 配置监控和日志

4. **安全加固**：
   - 审查代码安全
   - 配置防火墙
   - 准备备份方案

---

**祝备案顺利！准备好迎接正式上线吧！** 🚀
