# 自建服务器完整指南 - 用个人电脑部署 EIMS 系统

## 📊 可行性分析

### ✅ **可以用自己的电脑做服务器！**

但需要满足一定条件，并且有优缺点需要考虑。

---

## 🎯 适用场景评估

### ✅ 适合使用自建服务器的情况

| 场景 | 评价 | 说明 |
|------|------|------|
| **开发测试** | ✅ 完美 | 零成本，方便调试 |
| **内部演示** | ✅ 很好 | 临时展示，无需购买 |
| **微型企业 (< 10 人)** | ✅ 可以 | 预算有限的选择 |
| **短期使用 (< 6 个月)** | ✅ 推荐 | 过渡期使用 |
| **技术学习** | ✅ 强烈推荐 | 练手最佳选择 |

### ⚠️ 不适合使用自建服务器的情况

| 场景 | 原因 | 建议 |
|------|------|------|
| **生产环境 (> 30 人)** | 稳定性不足 | 购买云服务器 |
| **7×24 小时运行** | 电费 + 硬件损耗 | 云服务器更划算 |
| **对外商业服务** | 可靠性、安全性问题 | 专业云服务 |
| **高并发需求** | 家用带宽限制 | 云服务器 |
| **数据安全性要求高** | 备份、容灾能力弱 | 云服务商 |

---

## 💻 硬件要求

### 最低配置（< 10 人使用）

```
CPU: Intel i5 / AMD Ryzen 5（第 8 代以上）
内存：8GB DDR4
硬盘：256GB SSD
网络：100Mbps 宽带
电源：稳定供电 + UPS 不间断电源（推荐）
```

### 推荐配置（10-30 人使用）

```
CPU: Intel i7 / AMD Ryzen 7（第 10 代以上）
内存：16GB DDR4
硬盘：512GB SSD + 1TB HDD（数据存储）
网络：200Mbps+ 宽带
散热：良好通风环境
UPS：1000VA 以上不间断电源
```

### 理想配置（30-50 人使用）

```
CPU: Intel i9 / AMD Ryzen 9
内存：32GB DDR4
硬盘：1TB NVMe SSD + 4TB HDD
网络：500Mbps+ 光纤专线
UPS：2000VA 在线式 UPS
空调：恒温环境（20-25°C）
```

---

## 💰 成本对比分析

### 自建服务器 vs 云服务器（3 年总成本）

#### 方案 A：利用现有电脑（零硬件投入）

```
【一次性投入】
现有电脑：¥0（已有设备）
UPS 电源：¥500（推荐购买）
──────────────────────
小计：¥500

【持续费用】
电费：¥100/月 × 36 = ¥3,600
      （24 小时运行，约 200W 功耗）
宽带费：¥100/月 × 36 = ¥3,600
        （商用宽带或家庭宽带）
域名：¥60/年 × 3 = ¥180
SSL 证书：¥0（Let's Encrypt 免费）
动态 DNS：¥0（使用免费服务）
──────────────────────
3 年总计：¥7,880
平均每年：¥2,627
平均每月：¥219
```

#### 方案 B：购置二手服务器

```
【一次性投入】
二手服务器：¥2,000（如 Dell R730）
UPS 电源：¥800
网络设备：¥500（路由器、交换机）
──────────────────────
小计：¥3,300

【持续费用】
电费：¥200/月 × 36 = ¥7,200
      （服务器功耗更高）
宽带费：¥100/月 × 36 = ¥3,600
域名：¥60/年 × 3 = ¥180
维护费用：¥500/年 × 3 = ¥1,500
──────────────────────
3 年总计：¥15,780
平均每年：¥5,260
平均每月：¥438
```

#### 方案 C：腾讯云轻量（对比）

```
【云服务器费用】
服务器：¥96/月 × 36 = ¥3,456
数据库：¥187/月 × 36 = ¥6,732
OSS：¥8/月 × 36 = ¥288
CDN：¥15/月 × 36 = ¥540
域名：¥60/年 × 3 = ¥180
──────────────────────
3 年总计：¥11,196
平均每年：¥3,732
平均每月：¥311
```

### 💡 成本结论

```
3 年总成本对比：

利用旧电脑：¥7,880    ← 最便宜
二手服务器：¥15,780
腾讯云：¥11,196
阿里云：¥16,308

省钱排名：
1. 利用旧电脑 → 省 ¥3,316（相比腾讯云）
2. 腾讯云 → 性价比适中
3. 二手服务器 → 反而更贵
```

---

## 🔧 技术实现方案

### 网络架构设计

```
┌─────────────────────────────────────────┐
│          互联网                          │
└─────────────┬───────────────────────────┘
              │
              ↓ (公网访问)
    ┌─────────────────┐
    │   家庭/公司宽带   │
    │   (光猫 + 路由器) │
    └────────┬────────┘
             │
             ↓ (端口转发)
    ┌─────────────────┐
    │   您的电脑       │
    │ ┌─────────────┐ │
    │ │ Nginx       │ │ ← 反向代理
    │ ├─────────────┤ │
    │ │ Gunicorn    │ │ ← Django 应用
    │ ├─────────────┤ │
    │ │ MySQL       │ │ ← 数据库
    │ └─────────────┘ │
    └─────────────────┘
```

---

## 📋 详细部署步骤

### 步骤 1：系统准备

#### 安装操作系统

**推荐：Ubuntu Server 22.04 LTS**

```bash
# 下载镜像
https://ubuntu.com/download/server

# 制作启动盘
# 使用 Rufus (Windows) 或 Etcher

# 安装 Ubuntu
# 按照向导完成安装
```

**或者：Windows 10/11 + WSL2**

```powershell
# Windows 功能启用 WSL
wsl --install

# 安装 Ubuntu 子系统
wsl --install -d Ubuntu-22.04

# 进入 Ubuntu 环境
wsl
```

---

### 步骤 2：安装基础软件

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和依赖
sudo apt install -y python3 python3-pip python3-venv \
    git curl wget nginx mysql-server

# 验证安装
python3 --version  # 应该显示 Python 3.10+
nginx -v           # 应该显示 Nginx 1.18+
mysql --version    # 应该显示 MySQL 8.0+
```

---

### 步骤 3：部署 Django 项目

```bash
# 创建项目目录
sudo mkdir -p /var/www/eims
cd /var/www/eims

# 上传代码（方式 1：Git）
git clone <your-repo-url> .

# 上传代码（方式 2：直接复制）
# 将整个项目复制到 /var/www/eims

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 修改配置

# 数据库迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 创建超级用户
python manage.py createsuperuser
```

---

### 步骤 4：配置 Gunicorn

```bash
# 创建 systemd 服务文件
sudo nano /etc/systemd/system/eims.service
```

**eims.service 内容**：
```ini
[Unit]
Description=EIMS Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/eims
ExecStart=/var/www/eims/venv/bin/gunicorn \
    --access-logfile - \
    --workers 2 \
    --threads 2 \
    --worker-class gthread \
    --bind 127.0.0.1:8000 \
    wsgi:application

[Install]
WantedBy=multi-user.target
```

**启动服务**：
```bash
sudo systemctl daemon-reload
sudo systemctl start eims
sudo systemctl enable eims
sudo systemctl status eims
```

---

### 步骤 5：配置 Nginx

```bash
# 创建站点配置
sudo nano /etc/nginx/sites-available/eims
```

**eims 配置文件**：
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

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
        expires 7d;
    }

    # 反向代理到 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 禁止访问敏感文件
    location ~ /\. {
        deny all;
    }
}
```

**启用站点**：
```bash
sudo ln -sf /etc/nginx/sites-available/eims /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### 步骤 6：配置路由器端口转发

#### 登录路由器管理界面

```
1. 浏览器访问：192.168.1.1 或 192.168.0.1
2. 输入管理员账号密码（通常在路由器底部）
3. 找到"端口转发"或"虚拟服务器"设置
```

#### 添加端口转发规则

```
服务名称：EIMS
外部端口：80（HTTP）、443（HTTPS）
内部 IP 地址：您电脑的局域网 IP（如 192.168.1.100）
内部端口：80
协议：TCP + UDP
状态：启用
```

**保存后重启路由器**。

---

### 步骤 7：获取公网 IP

#### 检查是否有公网 IP

```bash
# 查看本机公网 IP
curl ifconfig.me

# 查看路由器 WAN 口 IP
# 登录路由器管理界面查看

# 如果两个 IP 一致 → 有公网 IP ✅
# 如果不一致 → 无公网 IP ❌
```

#### 如果没有公网 IP

**方法 1：联系运营商申请**
```
电信：拨打 10000 号申请
联通：拨打 10010 号申请
移动：拨打 10086 号申请

话术："家里需要安装监控，需要公网 IP"
通常免费或收取少量费用
```

**方法 2：使用内网穿透**
```
推荐服务：
- ngrok（免费）
- frp（开源）
- 花生壳（付费）
- 神卓互联（付费）
```

**方法 3：使用 IPv6**
```
如果宽带支持 IPv6：
1. 配置 IPv6 地址
2. 使用 IPv6 访问
3. 需要客户端也支持 IPv6
```

---

### 步骤 8：配置动态 DNS（DDNS）

#### 为什么需要 DDNS？

```
家庭宽带的公网 IP 是动态的（会变化）
DDNS 可以将域名自动解析到变化的 IP
```

#### 使用花生壳 DDNS（推荐）

```bash
# 1. 注册花生壳账号
https://hsk.oray.com/

# 2. 下载并安装客户端
wget http://download.oray.com/phtunnel/phddns_linux_x64.deb
sudo dpkg -i phddns_linux_x64.deb

# 3. 配置 SN 码和密码
sudo phddns config

# 4. 启动服务
sudo systemctl start phddns
sudo systemctl enable phddns
```

#### 使用阿里 DDNS（免费）

```bash
# 安装 ddns-go
wget https://github.com/jeessy2/ddns-go/releases/download/v5.8.0/ddns-go_5.8.0_linux_x86_64.tar.gz
tar -xzf ddns-go_5.8.0_linux_x86_64.tar.gz
sudo ./ddns-go -s install

# 配置阿里云 AccessKey
# 访问 http://localhost:9876
```

---

### 步骤 9：配置 SSL 证书（HTTPS）

#### 使用 Let's Encrypt 免费证书

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期配置
sudo crontab -e
# 添加以下行（每天凌晨 2 点检查续期）
0 2 * * * certbot renew --quiet
```

#### 配置 HTTPS 自动跳转

```nginx
# 在 Nginx 配置中添加
server {
    listen 80;
    server_name your-domain.com;
    
    # 强制跳转到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # ... 其他配置
}
```

---

## 🔒 安全加固措施

### 1. 防火墙配置

```bash
# 安装 UFW
sudo apt install -y ufw

# 允许 SSH
sudo ufw allow 22/tcp

# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable
sudo ufw status
```

### 2. 禁用 root 登录

```bash
# 编辑 SSH 配置
sudo nano /etc/ssh/sshd_config

# 修改以下配置
PermitRootLogin no
PasswordAuthentication no  # 使用密钥登录

# 重启 SSH 服务
sudo systemctl restart sshd
```

### 3. 配置 fail2ban（防暴力破解）

```bash
# 安装 fail2ban
sudo apt install -y fail2ban

# 配置
sudo nano /etc/fail2ban/jail.local
```

**jail.local 内容**：
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true
```

```bash
# 启动服务
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

### 4. 定期更新系统

```bash
# 设置自动更新
sudo nano /etc/apt/apt.conf.d/20auto-upgrades
```

**内容**：
```
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
```

### 5. 数据库安全

```sql
-- 删除匿名用户
DELETE FROM mysql.user WHERE User='';

-- 删除测试数据库
DROP DATABASE IF EXISTS test;

-- 限制远程访问
UPDATE mysql.user SET Host='localhost' WHERE User='root';
FLUSH PRIVILEGES;
```

---

## 📊 性能优化建议

### 1. Gunicorn 优化

```bash
# 根据您的 CPU 核心数调整
# workers = (CPU 核心数 × 2) + 1

# 例如 4 核 CPU
workers = (4 × 2) + 1 = 9
```

### 2. MySQL 优化

```ini
# /etc/mysql/my.cnf

[mysqld]
# 根据内存调整
innodb_buffer_pool_size = 2G      # 内存的 50%
max_connections = 100
query_cache_size = 64M
tmp_table_size = 128M
```

### 3. 系统优化

```bash
# 增加文件描述符限制
sudo nano /etc/security/limits.conf

# 添加
www-data soft nofile 65535
www-data hard nofile 65535
```

---

## ⚠️ 潜在问题与解决方案

### 问题 1：停电导致服务中断

**解决方案**：
```
1. 购买 UPS 不间断电源（推荐）
2. 配置自动关机脚本
3. 来电自动启动服务
```

**自动启动配置**：
```bash
# 所有服务都已设置开机自启
sudo systemctl enable nginx
sudo systemctl enable eims
sudo systemctl enable mysql
```

---

### 问题 2：宽带断网

**解决方案**：
```
1. 办理商用宽带（更稳定）
2. 准备 4G/5G 备用网络
3. 使用双线接入（高端方案）
```

---

### 问题 3：硬件故障

**解决方案**：
```
1. 定期备份数据到云端
2. 准备备用服务器
3. 关键硬件冗余（RAID、双电源）
```

**备份脚本示例**：
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup"

# 备份数据库
mysqldump -u root eims_db > ${BACKUP_DIR}/db_${DATE}.sql

# 备份代码
tar -czf ${BACKUP_DIR}/code_${DATE}.tar.gz /var/www/eims

# 上传到云存储（如阿里云 OSS）
ossutil cp ${BACKUP_DIR}/db_${DATE}.sql oss://your-bucket/backup/
ossutil cp ${BACKUP_DIR}/code_${DATE}.tar.gz oss://your-bucket/backup/

# 清理 7 天前的备份
find ${BACKUP_DIR} -name "*.sql" -mtime +7 -delete
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +7 -delete
```

---

### 问题 4：被攻击

**常见攻击类型**：

| 攻击类型 | 特征 | 防御方法 |
|---------|------|---------|
| DDoS | 流量暴增 | 限流、CDN |
| SQL 注入 | 异常查询 | 参数化查询 |
| XSS | 恶意脚本 | 输入过滤 |
| 暴力破解 | 大量登录失败 | fail2ban |

**应急处理**：
```bash
# 1. 查看实时日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 2. 封禁 IP
sudo ufw deny from 1.2.3.4

# 3. 限制请求频率
# 在 Nginx 配置中添加
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;

location / {
    limit_req zone=one burst=20;
    # ...
}
```

---

## 🆚 自建服务器 vs 云服务器 完整对比

### 全方位对比表

| 对比项 | 自建服务器 | 云服务器 | 优势方 |
|--------|-----------|---------|--------|
| **初期投入** | ¥0-3,000 | ¥100-200 | 自建（如果有旧电脑） |
| **月度成本** | ¥200-400 | ¥300-500 | 自建省 ¥100/月 |
| **3 年总成本** | ¥7,880-15,780 | ¥11,196-16,308 | 自建略省 |
| **部署难度** | ⭐⭐⭐⭐⭐ | ⭐⭐ | 云简单 |
| **维护成本** | 高（自己维护） | 低（云厂商维护） | 云省心 |
| **稳定性** | 取决于网络和电力 | 99.95%+ | 云稳定 |
| **性能** | 取决于硬件 | 可弹性伸缩 | 云灵活 |
| **安全性** | 自己负责 | 专业团队 | 云专业 |
| **扩展性** | 受限于硬件 | 随时升级 | 云方便 |
| **备份容灾** | 自己配置 | 自动备份 | 云完善 |
| **技术支持** | 自己解决 | 7×24 支持 | 云有保障 |
| **带宽质量** | 家庭宽带 | BGP 多线 | 云快速 |
| **公网 IP** | 需要申请 | 自带 | 云方便 |
| **适合场景** | 开发测试/小微企业 | 生产环境 | 看需求 |

---

## 💡 最终建议

### ✅ 推荐使用自建服务器的情况

**如果您符合以下条件，建议自建**：

1. ✅ **预算有限** - 不想花钱或花很少的钱
2. ✅ **技术能力强** - 能自己解决各种问题
3. ✅ **用户少** - < 20 人的内部使用
4. ✅ **短期使用** - 过渡期或临时项目
5. ✅ **学习目的** - 想学习服务器运维
6. ✅ **有闲置电脑** - 不浪费资源

---

### ❌ 不推荐使用自建服务器的情况

**如果您符合以下任一条件，建议购买云服务器**：

1. ❌ **生产环境** - 对外商业服务
2. ❌ **用户 > 30 人** - 并发量较大
3. ❌ **数据重要** - 不能丢失业务数据
4. ❌ **没时间维护** - 工作忙，没精力折腾
5. ❌ **不懂技术** - 遇到问题解决不了
6. ❌ **需要高可用** - 要求 7×24 小时稳定运行

---

## 🎯 混合方案（最佳实践）

### 开发用自建，生产用云端

```
【开发测试环境】
✅ 使用自己的电脑
✅ 零成本
✅ 方便调试
✅ 数据不重要

【生产环境】
✅ 购买云服务器
✅ 稳定可靠
✅ 专业维护
✅ 数据安全
```

**成本**：
- 开发环境：¥0（自建）
- 生产环境：¥315/月（腾讯云）
- 总计：¥315/月

**优势**：
- ✅ 开发测试不花钱
- ✅ 生产环境有保障
- ✅ 两者互不影响
- ✅ 总体成本可控

---

## 📋 快速决策指南

### 问自己几个问题：

**Q1: 多少人使用？**
- < 10 人 → 可以自建
- 10-30 人 → 谨慎考虑
- > 30 人 → 建议云服务器

**Q2: 预算多少？**
- 零预算 → 自建
- ¥200/月以内 → 自建
- ¥300/月以上 → 云服务器

**Q3: 技术能力？**
- 精通 Linux → 自建
- 了解基础 → 可以考虑
- 完全不懂 → 云服务器

**Q4: 使用时间？**
- 临时/短期 → 自建
- 长期稳定 → 云服务器

**Q5: 数据重要性？**
- 不重要/可丢失 → 自建
- 重要/不能丢 → 云服务器

---

## 📞 总结

### 我的建议：

**如果您是小微企业/初创团队**：
```
方案：开发自建 + 生产云端
开发测试：用自己电脑（¥0）
生产环境：腾讯云轻量（¥315/月）
总计：¥315/月
```

**如果您只是学习/演示**：
```
方案：完全自建
成本：¥200-400/月（电费 + 宽带）
收获：技术经验 + 实战技能
```

**如果您是生产环境**：
```
方案：直接云服务器
推荐：腾讯云轻量 ¥315/月
理由：稳定、省心、安全
```

---

### 最后提醒：

⚠️ **自建服务器的坑**：
1. 停电就宕机
2. 宽带断了就失联
3. 被攻击要自己处理
4. 数据丢失自己负责
5. 半夜报警要起来修

✅ **云服务器的好处**：
1. 专业团队维护
2. 自动备份
3. 高可用性
4. 弹性伸缩
5. 7×24 技术支持

**人生苦短，能用钱解决的，尽量不要花时间！** 😊

需要我帮您制定详细的自建方案或云服务器选购指南吗？
