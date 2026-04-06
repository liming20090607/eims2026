# 使用 root 用户修复服务器

## 📋 当前状况

**已知信息：**
- ✅ root 用户可以登录（通过阿里云 Workbench 密码登录）
- ❌ admin 用户可能无法登录
- ❌ 网页无法访问（ERR_CONNECTION_RESET）

**可能原因：**
1. Gunicorn 服务未运行
2. Supervisor 服务未运行
3. 防火墙阻止 8000 端口
4. 阿里云安全组未配置

---

## 🚀 快速修复步骤

### 步骤 1：使用 root 登录服务器

根据截图，使用 **Workbench 密码登录**：

1. 在阿里云控制台点击 **"立即登录"**（Workbench 密码登录）
2. 用户名：`root`
3. 输入 root 密码
4. 登录成功

---

### 步骤 2：上传诊断脚本

在本地 PowerShell 执行：

```powershell
scp E:\EIMS2026\bat\服务器诊断与修复-root 用.sh root@39.106.41.239:/tmp/
```

---

### 步骤 3：执行诊断脚本

在 Workbench 终端执行：

```bash
chmod +x /tmp/服务器诊断与修复-root 用.sh
bash /tmp/服务器诊断与修复-root 用.sh
```

**脚本会自动检查：**
- ✅ 系统状态（CPU、内存、磁盘）
- ✅ 网络连通性
- ✅ SSH 服务
- ✅ Gunicorn 进程
- ✅ Supervisor 状态
- ✅ 端口监听
- ✅ 防火墙配置
- ✅ Django 项目

**然后选择操作：**
```
1. 启动 Supervisor 和 Gunicorn
2. 重启所有服务
3. 查看错误日志
4. 测试本地访问
5. 退出
```

**建议先选择 1**（启动服务）

---

## 🔧 手动修复（如果脚本不行）

### 1. 启动 Supervisor

```bash
systemctl start supervisord
systemctl enable supervisord  # 设置开机自启
```

### 2. 启动 Gunicorn

```bash
# 查看服务状态
supervisorctl status

# 启动 EIMS 服务
supervisorctl start eims

# 如果服务不存在，创建配置
cat > /etc/supervisord.d/eims.ini << EOF
[program:eims]
command=/var/www/eims/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 eims.wsgi:application
directory=/var/www/eims
user=admin
autostart=true
autorestart=true
stderr_logfile=/var/log/eims/error.log
stdout_logfile=/var/log/eims/access.log
EOF

# 重新加载
supervisorctl reread
supervisorctl update
supervisorctl start eims
```

### 3. 配置防火墙

```bash
# 检查状态
firewall-cmd --state

# 如果运行中，开放端口
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload

# 验证
firewall-cmd --list-ports
```

### 4. 检查端口

```bash
# 查看 8000 端口
netstat -tlnp | grep 8000

# 应该看到
# tcp  0  0 0.0.0.0:8000  0.0.0.0:*  LISTEN  1234/python
```

### 5. 测试本地访问

```bash
curl http://localhost:8000/admin/
```

---

## 🛡️ 配置阿里云安全组（必须）

**这是外部访问的关键！**

### 步骤 1：打开安全组配置

1. 阿里云控制台 → ECS → 实例详情
2. 点击 **安全组** 标签
3. 点击 **配置规则**
4. 选择 **入方向**

### 步骤 2：添加规则

点击 **手动添加**：

| 优先级 | 策略 | 协议 | 端口 | 授权对象 | 描述 |
|--------|------|------|------|---------|------|
| 1 | 允许 | TCP | 8000/8000 | 0.0.0.0/0 | Django 应用 |
| 1 | 允许 | TCP | 22/22 | 0.0.0.0/0 | SSH（已有） |

### 步骤 3：保存

点击 **保存** 按钮。

---

## ✅ 验证修复

### 1. 检查服务状态

```bash
# 检查进程
ps aux | grep gunicorn

# 检查端口
netstat -tlnp | grep 8000

# 检查 Supervisor
supervisorctl status eims
```

**正常输出：**
```
root     1234  0.0  0.5  xxxxx  gunicorn: master
admin    1235  0.1  1.0  xxxxx  gunicorn: worker
tcp        0      0 0.0.0.0:8000    0.0.0.0:*    LISTEN      1234/python
eims: OK
```

### 2. 本地测试

```bash
curl -I http://localhost:8000/admin/
```

**预期：** HTTP 200 或 302

### 3. 远程测试

在浏览器访问：
```
http://39.106.41.239:8000/admin/
```

**预期：** 看到 Django Admin 登录页面

---

## 🔍 常见问题

### Q1: Supervisor 启动失败

**检查日志：**
```bash
journalctl -u supervisord | tail -n 20
```

**可能原因：**
- 配置文件错误
- Gunicorn 未安装
- 虚拟环境路径错误

**解决：**
```bash
# 检查配置
cat /etc/supervisord.d/eims.ini

# 测试 Gunicorn
cd /var/www/eims
source venv/bin/activate
gunicorn --version
```

### Q2: Gunicorn 绑定失败

**错误：** `Address already in use`

**解决：**
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 重启 Gunicorn
supervisorctl restart eims
```

### Q3: 防火墙问题

**测试：** 临时关闭防火墙

```bash
# 临时关闭
systemctl stop firewalld

# 测试访问
curl http://localhost:8000/

# 如果成功，需要配置防火墙规则
systemctl start firewalld
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload
```

### Q4: admin 用户问题

**检查 admin 账号：**
```bash
id admin
```

**如果不存在，创建：**
```bash
useradd -m -s /bin/bash admin
passwd admin
usermod -aG wheel admin
```

---

## 📊 完整检查清单

- [ ] root 可以登录
- [ ] Supervisor 正在运行
- [ ] Gunicorn 正在运行（至少 3 个进程）
- [ ] 端口 8000 正在监听（0.0.0.0:8000）
- [ ] 防火墙已开放 8000 端口
- [ ] 阿里云安全组已配置 8000 端口
- [ ] 本地 curl 测试成功
- [ ] 浏览器可以访问

---

## 📞 仍然无法访问？

### 提供以下信息以便诊断：

1. **诊断脚本输出**
   ```bash
   bash /tmp/服务器诊断与修复-root 用.sh
   ```

2. **服务状态**
   ```bash
   supervisorctl status eims
   ```

3. **进程列表**
   ```bash
   ps aux | grep gunicorn
   ```

4. **端口监听**
   ```bash
   netstat -tlnp | grep 8000
   ```

5. **错误日志**
   ```bash
   tail -n 20 /var/log/eims/error.log
   ```

6. **安全组截图**
   - 阿里云控制台 → 安全组 → 入方向规则

---

## 💡 建议操作顺序

**推荐：**
1. ✅ 使用 root 登录 Workbench
2. ✅ 运行诊断脚本（选项 1）
3. ✅ 配置阿里云安全组（必须！）
4. ✅ 测试访问

**预计时间：** 5-10 分钟

---

**最后更新：** 2026-04-03  
**适用环境：** Alibaba Cloud Linux, Django 4.2.7, Gunicorn, Supervisor  
**服务器 IP：** 39.106.41.239
