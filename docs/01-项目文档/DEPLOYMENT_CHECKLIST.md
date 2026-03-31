# 📋 阿里云部署检查清单

## 🎯 部署前准备

### 本地准备（在 Windows 电脑上完成）
- [ ] 确认项目所有功能正常
- [ ] 整理 `requirements.txt`
- [ ] 创建 `.gitignore` 文件
- [ ] 测试数据库配置为 MySQL
- [ ] 准备好上传工具（Git/FTP/SCP）

---

## 📦 服务器环境检查

### 基础环境
- [ ] 系统已更新：`apt update && apt upgrade -y` (Ubuntu) 或 `yum update -y` (CentOS)
- [ ] Python 版本：`python3 --version` (建议 3.8+)
- [ ] MySQL 服务：`systemctl status mysql` 或 `systemctl status mysqld`
- [ ] MySQL 驱动：确认已安装 `pymysql` 或 `mysqlclient`

---

## 🚀 部署步骤检查

### Step 1: 数据库配置
- [ ] 登录 MySQL：`mysql -u root -p`
- [ ] 创建数据库：`CREATE DATABASE eims_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
- [ ] 创建用户：`CREATE USER 'eims_user'@'localhost' IDENTIFIED BY '强密码';`
- [ ] 授权：`GRANT ALL PRIVILEGES ON eims_db.* TO 'eims_user'@'localhost';`
- [ ] 刷新权限：`FLUSH PRIVILEGES;`
- [ ] 测试连接：`mysql -u eims_user -p eims_db`

---

### Step 2: 上传代码
**选择一种方式**:

#### Git 方式（推荐）
- [ ] 本地初始化：`cd E:\EIMS2026 && git init`
- [ ] 提交代码：`git add . && git commit -m "Initial commit"`
- [ ] 创建远程仓库（GitHub/Gitee）
- [ ] 推送代码：`git remote add origin <仓库地址> && git push -u origin main`
- [ ] 服务器克隆：`cd /home && git clone <仓库地址> eims`

#### SCP 方式
- [ ] 本地压缩：`Compress-Archive E:\EIMS2026 E:\EIMS2026.zip`
- [ ] 上传文件：`scp E:\EIMS2026.zip root@服务器 IP:/tmp/`
- [ ] 服务器解压：`cd /home && unzip /tmp/EIMS2026.zip`

#### FTP/SFTP 方式
- [ ] 安装 FileZilla 或 WinSCP
- [ ] 连接服务器（IP、用户名 root、密码）
- [ ] 上传到 `/home/eims/` 目录

---

### Step 3: 安装依赖
- [ ] 进入项目目录：`cd /home/eims`
- [ ] 创建虚拟环境：`python3 -m venv venv`
- [ ] 激活虚拟环境：`source venv/bin/activate`
- [ ] 升级 pip：`pip install --upgrade pip`
- [ ] 安装依赖：`pip install -r requirements.txt`
- [ ] 安装生产环境包：`pip install gunicorn django-widget-tweaks`

---

### Step 4: 配置文件
- [ ] 创建 `.env` 文件
- [ ] 设置 `DJANGO_DEBUG=False`
- [ ] 生成并设置 `DJANGO_SECRET_KEY`（使用命令生成随机密钥）
- [ ] 配置数据库连接信息
- [ ] 设置 `ALLOWED_HOSTS` 为服务器 IP

**生成密钥命令**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### Step 5: 数据库迁移
- [ ] 应用迁移：`python manage.py migrate`
- [ ] 收集静态文件：`python manage.py collectstatic --noinput`
- [ ] 创建超级管理员：`python manage.py createsuperuser`
- [ ] 记录管理员账号信息：__________ / __________

---

### Step 6: Gunicorn 配置
- [ ] 创建服务文件：`/etc/systemd/system/eims.service`
- [ ] 配置 WorkingDirectory 为项目路径
- [ ] 配置 ExecStart 指向正确的 gunicorn 路径
- [ ] 重载 systemd：`systemctl daemon-reload`
- [ ] 启动服务：`systemctl start eims`
- [ ] 设置开机启动：`systemctl enable eims`
- [ ] 查看状态：`systemctl status eims`（应为 active running）

---

### Step 7: Nginx 配置
- [ ] 安装 Nginx：`apt install nginx -y` 或 `yum install nginx -y`
- [ ] 创建站点配置：`/etc/nginx/sites-available/eims`
- [ ] 配置 server_name 为服务器 IP
- [ ] 配置静态文件路径：`alias /home/eims/staticfiles/;`
- [ ] 配置媒体文件路径：`alias /home/eims/media/;`
- [ ] 配置反向代理：`proxy_pass http://unix:/home/eims/eims.sock;`
- [ ] 启用站点：`ln -s /etc/nginx/sites-available/eims /etc/nginx/sites-enabled/`
- [ ] 测试配置：`nginx -t`
- [ ] 重启 Nginx：`systemctl restart nginx`
- [ ] 设置开机启动：`systemctl enable nginx`

---

### Step 8: 阿里云安全组配置
**登录阿里云控制台 → 云服务器 ECS → 安全组**

- [ ] 添加规则：允许 80 端口（HTTP）
- [ ] 添加规则：允许 443 端口（HTTPS，如配置）
- [ ] 确认 22 端口已开放（SSH）

---

## ✅ 功能测试

### 基本访问测试
- [ ] 浏览器访问：`http://服务器 IP/`
- [ ] 页面加载正常
- [ ] 静态文件（CSS/JS）加载正常
- [ ] 图片/媒体文件显示正常

---

### 登录功能测试
- [ ] 访问登录页面
- [ ] 使用管理员账号登录
- [ ] 成功跳转到首页
- [ ] 右上角显示用户名

---

### 主要功能测试
- [ ] 合同台账列表显示
- [ ] 项目台账列表显示
- [ ] 创建新合同
- [ ] 创建新项目
- [ ] 文件上传功能
- [ ] 数据编辑功能
- [ ] 搜索功能
- [ ] 分页功能

---

### 移动端测试
- [ ] 手机浏览器访问
- [ ] 响应式布局正常
- [ ] 侧边栏可折叠
- [ ] 表格可横向滚动
- [ ] 按钮大小适中易于点击

---

### 多用户测试
- [ ] 创建第二个用户账号
- [ ] 使用第二账号登录
- [ ] 两个账号同时操作不冲突
- [ ] 数据隔离正常（如有权限控制）

---

## 🔧 性能和安全检查

### 性能优化
- [ ] Gunicorn workers 数量合理（建议 3-5 个）
- [ ] Nginx 启用 gzip 压缩（可选）
- [ ] 静态文件正确收集
- [ ] 数据库索引优化（可选）

---

### 安全加固
- [ ] DEBUG 已设置为 False
- [ ] SECRET_KEY 已更换为随机密钥
- [ ] ALLOWED_HOSTS 限制为实际域名/IP
- [ ] 数据库使用专用用户（非 root）
- [ ] 数据库密码为强密码
- [ ] 防火墙配置（UFW/firewalld）
- [ ] 定期备份策略

---

## 📊 监控和维护

### 日志检查
- [ ] Nginx 访问日志：`tail -f /var/log/nginx/access.log`
- [ ] Nginx 错误日志：`tail -f /var/log/nginx/error.log`
- [ ] Gunicorn 日志：`journalctl -u eims -f`
- [ ] Django 日志：`tail -f /home/eims/logs/django_error.log`

---

### 资源监控
- [ ] CPU 使用率：`top` 或 `htop`
- [ ] 内存使用：`free -h`
- [ ] 磁盘空间：`df -h`
- [ ] 网络连接：`netstat -tulpn`

---

### 备份策略
- [ ] 创建数据库备份脚本
- [ ] 配置定时任务（crontab）
- [ ] 测试恢复流程
- [ ] 备份文件存储位置确认

---

## 🆘 故障排查

### 常见问题

#### 502 Bad Gateway
- [ ] 检查 Gunicorn 是否运行：`systemctl status eims`
- [ ] 检查 socket 文件是否存在：`ls -la /home/eims/eims.sock`
- [ ] 重启 Gunicorn：`systemctl restart eims`

#### 404 Not Found
- [ ] 检查 URL 配置
- [ ] 检查静态文件路径
- [ ] 运行 `collectstatic`

#### 500 Internal Server Error
- [ ] 查看 Django 日志
- [ ] 查看 Nginx 错误日志
- [ ] 检查数据库连接

#### 无法访问网站
- [ ] 检查防火墙：`ufw status` 或 `firewall-cmd --list-all`
- [ ] 检查安全组规则
- [ ] 检查服务状态：`systemctl status nginx eims`

---

## 📝 文档记录

### 重要信息记录
- [ ] 服务器 IP：_______________
- [ ] SSH 账号：_______________
- [ ] 数据库名：_______________
- [ ] 数据库用户：_______________
- [ ] 管理员账号：_______________
- [ ] 域名（如有）：_______________

---

### 配置文件备份
- [ ] `.env` 文件内容备份（加密存储）
- [ ] `eims.service` 备份
- [ ] Nginx 配置备份
- [ ] 数据库备份

---

## 🎉 部署完成确认

最后确认：
- [ ] 所有功能测试通过
- [ ] 性能满足要求
- [ ] 安全措施已落实
- [ ] 监控机制已建立
- [ ] 备份策略已配置
- [ ] 相关文档已完善

---

**部署完成时间**: ______年______月______日  
**部署人员**: _______________  
**验收人员**: _______________

---

## 📞 后续支持

遇到问题时的检查顺序：
1. 查看应用日志
2. 查看 Web 服务器日志
3. 检查系统资源
4. 重启相关服务
5. 查阅部署文档
6. 联系技术支持

---

**祝部署顺利！** 🚀
