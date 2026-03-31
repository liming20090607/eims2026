# EIMS 阿里云 MySQL 部署完整指南

**版本**: 2026-03-26  
**目标环境**: 阿里云 CentOS/Ubuntu + MySQL 8.0 + Python 3.9+

---

## 📋 目录

1. [部署前准备](#部署前准备)
2. [数据库配置](#数据库配置)
3. [服务器环境搭建](#服务器环境搭建)
4. [项目部署](#项目部署)
5. [Nginx 配置](#nginx-配置)
6. [Gunicorn 配置](#gunicorn-配置)
7. [HTTPS 配置](#https-配置)
8. [常见问题](#常见问题)

---

## 🎯 部署前准备

### 本地清理（在 Windows 上执行）

#### 方法 1: 使用清理脚本（推荐）

```bash
# 在 E:\EIMS2026 目录下执行
bash cleanup_for_deploy.sh
```

#### 方法 2: 手动删除

删除以下文件：
```
test_*.py          (10 个测试文件)
debug_*.py         (3 个调试文件)
check_*.py         (4 个检查文件)
*.bat              (Windows 批处理，可选)
*.lnk              (快捷方式)
```

### 修改配置文件

#### 1. 编辑 `.env` 文件

打开 `.env` 文件，修改以下内容：

```ini
# 【必须修改】调试模式
DEBUG=False

# 【必须修改】生成新的密钥
# 在服务器上执行：python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY="在此粘贴生成的密钥"

# 【必须修改】允许的主机
ALLOWED_HOSTS="你的服务器 IP,你的域名，localhost,127.0.0.1"

# 【必须修改】MySQL 数据库配置
DB_NAME="eims_db"
DB_USER="eims_user"
DB_PASSWORD="你的强密码"
DB_HOST="localhost"
DB_PORT="3306"
```

---

## 🗄️ 数据库配置

### 在服务器上创建 MySQL 数据库

#### 方法 1: 使用自动化脚本（推荐）

```bash
# 上传项目后执行
chmod +x setup_mysql.sh
./setup_mysql.sh
```

#### 方法 2: 手动创建

```bash
# 登录 MySQL
mysql -u root -p

# 执行 SQL 命令
CREATE DATABASE IF NOT EXISTS `eims_db` 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'eims_user'@'localhost' 
  IDENTIFIED BY 'your_secure_password';

GRANT ALL PRIVILEGES ON `eims_db`.* TO 'eims_user'@'localhost';

FLUSH PRIVILEGES;

EXIT;
```

---

## 🖥️ 服务器环境搭建

### 1. 安装基础软件

```bash
# CentOS/RHEL
sudo yum update -y
sudo yum install -y python3 python3-pip python3-venv mysql-server nginx git

# Ubuntu/Debian
sudo apt update -y
sudo apt install -y python3 python3-pip python3-venv mysql-server nginx git
```

### 2. 启动 MySQL 和 Nginx

```bash
# CentOS
sudo systemctl start mysqld
sudo systemctl enable mysqld

sudo systemctl start nginx
sudo systemctl enable nginx

# Ubuntu
sudo systemctl start mysql
sudo systemctl enable mysql

sudo systemctl start nginx
sudo systemctl enable nginx
```

### 3. 创建项目目录

```bash
sudo mkdir -p /var/www/eims
sudo chown -R $USER:$USER /var/www/eims
cd /var/www/eims
```

---

## 📦 项目部署

### 1. 上传项目

#### 方法 1: 使用 SCP

```bash
# 在本地执行（Windows PowerShell 或 Git Bash）
scp -r EIMS2026/* user@your_server_ip:/var/www/eims/
```

#### 方法 2: 使用 Git

```bash
# 在服务器上执行
cd /var/www/eims
git clone <your_repository_url> .
```

### 2. 创建虚拟环境

```bash
cd /var/www/eims

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 安装生产环境依赖
pip install gunicorn pymysql
```

### 3. 数据库迁移

```bash
# 确保已激活虚拟环境
source venv/bin/activate

# 执行迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 创建超级用户
python manage.py createsuperuser
```

### 4. 测试运行

```bash
# 临时启动（测试用）
python manage.py runserver 0.0.0.0:8000

# 访问 http://your_server_ip:8000 测试
# 按 Ctrl+C 停止
```

---

## 🔧 Gunicorn 配置

### 1. 创建 Gunicorn 配置文件

创建文件 `/var/www/eims/gunicorn.conf.py`:

```python
# Gunicorn 配置文件
bind = "127.0.0.1:8000"  # 绑定到本地 8000 端口
workers = 3  # 工作进程数（CPU 核心数 * 2 + 1）
worker_class = "sync"
timeout = 120  # 超时时间（秒）
keepalive = 5  # 保持连接时间

# 日志
accesslog = "/var/www/eims/logs/gunicorn_access.log"
errorlog = "/var/www/eims/logs/gunicorn_error.log"
loglevel = "info"

# 进程名
proc_name = "eims_gunicorn"

# 工作目录
chdir = "/var/www/eims"

# 用户组（生产环境建议创建专用用户）
# user = "www-data"
# group = "www-data"
```

### 2. 创建 Systemd 服务

创建文件 `/etc/systemd/system/eims.service`:

```ini
[Unit]
Description=EIMS Django Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/eims
ExecStart=/var/www/eims/venv/bin/gunicorn --config gunicorn.conf.py wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. 启动 Gunicorn

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start eims

# 设置开机自启
sudo systemctl enable eims

# 查看状态
sudo systemctl status eims

# 查看日志
sudo journalctl -u eims -f
```

---

## 🌐 Nginx 配置

### 1. 创建 Nginx 配置文件

创建文件 `/etc/nginx/conf.d/eims.conf`:

```nginx
server {
    listen 80;
    server_name your_domain.com www.your_domain.com your_server_ip;
    
    # 日志
    access_log /var/log/nginx/eims_access.log;
    error_log /var/log/nginx/eims_error.log;
    
    # 静态文件
    location /static/ {
        alias /var/www/eims/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件
    location /media/ {
        alias /var/www/eims/media/;
        expires 30d;
    }
    
    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

### 2. 测试并重启 Nginx

```bash
# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

# 查看状态
sudo systemctl status nginx
```

---

## 🔒 HTTPS 配置（Let's Encrypt）

### 1. 安装 Certbot

```bash
# CentOS
sudo yum install -y certbot python3-certbot-nginx

# Ubuntu
sudo apt install -y certbot python3-certbot-nginx
```

### 2. 获取 SSL 证书

```bash
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

### 3. 自动续期

Certbot 会自动添加定时任务。手动测试续期：

```bash
sudo certbot renew --dry-run
```

---

## ✅ 验证部署

### 1. 检查服务状态

```bash
# Gunicorn
sudo systemctl status eims

# Nginx
sudo systemctl status nginx

# MySQL
sudo systemctl status mysqld  # 或 mysql
```

### 2. 访问网站

```
http://your_server_ip
http://your_domain.com
https://your_domain.com (如果配置了 HTTPS)
```

### 3. 测试管理后台

```
http://your_domain.com/admin/
```

使用创建的超级用户账号登录。

---

## 🔍 常见问题排查

### Q1: Gunicorn 启动失败

**症状**: `systemctl status eims` 显示错误

**解决**:
```bash
# 查看详细日志
sudo journalctl -u eims -n 50

# 常见原因：
# 1. 端口被占用 -> 修改 gunicorn.conf.py 中的 bind
# 2. 权限问题 -> 检查文件所有者
# 3. Python 路径错误 -> 检查 ExecStart 中的路径
```

### Q2: Nginx 502 Bad Gateway

**症状**: 浏览器显示 502 错误

**解决**:
```bash
# 1. 检查 Gunicorn 是否运行
sudo systemctl status eims

# 2. 检查 Nginx 配置
sudo nginx -t

# 3. 检查端口是否正确
netstat -tlnp | grep 8000

# 4. 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/eims_error.log
```

### Q3: 静态文件 404

**解决**:
```bash
# 重新收集静态文件
cd /var/www/eims
source venv/bin/activate
python manage.py collectstatic --noinput --clear

# 检查 Nginx 配置中的 alias 路径
# 确保 /var/www/eims/staticfiles/ 存在
```

### Q4: MySQL 连接失败

**解决**:
```bash
# 1. 检查 MySQL 服务
sudo systemctl status mysqld

# 2. 检查数据库配置
cat /var/www/eims/.env

# 3. 测试数据库连接
mysql -u eims_user -p -e "USE eims_db; SELECT 1;"

# 4. 检查用户权限
mysql -u root -p -e "SHOW GRANTS FOR 'eims_user'@'localhost';"
```

### Q5: 中文乱码

**解决**:
```bash
# 1. 确保 MySQL 使用 utf8mb4
mysql -u root -p -e "SHOW VARIABLES LIKE 'character%';"

# 2. 修改 MySQL 配置（/etc/my.cnf 或 /etc/mysql/mysql.conf.d/mysqld.cnf）
[mysqld]
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 3. 重启 MySQL
sudo systemctl restart mysqld
```

---

## 🛡️ 安全加固

### 1. 防火墙配置

```bash
# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Ubuntu (ufw)
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### 2. 禁用 DEBUG

确保 `.env` 文件中：
```ini
DEBUG=False
```

### 3. 限制 ALLOWED_HOSTS

```ini
ALLOWED_HOSTS="your_domain.com,www.your_domain.com"
```

### 4. 定期备份

```bash
# 使用备份脚本
chmod +x backup_db.sh
./backup_db.sh

# 添加到 crontab（每天凌晨 2 点备份）
crontab -e
0 2 * * * /var/www/eims/backup_db.sh
```

---

## 📊 性能优化建议

### 1. 数据库优化

```sql
-- 添加索引（在 MySQL 中执行）
USE eims_db;

-- 为常用查询字段添加索引
ALTER TABLE eims_app_project ADD INDEX idx_project_status (project_status);
ALTER TABLE eims_app_contract ADD INDEX idx_contract_status (contract_status);
```

### 2. Gunicorn 优化

调整 `gunicorn.conf.py` 中的 worker 数量：
```python
workers = 4  # 根据服务器配置调整
worker_connections = 1000
```

### 3. Nginx 优化

在 `nginx.conf` 的 `http` 块中添加：
```nginx
# 开启 gzip 压缩
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# 客户端最大上传大小
client_max_body_size 10M;
```

---

## 📝 维护清单

### 每日检查
- [ ] 检查服务状态：`systemctl status eims nginx mysqld`
- [ ] 查看错误日志：`tail -f /var/log/nginx/eims_error.log`
- [ ] 磁盘空间：`df -h`

### 每周维护
- [ ] 备份数据库：`./backup_db.sh`
- [ ] 清理过期 session：`python manage.py clearsessions`
- [ ] 更新系统包：`yum update` 或 `apt update`

### 每月维护
- [ ] Django 安全更新检查
- [ ] Python 依赖更新：`pip list --outdated`
- [ ] 审查访问日志分析

---

## 🎉 部署完成！

恭喜！您的 EIMS 系统已成功部署到阿里云。

**下一步**:
1. 测试所有功能是否正常
2. 配置监控告警（可选）
3. 设置日志轮转（可选）
4. 培训用户使用系统

**技术支持**:
- 查看 docs/ 文件夹中的详细文档
- 检查 DEPLOYMENT_CHECKLIST.md 获取完整清单
- 遇到问题先查看常见问题部分

祝使用愉快！🚀
