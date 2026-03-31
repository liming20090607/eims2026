# 🚀 阿里云服务器部署完整指南

## 📋 环境状态确认

✅ **已完成**:
1. ✅ 系统更新
2. ✅ MySQL 数据库安装
3. ✅ Python 环境安装
4. ✅ 数据库驱动安装

---

## 🎯 部署步骤总览

| 步骤 | 任务 | 预计时间 |
|------|------|---------|
| **Step 1** | 配置 MySQL 数据库 | 5 分钟 |
| **Step 2** | 上传项目代码 | 5 分钟 |
| **Step 3** | 安装 Python 依赖 | 5 分钟 |
| **Step 4** | 配置 Django 生产环境 | 10 分钟 |
| **Step 5** | 配置 Nginx + Gunicorn | 15 分钟 |
| **Step 6** | 配置 HTTPS（可选） | 10 分钟 |
| **Step 7** | 测试验证 | 5 分钟 |

---

## Step 1: 配置 MySQL 数据库 🔧

### 1.1 登录 MySQL

```bash
mysql -u root -p
# 输入您在安装时设置的 root 密码
```

### 1.2 创建数据库和用户

```sql
-- 创建 EIMS 数据库
CREATE DATABASE eims_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建专用用户（替换 your_password 为强密码）
CREATE USER 'eims_user'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';

-- 授权
GRANT ALL PRIVILEGES ON eims_db.* TO 'eims_user'@'localhost';
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

### 1.3 测试数据库连接

```bash
mysql -u eims_user -p
# 输入刚才设置的密码
```

---

## Step 2: 上传项目代码 📦

### 方法 1: 使用 Git（推荐）

**本地执行**:
```bash
# 在您的本地项目目录初始化 git
cd E:\EIMS2026
git init
git add .
git commit -m "Initial commit for production"

# 创建 GitHub/Gitee 仓库并推送
git remote add origin https://github.com/yourusername/eims.git
git push -u origin main
```

**服务器执行**:
```bash
# 克隆项目
cd /home
git clone https://github.com/yourusername/eims.git
cd eims
```

---

### 方法 2: 使用 SCP 传输

**本地 PowerShell 执行**:
```powershell
# 压缩项目目录
Compress-Archive -Path E:\EIMS2026\* -DestinationPath E:\EIMS2026.zip

# 上传到服务器（替换为您的服务器 IP）
scp E:\EIMS2026.zip root@your_server_ip:/tmp/
```

**服务器执行**:
```bash
cd /home
unzip /tmp/EIMS2026.zip
mv EIMS2026 eims
cd eims
```

---

### 方法 3: 使用 FTP/SFTP 工具

推荐使用 **FileZilla** 或 **WinSCP**:
- 主机：您的服务器 IP
- 用户名：root
- 密码：服务器 root 密码
- 端口：22

上传到：`/home/eims/`

---

## Step 3: 安装 Python 依赖 📥

### 3.1 创建虚拟环境

```bash
cd /home/eims

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 3.2 升级 pip

```bash
pip install --upgrade pip
```

### 3.3 安装依赖

```bash
pip install -r requirements.txt
```

### 3.4 安装额外依赖（如果需要）

```bash
# Django Widget Tweaks（表单增强）
pip install django-widget-tweaks

# Gunicorn（生产环境 WSGI 服务器）
pip install gunicorn

# MySQL 驱动（如果未安装）
pip install pymysql
```

---

## Step 4: 配置 Django 生产环境 ⚙️

### 4.1 创建 .env 生产环境文件

```bash
cd /home/eims
cat > .env << EOF
# Django 生产环境配置
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-super-secret-key-change-this-now-2026
DJANGO_ALLOWED_HOSTS=your_server_ip,localhost,127.0.0.1

# 数据库配置
DB_NAME=eims_db
DB_USER=eims_user
DB_PASSWORD=YourStrongPassword123!
DB_HOST=localhost
DB_PORT=3306

# 媒体文件配置
MEDIA_URL=/media/
MEDIA_ROOT=/home/eims/media

# 静态文件配置
STATIC_URL=/static/
STATIC_ROOT=/home/eims/staticfiles
EOF
```

### 4.2 修改 settings.py

编辑 `settings.py`，更新以下配置：

```python
# 安全配置
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'eims_db'),
        'USER': os.getenv('DB_USER', 'eims_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# 静态文件配置（生产环境）
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 安全设置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 4.3 数据库迁移

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 应用迁移
python manage.py makemigrations
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 创建超级管理员
python manage.py createsuperuser
# 按提示输入用户名、邮箱、密码
```

### 4.4 测试运行

```bash
# 快速测试（仅用于验证配置）
python manage.py runserver 0.0.0.0:8000
```

访问：`http://your_server_ip:8000/`

如果正常显示，按 `Ctrl+C` 停止，继续下一步。

---

## Step 5: 配置 Nginx + Gunicorn 🌐

### 5.1 安装 Gunicorn

```bash
source venv/bin/activate
pip install gunicorn
```

### 5.2 创建 Gunicorn 服务文件

```bash
cat > /etc/systemd/system/eims.service << EOF
[Unit]
Description=EIMS Django Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/home/eims
ExecStart=/home/eims/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/home/eims/eims.sock \
    wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### 5.3 启动 Gunicorn 服务

```bash
systemctl daemon-reload
systemctl start eims
systemctl enable eims
systemctl status eims
```

应该看到 `active (running)` 状态。

---

### 5.4 安装 Nginx

```bash
apt update
apt install nginx -y
```

### 5.5 配置 Nginx

```bash
cat > /etc/nginx/sites-available/eims << EOF
server {
    listen 80;
    server_name your_server_ip;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/eims/staticfiles/;
    }
    
    location /media/ {
        alias /home/eims/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/eims/eims.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
```

### 5.6 启用 Nginx 配置

```bash
ln -s /etc/nginx/sites-available/eims /etc/nginx/sites-enabled
nginx -t
systemctl restart nginx
systemctl enable nginx
```

### 5.7 开放防火墙（阿里云安全组）

**登录阿里云控制台**:
1. 进入 **云服务器 ECS**
2. 选择您的实例
3. 点击 **安全组**
4. 配置规则：
   - 入方向：允许 80 端口（HTTP）
   - 入方向：允许 443 端口（HTTPS，如果配置）
   - 入方向：允许 22 端口（SSH，已开放）

---

## Step 6: 配置 HTTPS（强烈推荐）🔒

### 6.1 安装 Certbot

```bash
apt install certbot python3-certbot-nginx -y
```

### 6.2 获取 SSL 证书

```bash
certbot --nginx -d your_domain.com
# 如果有域名

# 或使用临时域名（阿里云提供）
certbot --nginx
```

### 6.3 自动续期

Certbot 会自动配置续期。测试续期：

```bash
certbot renew --dry-run
```

---

## Step 7: 测试验证 ✅

### 7.1 访问系统

浏览器访问：`http://your_server_ip/`

### 7.2 测试功能

- [ ] 首页加载正常
- [ ] 登录功能
- [ ] 合同台账列表
- [ ] 项目台账列表
- [ ] 文件上传
- [ ] 多用户同时访问

### 7.3 手机访问测试

在手机浏览器输入：`http://your_server_ip/`

检查：
- [ ] 页面响应式布局正常
- [ ] 菜单可折叠展开
- [ ] 表格可横向滚动
- [ ] 按钮易于点击

---

## 🔧 常见问题排查

### 问题 1: 无法访问网站

**检查**:
```bash
# 查看 Nginx 状态
systemctl status nginx

# 查看 Gunicorn 状态
systemctl status eims

# 查看日志
tail -f /var/log/nginx/error.log
tail -f /home/eims/venv/bin/gunicorn-error.log
```

**解决**:
```bash
# 重启服务
systemctl restart nginx
systemctl restart eims
```

---

### 问题 2: 静态文件 404

**检查**:
```bash
ls -la /home/eims/staticfiles/
```

**解决**:
```bash
python manage.py collectstatic --noinput
systemctl restart eims
```

---

### 问题 3: 数据库连接失败

**检查**:
```bash
# 测试数据库连接
mysql -u eims_user -p
```

**解决**:
```bash
# 检查 .env 文件配置
cat .env

# 确保 MySQL 服务运行
systemctl status mysql
```

---

### 问题 4: 权限错误

**解决**:
```bash
# 设置正确的权限
chown -R root:root /home/eims
chmod -R 755 /home/eims
chmod 644 /home/eims/.env
```

---

## 📱 移动端优化建议

### 已自动适配的功能:
1. ✅ 响应式布局
2. ✅ 侧边栏可折叠
3. ✅ 表格横向滚动
4. ✅ 触摸友好的按钮尺寸

### 进一步优化（可选）:
```html
<!-- 在 base.html 的 <head> 中添加 -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

---

## 🔐 安全加固建议

### 1. 修改默认密钥

```bash
# 生成新的 SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

更新 `.env` 文件中的 `DJANGO_SECRET_KEY`。

### 2. 限制 ALLOWED_HOSTS

```env
DJANGO_ALLOWED_HOSTS=your_server_ip,www.yourdomain.com
```

### 3. 配置防火墙

```bash
# 安装 UFW
apt install ufw

# 配置规则
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 4. 定期备份数据库

```bash
# 创建备份脚本
cat > /home/backup_eims.sh << EOF
#!/bin/bash
mysqldump -u eims_user -p'YourStrongPassword123!' eims_db > /home/backups/eims_$(date +%Y%m%d).sql
EOF

chmod +x /home/backup_eims.sh

# 添加到 crontab（每天凌晨 2 点备份）
crontab -e
# 添加：0 2 * * * /home/backup_eims.sh
```

---

## 📊 性能优化建议

### 1. 启用缓存

```bash
# 安装 Redis
apt install redis-server

# 安装 Django Redis
pip install django-redis
```

修改 `settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 2. 数据库优化

```sql
-- 为常用查询字段添加索引
ALTER TABLE eims_app_contract ADD INDEX idx_project_code (project_code);
ALTER TABLE eims_app_contract ADD INDEX idx_status (status);
```

### 3. 启用 Gzip 压缩

在 Nginx 配置中添加:
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;
```

---

## 📝 维护手册

### 日常维护清单

**每周**:
- [ ] 检查磁盘空间：`df -h`
- [ ] 检查日志大小：`du -sh /var/log/*`
- [ ] 查看错误日志：`tail -100 /var/log/nginx/error.log`

**每月**:
- [ ] 更新系统：`apt update && apt upgrade -y`
- [ ] 备份数据库
- [ ] 清理过期会话：`python manage.py clearsessions`

**每季度**:
- [ ] 审查用户权限
- [ ] 检查安全更新
- [ ] 性能监控分析

---

## 🆘 紧急故障恢复

### 数据库崩溃

```bash
# 1. 停止服务
systemctl stop eims
systemctl stop nginx

# 2. 恢复数据库
mysql -u eims_user -p eims_db < /home/backups/eims_YYYYMMDD.sql

# 3. 重启服务
systemctl start eims
systemctl start nginx
```

### 代码问题回滚

```bash
cd /home/eims

# 如果使用 Git
git log  # 查看历史
git reset --hard <commit_hash>

# 重新部署
systemctl restart eims
```

---

## ✅ 部署完成检查清单

- [ ] 数据库创建成功
- [ ] 项目代码上传完成
- [ ] Python 依赖安装完成
- [ ] 数据库迁移完成
- [ ] 静态文件收集完成
- [ ] Gunicorn 服务运行正常
- [ ] Nginx 配置完成
- [ ] 可以通过 IP 访问
- [ ] 登录功能正常
- [ ] 主要功能测试通过
- [ ] 手机访问测试通过
- [ ] HTTPS 配置完成（可选）
- [ ] 备份策略配置完成

---

## 📞 获取帮助

如果遇到问题：
1. 查看日志：`tail -f /var/log/nginx/error.log`
2. 查看 Gunicorn 日志：`journalctl -u eims -f`
3. 检查 Django 配置：`python manage.py check --deploy`

---

**祝您部署成功！** 🎉

更新时间：2026-03-25  
适用版本：EIMS v1.0  
目标平台：阿里云 Ubuntu/CentOS
