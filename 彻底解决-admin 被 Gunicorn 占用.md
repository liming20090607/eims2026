# 彻底解决：admin 用户被 Gunicorn 进程占用

## 🚨 当前情况分析

**问题：**
```
userdel: user admin is currently used by process 5990
```

**原因：**
- admin 用户有 4 个 gunicorn 进程在运行（PID: 5990, 5991, 5992, 7770）
- 这些是 Django 应用的 worker 进程
- 只要有一个进程在运行，就无法删除用户

---

## ⚡ 立即执行方案（3 分钟）

### 步骤 1：停止所有 Gunicorn 进程

**在 VNC 中执行：**

```bash
# 方法 A：使用 pkill 全部终止（推荐）
pkill -9 -u admin

# 方法 B：逐个杀死
kill -9 5990 5991 5992 7770

# 验证是否全部终止
ps -u admin
# 应该没有任何输出
```

### 步骤 2：停止 Supervisor 服务（防止自动重启）

```bash
# 查看 supervisor 状态
systemctl status supervisord

# 停止 supervisor
systemctl stop supervisord

# 或者使用 supervisorctl
supervisorctl stop all
```

### 步骤 3：强制删除并重建

```bash
# 使用强制模式删除
userdel -f admin

# 如果仍然失败，手动清理
rm -rf /home/admin
sed -i '/^admin:/d' /etc/passwd
sed -i '/^admin:/d' /etc/shadow
sed -i '/^admin:/d' /etc/group
sed -i '/^admin:/d' /etc/gshadow

# 重新创建
useradd -m -s /bin/bash admin

# 设置密码（输入两次，例如：Admin@2026）
passwd admin

# 添加 sudo 权限
usermod -aG wheel admin

# 配置 SSH
su - admin -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"

echo ""
echo "✅ 完成！"
echo "SSH: ssh admin@39.106.41.239"
```

---

## 🎯 完整自动化脚本（推荐）

**复制以下内容到 VNC 执行：**

```bash
cat > /tmp/fix_admin_gunicorn.sh << 'SCRIPT_END'
#!/bin/bash

echo "======================================"
echo "修复 admin 用户被 Gunicorn 占用问题"
echo "======================================"
echo ""

USERNAME="admin"

# 1. 显示当前进程
echo "📋 当前 admin 用户的进程："
ps aux | grep -E "^(USER|${USERNAME})" | grep -v grep
echo ""

# 2. 停止 supervisor 服务
echo "🛑 正在停止 Supervisor 服务..."
systemctl stop supervisord 2>/dev/null || supervisorctl stop all 2>/dev/null
sleep 2
echo "✅ Supervisor 已停止"

# 3. 杀死所有 gunicorn 进程
echo ""
echo "🔪 正在杀死所有 Gunicorn 进程..."
pkill -9 gunicorn
sleep 2

# 检查是否还有 gunicorn 进程
if pgrep -u "$USERNAME" &>/dev/null; then
    echo "⚠️  仍有进程，强制终止..."
    pkill -KILL -u "$USERNAME"
    sleep 2
fi
echo "✅ 所有进程已终止"

# 4. 再次确认
echo ""
echo "🔍 验证进程状态..."
ps -u "$USERNAME" 2>/dev/null || echo "✅ 没有发现进程"

# 5. 强制删除用户
echo ""
echo "🗑️  正在强制删除用户..."
userdel -f "$USERNAME" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️  userdel 失败，尝试手动清理..."
    rm -rf /home/"$USERNAME"
    sed -i "/^${USERNAME}:/d" /etc/passwd
    sed -i "/^${USERNAME}:/d" /etc/shadow
    sed -i "/^${USERNAME}:/d" /etc/group
    sed -i "/^${USERNAME}:/d" /etc/gshadow
    echo "✅ 手动清理完成"
else
    echo "✅ 用户已删除"
fi

# 6. 重新创建
echo ""
echo "🆕 正在创建新用户..."
useradd -m -s /bin/bash "$USERNAME"

if [ $? -eq 0 ]; then
    echo "✅ 用户创建成功"
else
    echo "❌ 用户创建失败"
    exit 1
fi

# 7. 设置密码
echo ""
echo "🔐 请设置密码（输入两次）："
passwd "$USERNAME"

if [ $? -eq 0 ]; then
    echo "✅ 密码设置成功"
else
    echo "❌ 密码设置失败"
    exit 1
fi

# 8. 添加 sudo 权限
usermod -aG wheel "$USERNAME"
echo "✅ sudo 权限已配置"

# 9. 配置 SSH
su - "$USERNAME" -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
echo "✅ SSH 目录已配置"

# 10. 启动 supervisor
echo ""
echo "🚀 正在启动 Supervisor..."
systemctl start supervisord
sleep 2
echo "✅ Supervisor 已启动"

# 11. 显示结果
echo ""
echo "======================================"
echo "✅ admin 用户修复成功！"
echo "======================================"
echo ""
echo "📋 登录信息："
echo "━━━━━━━━━━━━━━━━━━━━"
echo "用户名：$USERNAME"
echo "密  码：(您刚才设置的密码)"
echo "━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔧 SSH 登录命令："
echo "ssh admin@39.106.41.239"
echo ""
echo "切换 root 命令："
echo "sudo su -"
echo ""
echo "📊 用户信息："
id "$USERNAME"
echo ""

echo "🏠 家目录："
ls -la /home/$USERNAME/
echo ""

echo "⚠️  重要提示："
echo "━━━━━━━━━━━━━━━━━━━━"
echo "1. Gunicorn 服务已停止，需要重新启动"
echo "2. 请在本地测试 SSH 登录（不要关闭此窗口）"
echo "3. 登录后需要手动启动服务或重启服务器"
echo ""

# 保存凭据
echo "用户名：$USERNAME" > /root/admin_cred_fixed.txt
echo "创建时间：$(date '+%Y-%m-%d %H:%M:%S')" >> /root/admin_cred_fixed.txt
chmod 600 /root/admin_cred_fixed.txt
echo "💾 凭据已保存到：/root/admin_cred_fixed.txt"
echo ""

SCRIPT_END

chmod +x /tmp/fix_admin_gunicorn.sh
/tmp/fix_admin_gunicorn.sh
```

---

## 🔍 为什么会这样？

### Gunicorn 进程说明

Gunicorn 是 Django 的 WSGI HTTP 服务器，通常以 supervisor 管理：

```
supervisord (父进程)
  └─ gunicorn (master)
      ├─ gunicorn (worker 1) - PID 5990
      ├─ gunicorn (worker 2) - PID 5991
      ├─ gunicorn (worker 3) - PID 5992
      └─ gunicorn (worker 4) - PID 7770
```

这些进程默认以运行用户的身份启动（这里是 admin），所以会占用用户。

---

## 📋 手动分步操作指南

如果您想手动一步步来：

### 第 1 步：停止 Supervisor 服务

```bash
# 查看状态
systemctl status supervisord

# 停止服务
systemctl stop supervisord

# 或者
supervisorctl stop all
```

### 第 2 步：杀死所有 Gunicorn 进程

```bash
# 方法 1：按用户杀死所有进程
pkill -9 -u admin

# 方法 2：按进程名杀死
pkill -9 gunicorn

# 方法 3：逐个杀死
kill -9 5990 5991 5992 7770
```

### 第 3 步：验证进程已终止

```bash
ps -u admin
# 应该没有任何输出
```

### 第 4 步：强制删除用户

```bash
# 使用强制选项
userdel -f admin

# 如果还不行，手动清理
rm -rf /home/admin
grep -v '^admin:' /etc/passwd > /tmp/passwd.new && mv /tmp/passwd.new /etc/passwd
grep -v '^admin:' /etc/shadow > /tmp/shadow.new && mv /tmp/shadow.new /etc/shadow
grep -v '^admin:' /etc/group > /tmp/group.new && mv /tmp/group.new /etc/group
```

### 第 5 步：重新创建

```bash
useradd -m -s /bin/bash admin
passwd admin
usermod -aG wheel admin
su - admin -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
```

### 第 6 步：重启 Supervisor

```bash
systemctl start supervisord
```

---

## ✅ 验证清单

完成后请立即测试：

### 测试 1：SSH 登录

**本地 PowerShell：**
```powershell
ssh admin@39.106.41.239
# 输入密码
```

### 测试 2：sudo 权限

```bash
sudo whoami
# 应输出：root
```

### 测试 3：检查服务状态

```bash
sudo systemctl status supervisord
# 应该是 active (running)

sudo supervisorctl status
# 应该显示 eims: RUNNING
```

---

## 🔧 后续操作

### 如果 Gunicorn 没有自动启动

**手动启动：**

```bash
# 作为 admin 用户
sudo supervisorctl start eims

# 或者重启所有服务
sudo supervisorctl restart all
```

### 如果服务配置丢失

**重新配置：**

```bash
# 检查 supervisor 配置文件
ls -la /etc/supervisord.d/

# 应该有 eims.ini 或类似文件
cat /etc/supervisord.d/eims.ini
```

---

## 🐛 常见问题

### Q: 杀死进程后网站无法访问？

**A:** 正常，因为停止了 Gunicorn。需要重新启动：

```bash
sudo systemctl start supervisord
# 或
sudo supervisorctl start eims
```

### Q: 删除用户时仍然报错？

**A:** 可能有其他会话或定时任务

**解决：**
```bash
# 检查 crontab
crontab -l -u admin

# 检查 systemd 服务
systemctl list-units --all | grep admin

# 检查是否有登录会话
who
w
```

### Q: 忘记密码怎么办？

**A:** 作为 root 可以随时重置：

```bash
passwd admin
```

---

## 📝 下一步：修复 Django Admin

成功创建 admin 用户后，继续修复 Django Admin：

### 快速修复流程

```bash
# SSH 登录
ssh admin@39.106.41.239

# 切换到 root
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

# 访问测试
# http://39.106.41.239/admin/
```

---

## 🎓 知识点总结

### 为什么 Gunicorn 会占用用户？

1. **进程归属**：Gunicorn 以特定用户身份运行
2. **会话保持**：即使 SSH 断开，服务进程仍在运行
3. **文件锁定**：进程可能持有该用户的文件

### 正确的删除流程

1. ✅ 停止相关服务（Supervisor/Gunicorn）
2. ✅ 终止所有用户进程
3. ✅ 验证无进程运行
4. ✅ 强制删除用户
5. ✅ 重新创建并配置

---

**文档创建时间：** 2026-04-02  
**适用场景：** admin 用户被 Gunicorn/Django 进程占用  
**预计用时：** 3-5 分钟
