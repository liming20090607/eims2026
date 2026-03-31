# EIMS 项目快速部署指南（10 分钟版）

## 🚀 最简部署方案（适合小型项目/测试环境）

### 方案 A：使用 PaaS 平台（最简单，5 分钟上线）

#### 1. 选择平台（推荐 Railway 或 Render）

**Railway.app**（推荐）：
- ✅ 免费额度 $5/月
- ✅ 自动 SSL
- ✅ 一键部署
- ✅ 支持 PostgreSQL

**Render.com**：
- ✅ 免费套餐
- ✅ 自动 HTTPS
- ✅ 内置数据库

#### 2. 部署步骤（以 Railway 为例）

```bash
# 1. 准备代码
cd e:\EIMS2026

# 2. 创建 railway.json 配置文件
```

创建 `railway.json`：
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn wsgi:application --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

创建 `Procfile`：
```
web: gunicorn wsgi:application --bind 0.0.0.0:$PORT
```

#### 3. 上传到 GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo>
git push -u origin main
```

#### 4. 在 Railway 部署
1. 访问 https://railway.app
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择你的仓库
5. 添加 PostgreSQL 数据库插件
6. 设置环境变量：
   ```
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=<生成新的密钥>
   ALLOWED_HOSTS=*
   ```
7. 点击 Deploy

---

### 方案 B：VPS 快速部署（适合生产环境）

#### 准备工作
- Ubuntu 22.04 服务器
- 域名解析到服务器 IP
- SSH 访问权限

#### 快速部署脚本

```bash
# 1. SSH 登录服务器
ssh root@your-server-ip

# 2. 安装必要软件
apt update && apt install -y python3-pip python3-venv nginx git

# 3. 创建项目目录
mkdir -p /var/www/eims
cd /var/www/eims

# 4. 上传代码（方式 1：Git）
git clone <your-repo-url> .

# 上传代码（方式 2：SCP）
# 本地执行：scp -r e:\EIMS2026\* root@your-ip:/var/www/eims/

# 5. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 6. 安装依赖
pip install --upgrade pip
pip install gunicorn django python-dotenv django-widget-tweaks

# 7. 配置环境变量
cat > .env << EOF
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ALLOWED_HOSTS=your-domain.com,your-server-ip
EOF

# 8. 数据库迁移（使用 SQLite 快速启动）
python3 manage.py migrate

# 9. 收集静态文件
python3 manage.py collectstatic --noinput

# 10. 创建超级用户
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python3 manage.py shell

# 11. 配置 Gunicorn
cat > /etc/systemd/system/eims.service << EOF
[Unit]
Description=EIMS Gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/eims
ExecStart=/var/www/eims/venv/bin/gunicorn \
    --access-logfile - \
    --workers 2 \
    --bind 0.0.0.0:8000 \
    wsgi:application

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start eims
systemctl enable eims

# 12. 配置 Nginx
cat > /etc/nginx/sites-available/eims << EOF
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
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/eims /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# 13. 配置防火墙
ufw allow 'Nginx Full'
ufw allow OpenSSH
echo "y" | ufw enable

# 14. 配置 SSL（可选但推荐）
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com --non-interactive --agree-tos --email your-email@example.com

echo "✅ 部署完成！"
echo "访问：http://your-domain.com"
echo "管理员账号：admin / admin123"
echo "请立即修改密码！"
```

---

## ⚡ 超快速部署（开发测试用，不推荐生产）

### 直接使用 runserver（仅限本地测试）

```bash
# 1. 修改 settings.py
# ALLOWED_HOSTS = ['*']

# 2. 启动服务器
python manage.py runserver 0.0.0.0:8000

# 3. 在浏览器访问
# http://your-server-ip:8000
```

⚠️ **警告**：此方法仅用于开发测试，不要用于生产环境！

---

## 🎯 推荐方案对比

| 方案 | 难度 | 成本 | 适用场景 | 部署时间 |
|------|------|------|----------|----------|
| Railway/Render | ⭐ | ¥30-50/月 | 小型项目/初创 | 5 分钟 |
| VPS + 脚本 | ⭐⭐⭐ | ¥50-200/月 | 生产环境 | 10-30 分钟 |
| VPS + 手动 | ⭐⭐⭐⭐ | ¥50-200/月 | 大型项目 | 1-2 小时 |
| 容器化部署 | ⭐⭐⭐⭐⭐ | ¥100-500/月 | 微服务架构 | 2-4 小时 |

---

## 📝 部署后必做检查

### 1. 基本功能测试
```bash
# 测试首页
curl http://your-domain.com/

# 测试登录页
curl http://your-domain.com/login/

# 测试静态文件
curl http://your-domain.com/static/css/style.css
```

### 2. 安全检查清单
- [ ] DEBUG 已关闭
- [ ] SECRET_KEY 已更换
- [ ] ALLOWED_HOSTS 已配置
- [ ] HTTPS 已启用
- [ ] 管理员密码已修改

### 3. 性能检查
- [ ] 页面加载时间 < 3 秒
- [ ] 静态文件使用 CDN（可选）
- [ ] 数据库查询优化

---

## 🔧 常用命令速查

```bash
# 查看服务状态
systemctl status nginx
systemctl status eims

# 重启服务
systemctl restart nginx
systemctl restart eims

# 查看日志
tail -f /var/log/nginx/error.log
journalctl -u eims -f

# 进入虚拟环境
cd /var/www/eims
source venv/bin/activate

# 更新代码
git pull
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart eims

# 备份数据库
python manage.py dumpdata > backup_$(date +%Y%m%d).json
```

---

## 🆘 紧急故障处理

### 网站无法访问
```bash
# 1. 检查服务状态
systemctl status nginx
systemctl status eims

# 2. 查看错误日志
tail -f /var/log/nginx/error.log

# 3. 重启服务
systemctl restart nginx
systemctl restart eims
```

### 数据库问题
```bash
# 检查数据库连接
python manage.py dbshell

# 如果是 SQLite，检查文件权限
ls -l db.sqlite3
chmod 644 db.sqlite3
```

---

## 💡 省钱技巧

1. **选择便宜的 VPS**
   - 腾讯云轻量应用服务器：¥24/月起
   - 阿里云 ECS：¥36/月起
   - DigitalOcean：$5/月

2. **使用免费服务**
   - Cloudflare CDN（免费）
   - Let's Encrypt SSL 证书（免费）
   - GitHub Pages（静态资源）

3. **优化资源配置**
   - 初期 1 核 1G 足够
   - 使用 SQLite 减少数据库成本
   - 合并静态文件减少 CDN 费用

---

## 📞 获取帮助

- 官方文档：https://docs.djangoproject.com/
- Django 中文社区：https://www.django.cn/
- Stack Overflow：https://stackoverflow.com/questions/tagged/django
