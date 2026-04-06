# 紧急解决：admin 用户被进程占用问题

## 🚨 您当前的情况

**错误信息：**
```
userdel: user admin is currently used by process 5976
```

**含义：** admin 用户正在被 SSH 会话（进程 5976）占用，无法删除。

---

## ⚡ 立即执行的解决方案（30 秒）

### 在 VNC 窗口中直接运行以下命令：

```bash
# 1️⃣ 杀死占用进程
kill -9 5976

# 2️⃣ 等待 3 秒
sleep 3

# 3️⃣ 验证进程已终止
ps -u admin

# 4️⃣ 强制删除用户
userdel -r admin

# 5️⃣ 重新创建
useradd -m -s /bin/bash admin

# 6️⃣ 设置密码（输入两次，例如：Admin@2026）
passwd admin

# 7️⃣ 添加 sudo 权限
usermod -aG wheel admin

# 8️⃣ 配置 SSH
su - admin -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"

# 9️⃣ 验证
id admin

# 🔟 完成提示
echo ""
echo "✅ admin 用户创建成功！"
echo "SSH 登录：ssh admin@39.106.41.239"
echo "切换 root: sudo su -"
```

---

## 🎯 或者使用增强版自动脚本

**复制以下完整内容到 VNC：**

```bash
cat > /tmp/force_create_admin_v2.sh << 'SCRIPT_END'
#!/bin/bash

echo "======================================"
echo "强制创建 admin 用户（增强版）"
echo "======================================"

USERNAME="admin"
PID_TO_KILL=5976

# 1. 杀死占用进程
echo ""
echo "🔪 正在杀死占用进程 $PID_TO_KILL..."
kill -9 $PID_TO_KILL 2>/dev/null
sleep 3

# 2. 检查是否还有其他进程
if ps -u "$USERNAME" &>/dev/null; then
    echo "⚠️  仍有进程，强制终止..."
    pkill -9 -u "$USERNAME"
    sleep 2
fi
echo "✅ 进程已清理"

# 3. 删除用户
echo ""
echo "🗑️  正在删除旧用户..."
userdel -r "$USERNAME" 2>/dev/null || userdel -f "$USERNAME" 2>/dev/null
echo "✅ 已删除"

# 4. 创建新用户
echo ""
echo "🆕 创建新用户..."
useradd -m -s /bin/bash "$USERNAME"
echo "✅ 用户创建成功"

# 5. 设置密码（手动输入）
echo ""
echo "🔐 请设置密码（输入两次）："
passwd "$USERNAME"

# 6. 添加 sudo 权限
usermod -aG wheel "$USERNAME"
echo "✅ sudo 权限已配置"

# 7. 配置 SSH
su - "$USERNAME" -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
echo "✅ SSH 目录已配置"

# 8. 显示结果
echo ""
echo "======================================"
echo "✅ 成功！"
echo "======================================"
echo ""
echo "SSH 登录：ssh admin@39.106.41.239"
echo "切换 root: sudo su -"
echo ""
echo "📊 用户信息："
id "$USERNAME"
echo ""

SCRIPT_END

chmod +x /tmp/force_create_admin_v2.sh
/tmp/force_create_admin_v2.sh
```

---

## 📋 详细步骤说明

### 为什么会出现这个问题？

当您通过 SSH 或其他方式以 admin 用户登录时，系统会创建一个会话进程。如果这个会话没有正常退出，进程就会继续存在，导致无法删除用户。

### 解决步骤详解：

#### 步骤 1：识别并终止进程
```bash
# 查看是什么进程在使用 admin
ps aux | grep admin

# 典型输出：
# admin  5976  0.0  0.1 sshd: admin@pts/0
# 这是 SSH 会话进程
```

#### 步骤 2：强制终止
```bash
kill -9 5976
# -9 表示 SIGKILL，强制立即终止
```

#### 步骤 3：验证
```bash
ps -u admin
# 应该没有任何输出，说明没有 admin 用户的进程了
```

#### 步骤 4：删除并重建
```bash
userdel -r admin
# -r 表示同时删除家目录

useradd -m -s /bin/bash admin
# -m 创建家目录
# -s 设置登录 shell 为 bash
```

#### 步骤 5：设置权限
```bash
passwd admin
# 交互式设置密码

usermod -aG wheel admin
# -aG 添加到 wheel 组（sudo 权限）
```

---

## ✅ 验证清单

完成后请立即测试：

### 测试 1：本地 SSH 登录

**打开本地 PowerShell（不要关闭 VNC 窗口）：**
```powershell
ssh admin@39.106.41.239

# 输入刚才设置的密码
```

**成功标志：**
```
[admin@iZ2ze74hagmo3egfxeffrcZ ~]$
```

### 测试 2：sudo 权限

**登录后执行：**
```bash
sudo whoami

# 应输出：root
```

### 测试 3：切换到 root

```bash
sudo su -

# 输入 admin 密码后应进入 root shell
```

---

## 🐛 如果仍然失败

### 情况 1：杀死进程后立即又有新进程

**可能原因：** systemd 服务或 cron 任务

**解决：**
```bash
# 查看是否有 systemd 服务
systemctl list-units --all | grep admin

# 查看 crontab
crontab -l

# 如果是登录会话，直接退出即可
exit
```

### 情况 2：userdel 仍然报错

**使用强制模式：**
```bash
userdel -f admin
# -f 表示强制删除，即使用户正在登录
```

### 情况 3：文件系统只读

**检查并重新挂载：**
```bash
mount | grep "on / "
# 如果是 ro（read-only），需要重新挂载为 rw

mount -o remount,rw /
```

---

## 📝 下一步：修复 Django Admin

成功创建 admin 用户后，继续修复 Django Admin 显示问题：

### 方法 A：使用自动修复脚本（推荐）

**在本地 PowerShell 执行：**
```powershell
# 上传修复后的 settings.py
scp E:\EIMS2026\settings.py admin@39.106.41.239:/var/www/eims/

# SSH 登录
ssh admin@39.106.41.239

# 登录后切换到 root
sudo su -

# 进入项目目录
cd /var/www/eims

# 激活虚拟环境
source venv/bin/activate

# 重新收集静态文件
python manage.py collectstatic --clear --noinput
python manage.py collectstatic --noinput

# 重启服务
supervisorctl restart eims
```

### 方法 B：一键修复脚本

**在本地运行：**
```
E:\EIMS2026\bat\修复 Django 版本兼容问题.bat
```

输入 admin 密码即可自动完成。

---

## 🔒 安全建议

### 1. 修改默认密码

首次登录后建议修改密码：
```bash
passwd admin
```

### 2. 禁用 root SSH 直接登录

**编辑 SSH 配置：**
```bash
vi /etc/ssh/sshd_config

# 修改这行
PermitRootLogin no

# 重启 SSH
systemctl restart sshd
```

### 3. 使用 SSH 密钥

比密码更安全：
```bash
# 生成密钥对（本地）
ssh-keygen -t rsa -b 4096

# 上传公钥
cat ~/.ssh/id_rsa.pub | ssh admin@39.106.41.239 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

---

## 📞 仍然遇到问题？

### 请提供以下信息：

1. **完整的错误输出**
   ```
   复制 VNC 中的完整错误信息
   ```

2. **执行的命令和输出**
   ```bash
   # 例如：
   ps -u admin
   id admin
   ```

3. **当前状态**
   - [ ] 已经杀死进程 5976
   - [ ] 已经删除 admin 用户
   - [ ] 重新创建了 admin 用户
   - [ ] 但仍然无法 SSH 登录

---

**文档创建时间：** 2026-04-02  
**适用场景：** admin 用户被进程占用无法删除的紧急情况  
**预计解决时间：** 1-2 分钟
