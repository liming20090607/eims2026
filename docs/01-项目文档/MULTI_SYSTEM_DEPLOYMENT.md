# 单服务器多系统部署方案

## 📊 需求分析

### 场景描述
- **系统数量**：2-3 个类似规模的 Django 系统
- **用户规模**：每个系统服务几十人的小公司（约 50-100 用户/系统）
- **总用户数**：约 150-300 用户
- **功能模块**：人员管理、合同管理、项目管理、审批流程等

---

## ✅ 可行性分析

### 资源需求估算（单个系统）

| 资源项 | 空闲状态 | 正常使用 | 峰值使用 |
|--------|----------|----------|----------|
| CPU 使用率 | 5-10% | 20-30% | 40-50% |
| 内存占用 | 300-500MB | 800MB-1.2GB | 1.5-2GB |
| 磁盘 I/O | 低 | 中等 | 中等 |
| 网络带宽 | < 0.5Mbps | 1-2Mbps | 3-5Mbps |
| 数据库连接 | 2-5 个 | 10-20 个 | 30-50 个 |

### 三个系统总计资源需求

| 资源项 | 正常情况 | 峰值情况 |
|--------|----------|----------|
| **CPU** | 60-90% (2-3 核) | 120-150% (需 4 核+) |
| **内存** | 2.4-3.6GB | 4.5-6GB |
| **带宽** | 3-6Mbps | 9-15Mbps |
| **磁盘** | 150-300GB | 300-600GB |

---

## 🎯 推荐配置方案

### 方案 A：经济型配置（适合预算有限）⭐⭐⭐

**适用**：2 个系统，或 3 个系统但访问量不大

```
CPU: 4 核
内存：8GB
硬盘：200GB SSD
带宽：5-8Mbps
操作系统：Ubuntu 22.04 LTS
```

**💰 成本**：约 ¥200-300/月

**⚠️ 注意事项**：
- 需要合理分配资源
- 建议错峰使用
- 监控资源使用情况
- 可能需要限制并发

**📈 性能预估**：
- 2 个系统：流畅运行 ✅
- 3 个系统：基本可用，高峰期可能卡顿 ⚠️

---

### 方案 B：标准型配置（强烈推荐）⭐⭐⭐⭐⭐

**适用**：3 个系统，每个系统 50-100 用户

```
CPU: 8 核
内存：16GB
硬盘：400GB SSD
带宽：8-12Mbps
操作系统：Ubuntu 22.04 LTS
```

**💰 成本**：约 ¥400-600/月

**✅ 优势**：
- 资源充足，三个系统互不影响
- 有足够的性能余量
- 可以应对业务增长
- 支持未来扩展到 4-5 个系统

**📈 性能预估**：
- 3 个系统：流畅运行 ✅
- 可同时支持 200-300 在线用户
- 页面响应时间：< 1 秒

---

### 方案 C：高性能配置（一步到位）⭐⭐⭐⭐⭐

**适用**：3 个系统 + 高并发需求 + 未来发展

```
CPU: 12-16 核
内存：24-32GB
硬盘：600GB-1TB SSD
带宽：12-20Mbps
操作系统：Ubuntu 22.04 LTS
```

**💰 成本**：约 ¥800-1200/月

**✅ 优势**：
- 性能非常充裕
- 可以轻松支持 5-8 个系统
- 支持高并发场景
- 可部署更多服务（Redis、Elasticsearch 等）

---

## 🔧 技术实现方案

### 架构设计

#### **方案一：共享服务器，隔离运行环境**（推荐）

```
┌─────────────────────────────────────────┐
│         云服务器 (8 核 16GB)             │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │      Nginx (反向代理)             │  │
│  │   company1.com → System1          │  │
│  │   company2.com → System2          │  │
│  │   company3.com → System3          │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │System1  │ │System2  │ │System3  │   │
│  │Gunicorn │ │Gunicorn │ │Gunicorn │   │
│  │:8001    │ │:8002    │ │:8003    │   │
│  └─────────┘ └─────────┘ └─────────┘   │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │      MySQL (多数据库实例)          │  │
│  │   db_company1                     │  │
│  │   db_company2                     │  │
│  │   db_company3                     │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │      Redis (可选，共享)            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**优点**：
- ✅ 资源利用率高
- ✅ 成本低
- ✅ 易于管理
- ✅ 数据隔离（不同数据库）

**缺点**：
- ⚠️ 单点故障风险
- ⚠️ 资源竞争（需监控）

---

#### **方案二：Docker 容器化部署**（最优雅）

```yaml
# docker-compose.yml 示例
version: '3.8'

services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
    depends_on:
      - system1
      - system2
      - system3

  system1:
    build: ./system1
    environment:
      - DJANGO_SETTINGS_MODULE=settings.prod
      - DATABASE_URL=mysql://user:pass@mysql:3306/db_company1
    volumes:
      - ./system1:/app
      - static1:/app/staticfiles

  system2:
    build: ./system2
    environment:
      - DJANGO_SETTINGS_MODULE=settings.prod
      - DATABASE_URL=mysql://user:pass@mysql:3306/db_company2
    volumes:
      - ./system2:/app
      - static2:/app/staticfiles

  system3:
    build: ./system3
    environment:
      - DJANGO_SETTINGS_MODULE=settings.prod
      - DATABASE_URL=mysql://user:pass@mysql:3306/db_company3
    volumes:
      - ./system3:/app
      - static3:/app/staticfiles

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data

volumes:
  mysql_data:
  redis_data:
  static1:
  static2:
  static3:
```

**优点**：
- ✅ 环境隔离最好
- ✅ 部署简单
- ✅ 易于扩展和维护
- ✅ 资源限制可控

**缺点**：
- ⚠️ 学习成本稍高
- ⚠️ 需要 Docker 知识

---

### Nginx 配置示例

```nginx
# /etc/nginx/conf.d/multi-system.conf

# 系统 1 - 公司 A
server {
    listen 80;
    server_name company1.com www.company1.com;

    location /static/ {
        alias /var/www/system1/staticfiles/;
    }

    location /media/ {
        alias /var/www/system1/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# 系统 2 - 公司 B
server {
    listen 80;
    server_name company2.com www.company2.com;

    location /static/ {
        alias /var/www/system2/staticfiles/;
    }

    location /media/ {
        alias /var/www/system2/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# 系统 3 - 公司 C
server {
    listen 80;
    server_name company3.com www.company3.com;

    location /static/ {
        alias /var/www/system3/staticfiles/;
    }

    location /media/ {
        alias /var/www/system3/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

### Gunicorn 配置（每个系统独立）

```bash
# System 1 - 启动命令
cd /var/www/system1
source venv/bin/activate
gunicorn wsgi:application \
    --bind 127.0.0.1:8001 \
    --workers 2 \
    --threads 2 \
    --worker-class gthread \
    --timeout 30 \
    --access-logfile /var/log/system1_access.log \
    --error-logfile /var/log/system1_error.log

# System 2 - 启动命令
cd /var/www/system2
source venv/bin/activate
gunicorn wsgi:application \
    --bind 127.0.0.1:8002 \
    --workers 2 \
    --threads 2 \
    --worker-class gthread \
    --timeout 30 \
    --access-logfile /var/log/system2_access.log \
    --error-logfile /var/log/system2_error.log

# System 3 - 启动命令
cd /var/www/system3
source venv/bin/activate
gunicorn wsgi:application \
    --bind 127.0.0.1:8003 \
    --workers 2 \
    --threads 2 \
    --worker-class gthread \
    --timeout 30 \
    --access-logfile /var/log/system3_access.log \
    --error-logfile /var/log/system3_error.log
```

---

### systemd 服务配置（每个系统独立）

```ini
# /etc/systemd/system/system1.service
[Unit]
Description=EIMS System1 Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/system1
ExecStart=/var/www/system1/venv/bin/gunicorn \
    --bind 127.0.0.1:8001 \
    --workers 2 \
    --threads 2 \
    wsgi:application

[Install]
WantedBy=multi-user.target

# /etc/systemd/system/system2.service
[Unit]
Description=EIMS System2 Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/system2
ExecStart=/var/www/system2/venv/bin/gunicorn \
    --bind 127.0.0.1:8002 \
    --workers 2 \
    --threads 2 \
    wsgi:application

[Install]
WantedBy=multi-user.target

# /etc/systemd/system/system3.service
[Unit]
Description=EIMS System3 Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/system3
ExecStart=/var/www/system3/venv/bin/gunicorn \
    --bind 127.0.0.1:8003 \
    --workers 2 \
    --threads 2 \
    wsgi:application

[Install]
WantedBy=multi-user.target
```

---

### 数据库配置（多实例隔离）

```sql
-- 创建三个独立的数据库
CREATE DATABASE db_company1 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE db_company2 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE db_company3 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建三个独立的用户（推荐，更安全）
CREATE USER 'user_company1'@'localhost' IDENTIFIED BY 'password1';
CREATE USER 'user_company2'@'localhost' IDENTIFIED BY 'password2';
CREATE USER 'user_company3'@'localhost' IDENTIFIED BY 'password3';

-- 授权（每个用户只能访问自己的数据库）
GRANT ALL PRIVILEGES ON db_company1.* TO 'user_company1'@'localhost';
GRANT ALL PRIVILEGES ON db_company2.* TO 'user_company2'@'localhost';
GRANT ALL PRIVILEGES ON db_company3.* TO 'user_company3'@'localhost';

FLUSH PRIVILEGES;
```

---

## 📁 目录结构规划

```
/var/www/
├── system1/                    # 公司 A 的系统
│   ├── manage.py
│   ├── settings.py
│   ├── .env.prod              # 独立的环境变量
│   ├── venv/                  # 独立的虚拟环境
│   ├── staticfiles/           # 独立的静态文件
│   └── media/                 # 独立的媒体文件
│
├── system2/                    # 公司 B 的系统
│   ├── manage.py
│   ├── settings.py
│   ├── .env.prod
│   ├── venv/
│   ├── staticfiles/
│   └── media/
│
├── system3/                    # 公司 C 的系统
│   ├── manage.py
│   ├── settings.py
│   ├── .env.prod
│   ├── venv/
│   ├── staticfiles/
│   └── media/
│
├── logs/                       # 统一日志目录
│   ├── system1_access.log
│   ├── system1_error.log
│   ├── system2_access.log
│   ├── system2_error.log
│   ├── system3_access.log
│   └── system3_error.log
│
└── backup/                     # 统一备份目录
    ├── system1_backup_20260322.sql
    ├── system2_backup_20260322.sql
    └── system3_backup_20260322.sql
```

---

## 🔒 安全隔离策略

### 1. 数据库隔离（必须）

```python
# 每个系统使用独立的数据库
# System 1 - .env.prod
DB_NAME=db_company1
DB_USER=user_company1
DB_PASSWORD=password1

# System 2 - .env.prod
DB_NAME=db_company2
DB_USER=user_company2
DB_PASSWORD=password2

# System 3 - .env.prod
DB_NAME=db_company3
DB_USER=user_company3
DB_PASSWORD=password3
```

### 2. 文件系统隔离

```bash
# 设置正确的文件权限
chown -R www-data:www-data /var/www/system1
chown -R www-data:www-data /var/www/system2
chown -R www-data:www-data /var/www/system3

chmod -R 755 /var/www/system1
chmod -R 755 /var/www/system2
chmod -R 755 /var/www/system3
```

### 3. 环境变量隔离

```bash
# 每个系统有独立的 .env.prod 文件
# 包含独立的 SECRET_KEY、数据库密码等
```

### 4. Session 隔离

```python
# settings.py 中设置不同的 SESSION_COOKIE_NAME
# System 1
SESSION_COOKIE_NAME = 'system1_sessionid'

# System 2
SESSION_COOKIE_NAME = 'system2_sessionid'

# System 3
SESSION_COOKIE_NAME = 'system3_sessionid'
```

---

## 📊 资源监控与优化

### 实时监控脚本

```bash
#!/bin/bash
# monitor_systems.sh - 监控系统资源使用

echo "=== 系统资源监控 ==="
echo "时间：$(date)"
echo ""

# CPU 使用率
echo "CPU 使用率:"
top -bn1 | grep "Cpu(s)" | awk '{print "  "$2"% 用户空间, "$4"% 内核空间"}'
echo ""

# 内存使用率
echo "内存使用率:"
free -h | grep Mem | awk '{print "  已用："$3", 总计："$2", 使用率："$3/$2*100"%"}'
echo ""

# 磁盘使用率
echo "磁盘使用率:"
df -h / | tail -1 | awk '{print "  已用："$3", 总计："$2", 使用率："$5}'
echo ""

# 各系统进程
echo "System1 进程:"
ps aux | grep "[g]unicorn.*:8001" | wc -l
echo "System2 进程:"
ps aux | grep "[g]unicorn.*:8002" | wc -l
echo "System3 进程:"
ps aux | grep "[g]unicorn.*:8003" | wc -l
echo ""

# 网络连接数
echo "网络连接数:"
netstat -an | grep ESTABLISHED | wc -l
echo ""
```

### 资源限制配置

```ini
# /etc/security/limits.conf - 限制每个进程的资源

# 限制 Gunicorn 进程
www-data soft nofile 65535
www-data hard nofile 65535
www-data soft nproc 4096
www-data hard nproc 4096
```

---

## 💡 性能优化建议

### 1. Worker 数量优化

```python
# 根据 CPU 核心数分配
# 8 核 CPU，3 个系统
# 每个系统分配 2 个 worker

# System 1: workers=2
# System 2: workers=2
# System 3: workers=2
# 剩余 2 核用于系统和其他服务
```

### 2. 线程数优化

```python
# 使用 gthread worker 类型
# 每个 worker 2-4 个线程

--worker-class gthread
--threads 2
```

### 3. 数据库连接池

```python
# settings.py
DATABASES = {
    'default': {
        # ...
        'CONN_MAX_AGE': 60,  # 连接复用 60 秒
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'connect_timeout': 10,
        }
    }
}
```

### 4. 缓存优化

```python
# 使用 Redis 缓存（三个系统共享）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/0',  # System1 使用 db 0
    }
}

# System2 使用 db 1
# LOCATION = 'redis://127.0.0.1:6379/1'

# System3 使用 db 2
# LOCATION = 'redis://127.0.0.1:6379/2'
```

---

## 🆘 故障排查

### 常见问题及解决方案

#### 问题 1：某个系统占用过多资源

```bash
# 查看资源占用
ps aux | grep gunicorn

# 限制 worker 数量
# 编辑 systemd 服务文件，减少 workers 数量
sudo systemctl restart system1
```

#### 问题 2：数据库连接数过多

```sql
-- 查看当前连接数
SHOW STATUS LIKE 'Threads_connected';

-- 修改最大连接数
SET GLOBAL max_connections = 200;

-- 在 Django 中限制连接池
CONN_MAX_AGE = 60
```

#### 问题 3：磁盘空间不足

```bash
# 清理日志
find /var/log -name "*.log" -mtime +7 -delete

# 清理过期备份
find /var/www/backup -name "*.sql" -mtime +30 -delete

# 清理静态文件缓存
python manage.py collectstatic --clear
python manage.py collectstatic --noinput
```

---

## 📋 部署检查清单

### 部署前准备

- [ ] 购买云服务器（推荐 8 核 16GB）
- [ ] 注册域名（3 个，分别对应 3 个系统）
- [ ] 域名解析到服务器 IP
- [ ] 安装 Ubuntu 22.04
- [ ] 更新系统包

### 基础环境安装

- [ ] 安装 Python 3.9+
- [ ] 安装 Nginx
- [ ] 安装 MySQL 8.0
- [ ] 安装 Redis（可选）
- [ ] 配置防火墙

### 系统部署

- [ ] 创建目录结构
- [ ] 上传代码（3 个系统）
- [ ] 创建虚拟环境（3 个）
- [ ] 安装依赖（3 次）
- [ ] 配置环境变量（3 份 .env.prod）
- [ ] 创建数据库（3 个）
- [ ] 运行迁移（3 次）
- [ ] 收集静态文件（3 次）
- [ ] 创建超级用户（3 个）

### Web 服务配置

- [ ] 配置 Nginx（3 个 server 块）
- [ ] 配置 Gunicorn（3 个服务）
- [ ] 配置 systemd（3 个服务文件）
- [ ] 启动服务（3 个系统）
- [ ] 配置 SSL 证书（3 个域名）

### 测试验证

- [ ] 访问 System1（company1.com）
- [ ] 访问 System2（company2.com）
- [ ] 访问 System3（company3.com）
- [ ] 测试登录功能
- [ ] 测试主要功能模块
- [ ] 压力测试

---

## 💰 成本对比分析

### 方案对比

| 方案 | 配置 | 成本/月 | 适用场景 |
|------|------|---------|----------|
| **单服务器多系统** | 8 核 16GB | ¥400-600 | 2-3 个小公司系统 ✅ |
| **多台独立服务器** | 3×(2 核 4GB) | ¥600-900 | 完全隔离，成本高 |
| **容器化部署** | 8 核 16GB | ¥400-600 | 最佳实践，易维护 |
| **云服务 SaaS** | 按用户数 | ¥1000-3000 | 最贵，但省心 |

### 节省成本计算

```
传统方案（3 台独立服务器）：
3 × ¥200/月 = ¥600/月

单服务器多系统方案：
1 × ¥500/月 = ¥500/月

每年节省：
(¥600 - ¥500) × 12 = ¥1200/年

如果选择更高配置：
传统方案：3 × ¥400/月 = ¥1200/月
多系统方案：1 × ¥800/月 = ¥800/月
每年节省：(¥1200 - ¥800) × 12 = ¥4800/年
```

---

## ✅ 结论与建议

### 回答您的问题：**完全可以！**

**推荐配置**：
```
CPU: 8 核
内存：16GB
硬盘：400GB SSD
带宽：8-12Mbps
```

**关键要点**：
1. ✅ **技术上完全可行** - Django + Gunicorn + Nginx 架构成熟稳定
2. ✅ **经济高效** - 比单独部署节省 30-50% 成本
3. ✅ **性能充足** - 8 核 16GB 足够支撑 3 个系统正常运行
4. ✅ **安全隔离** - 数据库、文件系统、Session 完全隔离
5. ✅ **易于扩展** - 未来可以扩展到 4-5 个系统

**风险提示**：
- ⚠️ 单点故障风险（一台服务器挂了，所有系统都受影响）
- ⚠️ 资源竞争风险（需要监控和合理分配）
- ⚠️ 安全隔离要求高（配置不当可能导致数据泄露）

**最佳实践建议**：
1. 使用 Docker 容器化部署（最优雅）
2. 做好数据库隔离（独立数据库 + 独立用户）
3. 配置监控系统（实时了解资源使用）
4. 定期备份（每个系统独立备份）
5. 使用对象存储（减少本地存储压力）

---

## 📞 下一步行动

1. **确定配置**
   - 预算充足 → 8 核 16GB
   - 预算有限 → 4 核 8GB（先跑 2 个系统）

2. **选择部署方式**
   - 传统部署（简单直接）
   - Docker 部署（推荐，易维护）

3. **准备资源**
   - 购买服务器
   - 注册域名
   - 准备代码

4. **开始部署**
   - 参考本方案逐步实施
   - 做好测试验证

需要我帮您制定详细的部署计划或提供具体的配置文件吗？😊
