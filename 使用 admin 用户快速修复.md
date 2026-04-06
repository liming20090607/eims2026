# 使用 admin 用户快速修复服务器

## ✅ 当前状况

**好消息：**
- ✅ root 用户可以登录
- ✅ admin 用户也可以登录
- ❌ 网页无法访问（需要修复）

---

## 🚀 最快修复方案（5 分钟）

### 步骤 1：SSH 登录 admin

使用 SSH 工具登录：
```bash
ssh admin@39.106.41.239
```

输入您找回的 admin 密码。

**或使用阿里云 Workbench：**
1. 点击 **"立即登录"**（Workbench 密码登录）
2. 用户名：`admin`
3. 输入 admin 密码

---

### 步骤 2：上传诊断脚本

在本地 PowerShell 执行：
```powershell
scp E:\EIMS2026\bat\服务器诊断与修复-admin 用.sh admin@39.106.41.239:/tmp/
```

---

### 步骤 3：执行修复脚本

SSH 或 Workbench 中执行：

```bash
# 添加执行权限
chmod +x /tmp/服务器诊断与修复-admin 用.sh

# 运行脚本
bash /tmp/服务器诊断与修复-admin 用.sh
```

**脚本会自动诊断：**
- ✅ Gunicorn 进程状态
- ✅ Supervisor 服务状态
- ✅ 端口 8000 监听
- ✅ 防火墙配置
- ✅ Django 项目配置
- ✅ 错误日志

**然后选择操作：**
```
1. 启动 Supervisor 和 Gunicorn (推荐)
2. 重启所有服务
3. 查看错误日志
4. 测试本地访问
5. 开放防火墙 8000 端口
6. 退出
```

**建议先选择 1**（启动服务）

---

## 🔧 手动修复命令（如果脚本不行）

### 1. 启动 Supervisor

```bash
sudo systemctl start supervisord
sudo systemctl enable supervisord  # 开机自启
```

### 2. 启动 Gunicorn

```bash
# 查看服务状态
sudo supervisorctl status

# 启动 EIMS
sudo supervisorctl start eims

# 如果服务不存在
sudo supervisorctl reread
sudo supervisorctl update
```

### 3. 检查进程和端口

```bash
# 检查 Gunicorn 进程
ps aux | grep gunicorn

# 检查端口 8000
sudo netstat -tlnp | grep 8000
```

### 4. 配置防火墙（如果需要）

```bash
# 查看防火墙状态
sudo firewall-cmd --state

# 开放 8000 端口
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# 验证
sudo firewall-cmd --list-ports
```

---

## 🛡️ 阿里云安全组配置（必须）

**这是外部访问的关键！**

### 配置步骤

1. **访问阿里云控制台**
   - https://ecs.console.aliyun.com/

2. **找到实例**
   - 搜索 IP：`39.106.41.239`
   - 点击实例 ID

3. **配置安全组**
   - 点击 **安全组** → **配置规则**
   - 选择 **入方向**
   - 点击 **手动添加**

4. **添加规则**
   ```
   优先级：1
   策略：允许
   协议类型：TCP
   端口范围：8000/8000
   授权对象：0.0.0.0/0
   描述：Django 应用端口
   ```

5. **保存**

---

## ✅ 验证修复

### 检查清单

```bash
# 1. 检查进程
ps aux | grep gunicorn
# 应该看到 1 个 master + 3 个 workers

# 2. 检查端口
sudo netstat -tlnp | grep 8000
# 应该显示 0.0.0.0:8000 LISTEN

# 3. 检查 Supervisor
sudo supervisorctl status eims
# 应该显示 RUNNING

# 4. 本地测试
curl http://localhost:8000/admin/
# 应该返回 HTTP 200 或 302
```

### 浏览器测试

打开浏览器访问：
```
http://39.106.41.239:8000/admin/
```

按 `Ctrl+F5` 强制刷新

**预期：** 看到 Django Admin 登录页面

---

## 🔍 常见问题

### Q1: admin 用户没有 sudo 权限

**错误：** `user is not in the sudoers file`

**解决：**
```bash
# 使用 root 登录
ssh root@39.106.41.239

# 添加 admin 到 wheel 组
usermod -aG wheel admin

# 验证
id admin
# 应该显示 groups=1001(admin),10(wheel)
```

---

### Q2: Supervisor 服务不存在

**检查：**
```bash
sudo supervisorctl status
# 显示 eims: ERROR (no such group)
```

**解决：**
```bash
# 创建配置文件
sudo nano /etc/supervisord.d/eims.ini
```

**内容：**
```ini
[program:eims]
command=/var/www/eims/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 eims.wsgi:application
directory=/var/www/eims
user=admin
autostart=true
autorestart=true
stderr_logfile=/var/log/eims/error.log
stdout_logfile=/var/log/eims/access.log
```

**然后：**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start eims
```

---

### Q3: Gunicorn 未安装

**检查：**
```bash
source /var/www/eims/venv/bin/activate
python -c "import gunicorn"
# 如果报错，说明未安装
```

**安装：**
```bash
pip install gunicorn
```

---

### Q4: 端口被占用

**错误：** `Address already in use`

**解决：**
```bash
# 查找占用进程
sudo lsof -i :8000

# 杀死进程
sudo kill -9 <PID>

# 重启 Gunicorn
sudo supervisorctl restart eims
```

---

## 📊 完整检查清单

修复完成后，请确认：

- [ ] admin 可以 SSH 登录
- [ ] admin 有 sudo 权限
- [ ] Supervisor 正在运行
- [ ] Gunicorn 有 3-4 个进程
- [ ] 端口 8000 正在监听
- [ ] 防火墙已开放 8000 端口
- [ ] 阿里云安全组已配置
- [ ] 本地 curl 测试成功
- [ ] 浏览器可以访问

---

## 📞 仍然无法访问？

### 提供以下信息：

1. **诊断脚本输出**
   ```bash
   bash /tmp/服务器诊断与修复-admin 用.sh
   ```

2. **服务状态**
   ```bash
   sudo supervisorctl status eims
   ```

3. **进程列表**
   ```bash
   ps aux | grep gunicorn
   ```

4. **端口监听**
   ```bash
   sudo netstat -tlnp | grep 8000
   ```

5. **错误日志**
   ```bash
   sudo tail -n 20 /var/log/eims/error.log
   ```

6. **安全组配置截图**

---

## 💡 建议操作顺序

**推荐：**
1. ✅ 使用 admin SSH 登录
2. ✅ 运行诊断脚本（选择选项 1）
3. ✅ 配置阿里云安全组（必须！）
4. ✅ 浏览器测试访问

**预计时间：** 5-10 分钟

---

## 📁 相关工具文件

- **诊断脚本：** [`bat\服务器诊断与修复-admin 用.sh`](file://e:\EIMS2026\bat\服务器诊断与修复-admin 用.sh)
- **root 用户脚本：** [`bat\服务器诊断与修复-root 用.sh`](file://e:\EIMS2026\bat\服务器诊断与修复-root 用.sh)
- **完整指南：** [`使用 root 用户修复服务器.md`](file://e:\EIMS2026\使用 root 用户修复服务器.md)

---

**最后更新：** 2026-04-03  
**适用环境：** Alibaba Cloud Linux, Django 4.2.7, Gunicorn, Supervisor  
**服务器 IP：** 39.106.41.239
