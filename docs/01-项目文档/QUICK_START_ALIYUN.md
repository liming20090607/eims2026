# 🚀 阿里云 EIMS 系统快速部署指南

## ⚡ 5 分钟快速部署（适合有经验用户）

### 前置条件
✅ 阿里云服务器（Ubuntu/CentOS）  
✅ MySQL 已安装并运行  
✅ Python 3.8+ 已安装  
✅ 项目代码已上传到服务器  

---

## 📋 快速部署步骤

### 1️⃣ 数据库配置（2 分钟）

```bash
# 登录 MySQL
mysql -u root -p

# 执行 SQL（替换 your_password 为强密码）
CREATE DATABASE eims_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'eims_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON eims_db.* TO 'eims_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

### 2️⃣ 项目配置（1 分钟）

```bash
cd /home/eims

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn django-widget-tweaks
```

---

### 3️⃣ 环境变量（1 分钟）

```bash
# 创建 .env 文件
cat > .env << EOF
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DJANGO_ALLOWED_HOSTS=$(hostname -I | awk '{print $1}')

DB_NAME=eims_db
DB_USER=eims_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
EOF
```

---

### 4️⃣ 数据库迁移（1 分钟）

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

---

### 5️⃣ 启动服务（使用一键脚本）

```bash
# 赋予执行权限
chmod +x deploy.sh

# 执行部署脚本（自动配置 Gunicorn + Nginx）
bash deploy.sh
```

---

## ✅ 验证访问

**浏览器访问**: `http://你的服务器 IP/`

**Admin 后台**: `http://你的服务器 IP/admin/`

---

## 🔧 常用命令

### 服务管理
```bash
# 查看状态
systemctl status eims
systemctl status nginx

# 重启服务
systemctl restart eims
systemctl restart nginx

# 查看日志
journalctl -u eims -f
tail -f /var/log/nginx/error.log
```

---

### 数据库备份
```bash
# 手动备份
bash backup_db.sh

# 定时备份（每天凌晨 2 点）
crontab -e
# 添加：0 2 * * * /home/eims/backup_db.sh
```

---

### 更新代码
```bash
cd /home/eims
source venv/bin/activate

# 如果使用 Git
git pull origin main

# 迁移数据库
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 重启服务
systemctl restart eims
```

---

## 🆘 故障排查

### 无法访问？
```bash
# 1. 检查服务状态
systemctl status eims
systemctl status nginx

# 2. 查看错误日志
tail -f /var/log/nginx/error.log

# 3. 重启所有服务
systemctl restart eims
systemctl restart nginx
```

---

### 502 Bad Gateway？
```bash
# Gunicorn 未运行
systemctl start eims

# 或 socket 文件问题
ls -la /home/eims/eims.sock
```

---

### 静态文件 404？
```bash
python manage.py collectstatic --noinput
systemctl restart eims
```

---

## 📱 移动端访问

**手机浏览器输入**: `http://你的服务器 IP/`

系统已自动适配移动端：
- ✅ 响应式布局
- ✅ 触摸友好按钮
- ✅ 可折叠侧边栏
- ✅ 横向滚动表格

---

## 🔐 安全提醒

### 必须完成的安全配置

1. **修改密钥**
   ```bash
   # 生成新密钥并更新 .env
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **阿里云安全组**
   - 开放 80 端口（HTTP）
   - 开放 443 端口（HTTPS，如配置）
   - 限制 22 端口访问IP

3. **数据库密码**
   - 使用强密码（大小写 + 数字 + 特殊字符）
   - 定期更换

---

## 📊 性能监控

```bash
# 系统资源
top          # CPU 和内存
df -h        # 磁盘空间
free -h      # 内存使用

# 应用状态
systemctl status eims
systemctl status nginx

# 日志分析
tail -100 /var/log/nginx/access.log
```

---

## 📖 详细文档

- 📘 [完整部署指南](file://ALIYUN_DEPLOYMENT_GUIDE.md) - 687 行详细说明
- ✅ [部署检查清单](file://DEPLOYMENT_CHECKLIST.md) - 逐项检查
- 🔧 [生产环境配置](file://settings_production.py) - 优化后的 settings

---

## 🎯 下一步建议

部署成功后：

1. **配置 HTTPS**（强烈推荐）
   ```bash
   apt install certbot python3-certbot-nginx
   certbot --nginx
   ```

2. **设置自动备份**
   ```bash
   chmod +x backup_db.sh
   crontab -e
   # 0 2 * * * /home/eims/backup_db.sh
   ```

3. **性能优化**
   - 启用 Redis 缓存
   - 配置 CDN（如有需要）
   - 数据库索引优化

4. **监控告警**
   - 配置日志轮转
   - 设置监控告警（阿里云监控）
   - 定期安全检查

---

## 💡 技术支持

**遇到问题？**

1. 查看详细部署指南
2. 使用检查清单逐项核对
3. 查看日志定位问题
4. 联系技术支持

---

**祝您部署成功！** 🎉

更新时间：2026-03-25  
适用版本：EIMS v1.0  
支持平台：阿里云 Ubuntu/CentOS
