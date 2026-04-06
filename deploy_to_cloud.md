# 协同 AI 办公系统 - 本地同步到云服务器部署指南

**最后更新：** 2026-04-06

---

## 📋 服务器信息

| 项目 | 信息 |
|------|------|
| **云服务器 IP** | 39.106.41.239 |
| **SSH 用户** | root |
| **代码路径** | /var/www/eims |
| **Git 仓库** | https://gitee.com/liming20090607/eims2026.git |
| **数据库** | MySQL - 数据库名: eims, 用户: root |
| **Web 服务器** | Nginx + Gunicorn |
| **进程管理** | Supervisor |

---

## 🚀 部署流程

### 第一步：本地准备（在本地 Windows 执行）

#### 1.1 提交并推送最新代码

```powershell
cd e:\EIMS2026

# 查看当前状态
git status

# 添加所有更改
git add .

# 提交
git commit -m "更新系统：协同AI办公系统功能完善 - 添加审批流程、优化菜单结构"

# 推送到 Gitee
git push gitee master

# 同时也推送到 GitHub
git push origin master
```

#### 1.2 导出本地数据库

```powershell
# 使用我们创建的备份脚本
python backup_local.py
```

生成的备份文件类似：`backup_local_20260406_172503.json`

---

### 第二步：备份服务器数据（SSH 登录服务器）

#### 2.1 登录服务器

```bash
ssh root@39.106.41.239
```

#### 2.2 备份当前数据库

```bash
# 进入项目目录
cd /var/www/eims

# 创建备份目录（如果不存在）
mkdir -p backups

# 备份当前数据库
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u root -p eims > backups/eims_backup_${DATE}.sql

# 压缩备份文件
gzip backups/eims_backup_${DATE}.sql

# 查看备份文件
ls -lh backups/
```

#### 2.3 备份服务器代码（可选，以防需要回滚）

```bash
# 备份当前代码
tar -czf /var/backups/eims_code_backup_$(date +%Y%m%d_%H%M%S).tar.gz /var/www/eims
```

---

### 第三步：更新服务器代码

#### 3.1 拉取最新代码

```bash
cd /var/www/eims

# 拉取最新代码
git pull gitee master

# 或者从 GitHub 拉取
git pull origin master
```

#### 3.2 检查是否有新的依赖

```bash
# 激活虚拟环境
source /var/www/eims/venv/bin/activate

# 检查 requirements.txt 是否有更新
cat requirements.txt

# 如果有新依赖，安装它们
pip install -r requirements.txt
```

#### 3.3 更新数据库配置

```bash
# 编辑 .env 文件（如果需要）
vi .env

# 确保数据库配置正确：
# DB_NAME=eims
# DB_USER=root
# DB_PASSWORD=你的MySQL root密码
# DB_HOST=localhost
# DB_PORT=3306
```

#### 3.4 应用数据库迁移

```bash
# 在虚拟环境中执行
cd /var/www/eims
source venv/bin/activate

# 检查是否有新的迁移
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput
```

---

### 第四步：导入本地数据（可选）

**注意：** 这一步只有在您希望将本地数据同步到服务器时才执行。

#### 4.1 上传备份文件到服务器

在本地 PowerShell 中执行：

```powershell
# 上传备份文件
scp e:\EIMS2026\backup_local_20260406_172503.json root@39.106.41.239:/var/www/eims/
```

#### 4.2 在服务器上导入数据

```bash
# SSH 登录服务器
ssh root@39.106.41.239

cd /var/www/eims

# 激活虚拟环境
source venv/bin/activate

# 清空现有数据（谨慎操作！）
python manage.py flush --noinput

# 导入备份数据
python manage.py loaddata backup_local_20260406_172503.json
```

---

### 第五步：重启服务

```bash
# 重启 Gunicorn 服务
supervisorctl restart eims

# 查看服务状态
supervisorctl status

# 如果 Supervisor 未运行，启动它
systemctl restart supervisord

# 重启 Nginx
systemctl restart nginx

# 检查服务状态
systemctl status nginx
systemctl status supervisord
```

---

### 第六步：验证部署

#### 6.1 检查服务状态

```bash
# 检查 Gunicorn 进程
ps aux | grep gunicorn

# 检查 Nginx 状态
nginx -t

# 查看日志
tail -f /var/log/nginx/error.log
tail -f /var/www/eims/logs/gunicorn.log
```

#### 6.2 测试访问

在本地浏览器访问：
- **HTTP**: http://39.106.41.239
- **HTTPS**: https://39.106.41.239（如果配置了 SSL）

测试功能：
1. ✅ 登录页面
2. ✅ 首页导航
3. ✅ 审批流程
4. ✅ 合同管理
5. ✅ 项目管理

---

## ⚠️ 常见问题处理

### 问题 1：端口 80 被占用

```bash
# 查找占用端口的进程
lsof -i :80

# 或使用
netstat -tuln | grep :80

# 停止冲突的服务
systemctl stop httpd  # 或其他占用端口的服务
```

### 问题 2：Gunicorn 启动失败

```bash
# 查看详细日志
journalctl -u supervisord -n 50 --no-pager

# 检查 Gunicorn 配置
cat /etc/supervisord.d/eims.ini

# 手动测试 Gunicorn
cd /var/www/eims
source venv/bin/activate
gunicorn --bind 127.0.0.1:8000 wsgi:application
```

### 问题 3：静态文件不加载

```bash
# 重新收集静态文件
cd /var/www/eims
source venv/bin/activate
python manage.py collectstatic --noinput

# 检查 Nginx 配置
cat /etc/nginx/conf.d/eims.conf

# 重启 Nginx
systemctl restart nginx
```

### 问题 4：数据库连接失败

```bash
# 测试数据库连接
mysql -u root -p -e "USE eims; SELECT COUNT(*) FROM auth_user;"

# 检查 MySQL 服务
systemctl status mysqld  # 或 mariadb

# 重启 MySQL
systemctl restart mysqld
```

---

## 📝 快速部署命令（一键脚本）

创建一个快速部署脚本：

```bash
#!/bin/bash
# 文件：/var/www/eims/deploy.sh

echo "开始部署更新..."

cd /var/www/eims

# 1. 拉取代码
echo "1. 拉取最新代码..."
git pull gitee master

# 2. 激活虚拟环境并更新依赖
echo "2. 更新 Python 依赖..."
source venv/bin/activate
pip install -r requirements.txt

# 3. 数据库迁移
echo "3. 应用数据库迁移..."
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# 4. 重启服务
echo "4. 重启服务..."
supervisorctl restart eims
systemctl restart nginx

echo "部署完成！"
```

使用方式：
```bash
# 添加执行权限
chmod +x /var/www/eims/deploy.sh

# 执行部署
/var/www/eims/deploy.sh
```

---

## 🎯 本次部署检查清单

- [ ] 本地代码已提交并推送到 Gitee/GitHub
- [ ] 本地数据库已备份（backup_local_*.json）
- [ ] SSH 登录到服务器（root@39.106.41.239）
- [ ] 服务器数据库已备份
- [ ] 服务器代码已拉取最新提交
- [ ] Python 依赖已更新
- [ ] 数据库迁移已应用
- [ ] 静态文件已收集
- [ ] Gunicorn 服务已重启
- [ ] Nginx 服务已重启
- [ ] 系统功能测试通过

---

## 📞 技术支持

如遇问题，请检查：
1. 日志文件：`/var/www/eims/logs/`
2. Nginx 错误日志：`/var/log/nginx/error.log`
3. Supervisor 日志：`journalctl -u supervisord`

**祝您部署顺利！** 
