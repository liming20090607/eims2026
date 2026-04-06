# admin 用户创建成功 - 下一步操作指南

## ✅ 当前状态

**admin 用户已成功创建！**

从输出可以看到：
```
uid=1001(admin) gid=1001(admin) groups=1001(admin),10(wheel)
```

这说明：
- ✅ 用户已创建（uid=1001）
- ✅ 家目录已创建（gid=1001）
- ✅ sudo 权限已配置（在 wheel 组）
- ⚠️ 密码设置失败（需要重新设置）

---

## 🔐 立即设置密码

**在 VNC 中执行：**

```bash
# 作为 root，直接为 admin 设置密码
passwd admin

# 系统会提示输入两次密码
# 建议设置一个强密码，例如：Admin@20260402
# 或者您自己设定的密码
```

**密码要求：**
- ✅ 至少 8 个字符
- ✅ 包含大小写字母
- ✅ 包含数字
- ✅ 包含特殊字符
- ❌ 不要使用简单的密码（如 admin123、password 等）

**推荐密码示例：**
- `Admin@2026`
- `EIMS_Admin#2026`
- `Server@39.106`

---

## 🧪 测试 SSH 登录

### 步骤 1：不要关闭 VNC 窗口

保持 VNC 连接打开，以便出现问题时可以及时解决。

### 步骤 2：在本地 PowerShell 中测试

**打开新的 PowerShell 窗口：**

```powershell
# 测试 SSH 登录
ssh admin@39.106.41.239

# 输入刚才设置的密码
```

**成功标志：**
```
[admin@iZ2ze74hagmo3egfxeffrcZ ~]$
```

### 步骤 3：测试 sudo 权限

**登录后执行：**

```bash
# 测试 sudo
sudo whoami
# 应输出：root

# 切换到 root
sudo su -
# 输入 admin 密码后应进入 root shell

# 返回 admin 用户
exit
```

---

## 🚀 继续修复 Django Admin

成功创建 admin 用户并测试登录后，继续修复 Django Admin 显示问题。

### 方法 A：上传修复后的 settings.py

**在本地 PowerShell 执行：**

```powershell
# 上传 settings.py
scp E:\EIMS2026\settings.py admin@39.106.41.239:/var/www/eims/

# SSH 登录
ssh admin@39.106.41.239

# 登录后切换到 root
sudo su -

# 进入项目目录
cd /var/www/eims

# 激活虚拟环境
source venv/bin/activate

# 验证 settings.py 语法
python -c "import settings; print('OK')"

# 重新收集静态文件
python manage.py collectstatic --clear --noinput
python manage.py collectstatic --noinput

# 重启服务
supervisorctl restart eims

# 查看服务状态
supervisorctl status eims
```

### 方法 B：使用一键修复脚本

**在本地运行脚本：**

```
双击运行：E:\EIMS2026\bat\修复 Django 版本兼容问题.bat
```

输入 admin 密码即可自动完成所有修复步骤。

---

## 📋 完整验证清单

请按顺序验证以下项目：

### 1. SSH 登录验证

- [ ] 可以从本地 SSH 登录
  ```powershell
  ssh admin@39.106.41.239
  ```

- [ ] 登录后显示欢迎信息
  ```
  [admin@iZ2ze74hagmo3egfxeffrcZ ~]$
  ```

### 2. sudo 权限验证

- [ ] 可以执行 sudo 命令
  ```bash
  sudo whoami
  # 输出：root
  ```

- [ ] 可以切换到 root
  ```bash
  sudo su -
  # 进入 root shell
  ```

### 3. 服务状态验证

- [ ] Supervisor 正常运行
  ```bash
  sudo systemctl status supervisord
  # 应该是 active (running)
  ```

- [ ] Gunicorn 正常运行
  ```bash
  sudo supervisorctl status eims
  # 应该显示 RUNNING
  ```

### 4. Django Admin 验证

- [ ] 访问 Admin 后台
  ```
  http://39.106.41.239/admin/
  ```

- [ ] 页面样式正常显示
  - 有 CSS 样式（不是纯 HTML）
  - 顶部显示"协同 AI 办公系统"
  - 左侧导航栏正常
  - 无黑块或乱码

---

## 🐛 常见问题解决

### 问题 1：忘记密码

**解决：**
```bash
# 在 VNC 中作为 root 执行
passwd admin

# 重新设置密码
```

### 问题 2：SSH 登录仍然失败

**诊断：**
```bash
# 检查 SSH 服务
systemctl status sshd

# 检查防火墙
sudo firewall-cmd --list-all

# 查看详细日志
tail -f /var/log/secure
```

**解决：**
```bash
# 确保密码登录被允许
sudo vi /etc/ssh/sshd_config
# 确保：PasswordAuthentication yes

# 重启 SSH
sudo systemctl restart sshd
```

### 问题 3：Gunicorn 没有自动启动

**解决：**
```bash
# 手动启动
sudo supervisorctl start eims

# 或重启所有服务
sudo supervisorctl restart all
```

### 问题 4：网站无法访问

**可能原因：** Gunicorn 未启动或端口被占用

**解决：**
```bash
# 检查进程
ps aux | grep gunicorn

# 检查端口
sudo netstat -tlnp | grep 8000

# 重启服务
sudo supervisorctl restart eims
```

---

## 📝 如果密码设置失败

从脚本输出看到密码设置有误，现在手动设置：

### 在 VNC 中执行：

```bash
# 作为 root
passwd admin

# 输入新密码（例如：Admin@20260402）
# 再次输入确认密码

# 如果提示密码太简单，可以使用更复杂的密码
# 例如：EIMS_Admin@39.106.41.239
```

### 密码策略说明

**错误信息解释：**
```
BAD PASSWORD: The password fails the dictionary check - it is too simplistic/systematic
```

这意味着：
- ❌ 密码太简单（如 admin123、password 等）
- ❌ 使用了常见单词
- ❌ 模式太规则

**如何设置强密码：**
- ✅ 使用大小写字母混合：`AaBbCc`
- ✅ 添加数字：`2026`
- ✅ 添加特殊字符：`@#$%`
- ✅ 至少 8 个字符
- ✅ 避免连续字符：`123456`、`abcdef`

**推荐密码格式：**
```
大写字母 + 小写字母 + 数字 + 特殊字符
例如：Admin@2026、EIMS_Sys#2026
```

---

## 🎓 知识点总结

### 为什么密码设置失败但用户创建成功了？

1. **useradd 成功** → 用户账户已创建
2. **passwd 失败** → 密码不符合策略要求
3. **结果** → 用户存在但没有有效密码

**解决方案：**
- 作为 root 可以直接设置密码（ bypass 策略检查）
- 或使用复杂密码满足策略要求

### 完整的用户管理流程

```bash
# 1. 创建用户
useradd -m -s /bin/bash admin

# 2. 设置密码
passwd admin

# 3. 添加 sudo 权限
usermod -aG wheel admin

# 4. 验证
id admin
# 输出：uid=1001(admin) gid=1001(admin) groups=1001(admin),10(wheel)

# 5. 测试登录
ssh admin@服务器 IP
```

---

## ✅ 成功标志

当您看到以下内容时，说明一切正常：

```
✅ admin 用户已创建
✅ 可以 SSH 登录
✅ sudo 权限正常
✅ Gunicorn 服务运行正常
✅ Django Admin 可以访问且样式正常
```

---

**文档创建时间：** 2026-04-02  
**当前状态：** admin 用户创建成功，需要设置密码  
**下一步：** 设置密码 → 测试 SSH → 修复 Django Admin
