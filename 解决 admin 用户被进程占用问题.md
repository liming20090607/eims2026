# 解决 admin 用户已存在且被占用的问题

## 🔍 问题分析

**错误信息：**
```
userdel: user admin is currently used by process 5976
```

**含义：** admin 用户已被某个进程（PID 5976）使用，无法直接删除。

---

## ⚡ 快速解决方案

### 方法 1：强制删除并重建（推荐）⭐⭐⭐⭐⭐

**在 VNC 中执行以下命令：**

```bash
# 1. 查看是什么进程在使用 admin 用户
ps -u admin

# 或者查看特定进程
ps aux | grep 5976

# 2. 终止该进程
kill -9 5976

# 3. 如果还有会话，强制退出
pkill -9 -u admin

# 4. 确认没有 admin 用户的进程了
ps -u admin

# 5. 现在可以删除并重新创建了
userdel -r admin

# 6. 重新创建 admin 用户
useradd -m -s /bin/bash admin

# 7. 设置密码（手动输入两次）
passwd admin

# 8. 添加 sudo 权限
usermod -aG wheel admin

# 9. 验证
id admin

# 10. 配置 SSH 目录
su - admin -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"

# 11. 显示登录信息
echo ""
echo "✅ admin 用户创建成功！"
echo "━━━━━━━━━━━━━━━━━━"
echo "用户名：admin"
echo "密  码：(您刚才设置的密码)"
echo "━━━━━━━━━━━━━━━━━━"
echo "SSH 登录：ssh admin@39.106.41.239"
echo "切换 root: sudo su -"
```

---

### 方法 2：直接使用现有 admin 用户

如果您不介意使用现有的 admin 用户，可以直接设置密码：

```bash
# 检查用户是否存在
id admin

# 如果存在，直接设置密码
passwd admin
# 输入两次新密码

# 确保有 sudo 权限
usermod -aG wheel admin

# 配置 SSH 目录
su - admin -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"

# 完成
echo "✅ admin 用户配置完成！"
echo "SSH 登录：ssh admin@39.106.41.239"
```

---

### 方法 3：完整清理脚本

**复制以下完整脚本到 VNC：**

```bash
cat > /tmp/force_create_admin.sh << 'SCRIPT_END'
#!/bin/bash

echo "======================================"
echo "强制创建 admin 用户"
echo "======================================"

USERNAME="admin"

# 1. 查找并显示所有 admin 用户的进程
echo ""
echo "📋 正在检查 admin 用户的进程..."
ps aux | grep -E "^(USER|${USERNAME})" | grep -v grep

# 2. 终止所有 admin 用户的进程
echo ""
echo "🔧 正在终止 admin 用户的所有进程..."
pkill -9 -u "$USERNAME" 2>/dev/null

# 等待一下
sleep 2

# 3. 再次检查
if ps -u "$USERNAME" &>/dev/null; then
    echo "⚠️  仍有进程在运行，尝试强制终止..."
    pkill -KILL -u "$USERNAME" 2>/dev/null
    sleep 1
fi

# 4. 删除用户
echo ""
echo "🗑️  正在删除旧用户..."
userdel -r "$USERNAME" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 已删除旧用户 $USERNAME"
else
    echo "⚠️  用户删除失败，继续尝试创建..."
fi

# 5. 创建新用户
echo ""
echo "🆕 正在创建新用户 $USERNAME..."
useradd -m -s /bin/bash "$USERNAME"

if [ $? -ne 0 ]; then
    echo "❌ 用户创建失败"
    exit 1
fi

echo "✅ 用户创建成功"

# 6. 设置随机密码
RANDOM_PASS=$(openssl rand -base64 12)
echo "$RANDOM_PASS" | passwd --stdin "$USERNAME" &>/dev/null

echo "✅ 密码设置成功"

# 7. 添加 sudo 权限
usermod -aG wheel "$USERNAME"
echo "✅ sudo 权限已配置"

# 8. 配置 SSH
su - "$USERNAME" -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
echo "✅ SSH 目录已配置"

# 9. 显示结果
echo ""
echo "======================================"
echo "✅ admin 用户强制创建成功！"
echo "======================================"
echo ""
echo "📋 登录信息："
echo "━━━━━━━━━━━━━━━━━━━━"
echo "用户名：$USERNAME"
echo "密  码：$RANDOM_PASS"
echo "━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  重要提示："
echo "1. 请立即复制上面的密码"
echo "2. 建议首次登录后修改密码"
echo "3. 使用 'sudo su -' 切换 root"
echo ""
echo "🔧 SSH 登录命令："
echo "ssh admin@39.106.41.239"
echo ""
echo "📊 用户信息："
id "$USERNAME"
echo ""

# 保存凭据
echo "用户名：$USERNAME" > /root/admin_cred.txt
echo "密码：$RANDOM_PASS" >> /root/admin_cred.txt
chmod 600 /root/admin_cred.txt
echo "💾 凭据已保存到：/root/admin_cred.txt"
echo ""

SCRIPT_END

chmod +x /tmp/force_create_admin.sh
/tmp/force_create_admin.sh
```

---

## 🔍 详细诊断步骤

### 步骤 1：查看是什么进程在使用 admin

```bash
# 查看 admin 用户的所有进程
ps -u admin

# 或查看详细信息
ps aux | grep admin
```

**可能的输出：**
```
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
admin     5976  0.0  0.1  12345  6789 ?        Ss   17:59   0:00 sshd: admin@pts/0
```

这说明是 SSH 会话在使用 admin 用户。

### 步骤 2：终止进程

```bash
# 终止特定进程
kill -9 5976

# 或终止所有 admin 用户的进程
pkill -9 -u admin
```

### 步骤 3：验证进程已终止

```bash
# 应该没有任何输出
ps -u admin
```

---

## 🎯 推荐的完整流程

**基于您当前的情况，我建议：**

```bash
# 1. 终止占用进程
kill -9 5976

# 2. 等待几秒
sleep 3

# 3. 检查是否还有其他进程
ps -u admin

# 4. 如果有，全部终止
pkill -9 -u admin

# 5. 删除用户
userdel -r admin

# 6. 重新创建
useradd -m -s /bin/bash admin

# 7. 设置一个好记的密码
passwd admin
# 输入两次密码（例如：Admin@2026）

# 8. 添加 sudo 权限
usermod -aG wheel admin

# 9. 验证
id admin
# 应显示：uid=1001(admin) gid=1001(admin) groups=1001(admin),10(wheel)

# 10. 配置 SSH
su - admin -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"

# 11. 测试本地登录
# 不要关闭 VNC，打开本地 PowerShell 测试
# ssh admin@39.106.41.239
```

---

## ✅ 验证清单

完成后请检查：

- [ ] **admin 用户可以 SSH 登录**
  ```powershell
  ssh admin@39.106.41.239
  ```

- [ ] **可以切换到 root**
  ```bash
  sudo su -
  # 输入 admin 密码后应进入 root shell
  ```

- [ ] **家目录存在**
  ```bash
  ls -la /home/admin/
  ```

- [ ] **没有其他进程占用**
  ```bash
  ps -u admin
  # 应该只有当前登录的 session
  ```

---

## 🐛 常见问题

### Q: 杀死进程后立即又有新进程？

**A:** 可能有 systemd 服务或 cron 任务在使用 admin 用户

**解决：**
```bash
# 查看是否有 systemd 服务
systemctl list-units --all | grep admin

# 查看 crontab
crontab -l

# 如果是登录会话，退出即可
exit
```

### Q: userdel 仍然报错？

**A:** 可能文件被锁定

**解决：**
```bash
# 强制删除（慎用）
userdel -f admin

# 或者手动删除
rm -rf /home/admin
sed -i '/^admin:/d' /etc/passwd
sed -i '/^admin:/d' /etc/shadow
sed -i '/^admin:/d' /etc/group
```

### Q: 忘记密码怎么办？

**A:** 作为 root 可以随时重置

```bash
passwd admin
# 输入新密码
```

---

## 📝 下一步

成功创建 admin 用户后：

1. **立即测试 SSH 登录**
   ```powershell
   ssh admin@39.106.41.239
   ```

2. **修复 Django Admin**
   ```bash
   cd /var/www/eims
   source venv/bin/activate
   
   # 上传修复后的 settings.py
   python manage.py collectstatic --clear --noinput
   python manage.py collectstatic --noinput
   
   sudo supervisorctl restart eims
   ```

---

**文档创建时间：** 2026-04-02  
**适用场景：** admin 用户被进程占用无法删除的情况
