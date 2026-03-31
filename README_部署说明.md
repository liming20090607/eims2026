# 🚀 EIMS 阿里云部署快速指南

## 📦 部署文件说明

本项目已为您准备好完整的阿里云部署文件：

### 1. 📄 文档类
- **`部署指南_阿里云.md`** - 完整的部署教程（472 行）
- **`部署检查清单.md`** - 逐步检查清单（325 行）
- **`README_部署说明.md`** - 本文件，快速参考

### 2. 🔧 脚本类
- **`deploy.sh`** - 自动化部署脚本（95 行）
- **`backup_db.sh`** - 数据库备份脚本（25 行）

### 3. ⚙️ 配置类
- **`settings_production.py`** - 生产环境配置模板（129 行）

---

## 🎯 快速部署流程（10 分钟）

### 前置准备
1. **阿里云账号** - 已注册并完成实名认证
2. **ECS 服务器** - Ubuntu 22.04，1 核 2GB 起
3. **域名**（可选）- 已备案（国内服务器）

### 步骤 1：购买和配置服务器
```
阿里云控制台 → ECS → 创建实例
- 操作系统：Ubuntu 22.04
- 配置：1 核 2GB（建议 2 核 4GB）
- 网络：按量付费或包年包月
- 安全组：开放 80、443、22 端口
```

### 步骤 2：连接服务器
```bash
ssh root@你的服务器公网 IP
```

### 步骤 3：上传项目（3 种方法任选）

**方法 A：使用 Git（推荐）**
```bash
sudo mkdir -p /var/www/eims
sudo chown -R $USER:$USER /var/www/eims
cd /var/www/eims
git clone <你的仓库地址> .
```

**方法 B：使用 SCP（从本地上传）**
```bash
# 在本地 PowerShell 执行
scp -r e:\EIMS2026\* root@服务器 IP:/var/www/eims/
```

**方法 C：使用 FTP 工具**
- 下载 FileZilla 或 WinSCP
- 连接到服务器
- 上传整个项目到 `/var/www/eims/`

### 步骤 4：运行自动部署脚本
```bash
cd /var/www/eims
chmod +x deploy.sh
sudo bash deploy.sh
```

脚本会自动：
- ✅ 安装 Python、Nginx、MySQL
- ✅ 创建数据库和用户
- ✅ 配置 Systemd 服务
- ✅ 配置 Nginx 反向代理
- ✅ 配置防火墙

### 步骤 5：手动配置（重要！）

#### 5.1 创建虚拟环境
```bash
cd /var/www/eims
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn mysqlclient
```

#### 5.2 配置 .env 文件
```bash
nano .env
```

添加内容：
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=你的超长随机密钥（运行下面的命令生成）
DJANGO_ALLOWED_HOSTS=你的域名，服务器 IP

# 数据库配置
DB_NAME=eims
DB_USER=eims_user
DB_PASSWORD=你设置的数据库密码
DB_HOST=localhost
DB_PORT=3306

# 文件路径
MEDIA_ROOT=/var/www/eims/media
STATIC_ROOT=/var/www/eims/staticfiles
```

生成随机密钥：
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 5.3 修改 settings.py
```bash
nano settings.py
```

修改关键配置：
```python
DEBUG = False
ALLOWED_HOSTS = ['你的域名', '服务器 IP']
```

或直接使用生产配置：
```bash
cp settings_production.py settings.py
# 然后根据实际情况修改
```

#### 5.4 数据库迁移
```bash
cd /var/www/eims
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 5.5 重启服务
```bash
sudo systemctl restart eims
sudo systemctl restart nginx
sudo systemctl status eims
sudo systemctl status nginx
```

### 步骤 6：配置 SSL 证书（推荐）
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d 你的域名
# 按提示输入邮箱和域名
```

---

## 📊 部署后验证

### 访问测试
- 前台：http://你的域名
- 后台：http://你的域名/admin
- API：http://你的域名/api/

### 功能检查清单
- [ ] 首页正常显示
- [ ] 管理员后台可登录
- [ ] 静态文件（CSS/JS）正常加载
- [ ] 媒体文件（上传的文件）正常访问
- [ ] 数据库操作正常
- [ ] 所有功能模块正常

### 服务状态检查
```bash
# 应用服务
sudo systemctl status eims

# Web 服务器
sudo systemctl status nginx

# 数据库
sudo systemctl status mysql

# 查看日志
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔧 日常维护

### 日志查看
```bash
# 实时查看日志
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/log/nginx/access.log

# 查看最近 100 行
sudo tail -n 100 /var/log/gunicorn/error.log
```

### 数据库备份
```bash
# 手动备份
mysqldump -u eims_user -p eims > backup_$(date +%Y%m%d).sql

# 配置自动备份
crontab -e
# 添加：0 2 * * * /var/www/eims/backup_db.sh
```

### 服务重启
```bash
# 重启应用
sudo systemctl restart eims

# 重启 Nginx
sudo systemctl restart nginx

# 全部重启
sudo systemctl restart eims nginx
```

### 代码更新
```bash
cd /var/www/eims
git pull  # 或使用其他方式上传代码
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart eims
```

---

## 🐛 常见问题

### 1. 502 Bad Gateway
**原因**：Gunicorn 未运行
```bash
sudo systemctl status eims
sudo systemctl restart eims
sudo tail -f /var/log/gunicorn/error.log
```

### 2. 静态文件 404
**原因**：未收集静态文件
```bash
source venv/bin/activate
python manage.py collectstatic --clear --noinput
sudo systemctl restart nginx
```

### 3. 数据库连接失败
```bash
# 检查 MySQL 状态
sudo systemctl status mysql

# 测试连接
python manage.py dbshell
```

### 4. 权限错误
```bash
sudo chown -R www-data:www-data /var/www/eims
sudo chmod -R 755 /var/www/eims
```

### 5. 端口被占用
```bash
# 查看端口占用
sudo netstat -tulpn | grep 8000

# 杀掉占用进程
sudo kill -9 进程 ID
```

---

## 📞 技术支持

### 官方文档
- **Django**: https://docs.djangoproject.com/
- **Gunicorn**: https://docs.gunicorn.org/
- **Nginx**: https://nginx.org/
- **MySQL**: https://dev.mysql.com/doc/

### 社区论坛
- **Django 中文社区**: https://www.django.cn/
- **SegmentFault**: https://segmentfault.com/
- **知乎 Django 话题**: https://www.zhihu.com/topic/19552832

### 阿里云文档
- **ECS 使用指南**: https://help.aliyun.com/product/25362.html
- **安全组配置**: https://help.aliyun.com/document_detail/25471.html
- **域名备案**: https://help.aliyun.com/product/27354.html

---

## 🔐 安全建议

### 必须配置
1. ✅ `DEBUG = False`
2. ✅ 修改 `ALLOWED_HOSTS`
3. ✅ 使用强密码（数据库、管理员）
4. ✅ 生成随机 `SECRET_KEY`（50+ 字符）
5. ✅ 配置 HTTPS
6. ✅ 定期备份数据库

### 推荐配置
1. ✅ 使用 Redis 缓存
2. ✅ 配置防火墙规则
3. ✅ 限制文件上传大小
4. ✅ 配置日志轮转
5. ✅ 启用自动安全更新

---

## 📈 性能优化

### 基础优化
- 使用 Gunicorn 多 worker
- Nginx 静态文件缓存
- 数据库查询优化
- 开启 Gzip 压缩

### 高级优化
- Redis 缓存热点数据
- CDN 加速静态资源
- 数据库主从复制
- 负载均衡（多服务器）

---

## 🎉 部署完成！

现在您的 EIMS 系统已经成功部署到阿里云！

**下一步**：
1. 访问网站测试所有功能
2. 配置域名备案（如需要）
3. 申请 SSL 证书
4. 设置监控告警
5. 配置自动备份

**祝部署顺利！** 🚀

---

*最后更新时间：2026 年 3 月 31 日*
