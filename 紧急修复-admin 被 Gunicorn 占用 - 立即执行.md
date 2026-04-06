# 紧急修复：admin 被 Gunicorn 占用 - 立即执行版

## 🚨 您的当前情况

**问题：** admin 用户有 4 个 gunicorn 进程（PID: 5990, 5991, 5992, 7770）  
**影响：** 无法删除和重建 admin 用户

---

## ⚡ 最快解决方案（复制粘贴到 VNC）

### 方法 1：一键自动脚本（推荐）⭐⭐⭐⭐⭐

**复制以下内容到 VNC 窗口：**

```bash
cat > /tmp/quick_fix_admin.sh << 'EOF'
#!/bin/bash
echo "======================================"
echo "快速修复：admin 被 Gunicorn 占用"
echo "======================================"
USERNAME="admin"

# 停止 supervisor
echo "🛑 正在停止 Supervisor..."
systemctl stop supervisord 2>/dev/null || supervisorctl stop all 2>/dev/null
sleep 2

# 杀死所有 gunicorn 进程
echo "🔪 正在杀死 Gunicorn 进程..."
pkill -9 gunicorn
sleep 2

# 验证
echo "🔍 验证进程状态..."
ps -u "$USERNAME" 2>/dev/null || echo "✅ 没有发现进程"

# 强制删除
echo "🗑️  正在删除用户..."
userdel -f "$USERNAME" 2>/dev/null
rm -rf /home/"$USERNAME"
sed -i "/^${USERNAME}:/d" /etc/passwd 2>/dev/null
sed -i "/^${USERNAME}:/d" /etc/shadow 2>/dev/null
sed -i "/^${USERNAME}:/d" /etc/group 2>/dev/null

# 重新创建
echo "🆕 创建新用户..."
useradd -m -s /bin/bash "$USERNAME"

# 设置密码
echo "🔐 请设置密码（输入两次）："
passwd "$USERNAME"

# 添加权限
usermod -aG wheel "$USERNAME"
su - "$USERNAME" -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"

# 启动 supervisor
systemctl start supervisord

echo ""
echo "✅ 完成！"
echo "SSH: ssh admin@39.106.41.239"
EOF

chmod +x /tmp/quick_fix_admin.sh
/tmp/quick_fix_admin.sh
```

---

### 方法 2：手动快速执行

**按顺序执行以下命令：**

```bash
# 1. 停止 supervisor（防止进程重启）
systemctl stop supervisord

# 2. 杀死所有 gunicorn 进程
pkill -9 gunicorn

# 3. 等待 2 秒
sleep 2

# 4. 验证没有 admin 用户的进程
ps -u admin
# 应该没有任何输出

# 5. 强制删除用户
userdel -f admin

# 6. 如果失败，手动清理
rm -rf /home/admin
grep -v '^admin:' /etc/passwd > /tmp/passwd.new && mv /tmp/passwd.new /etc/passwd
grep -v '^admin:' /etc/shadow > /tmp/shadow.new && mv /tmp/shadow.new /etc/shadow
grep -v '^admin:' /etc/group > /tmp/group.new && mv /tmp/group.new /etc/group

# 7. 重新创建
useradd -m -s /bin/bash admin

# 8. 设置密码（输入两次）
passwd admin

# 9. 添加 sudo 权限
usermod -aG wheel admin

# 10. 配置 SSH
su - admin -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"

# 11. 启动 supervisor
systemctl start supervisord

echo ""
echo "✅ 完成！SSH: ssh admin@39.106.41.239"
```

---

## 📋 详细步骤说明

### 为什么需要停止 Supervisor？

Supervisor 是进程管理器，会自动重启 Gunicorn 进程。如果不停止它：
- 杀死一个进程，它会立即重启一个新的
- 导致永远无法完全清除所有进程

### 完整流程：

1. **停止 Supervisor** → 防止进程自动重启
2. **杀死所有 Gunicorn** → 清理占用进程
3. **验证无进程** → 确保可以删除
4. **强制删除** → 清理旧用户
5. **重新创建** → 新建可用用户
6. **启动 Supervisor** → 恢复服务运行

---

## ✅ 验证清单

完成后请立即测试：

### 测试 1：SSH 登录

**打开本地 PowerShell（不要关闭 VNC）：**
```powershell
ssh admin@39.106.41.239
```

**成功标志：**
```
[admin@iZ2ze74hagmo3egfxeffrcZ ~]$
```

### 测试 2：sudo 权限

```bash
sudo whoami
# 应输出：root
```

### 测试 3：服务状态

```bash
sudo systemctl status supervisord
# 应该是 active (running)

sudo supervisorctl status
# 应该显示 eims: RUNNING
```

---

## 🐛 如果仍然失败

### 情况 1：还有进程存在

**解决：**
```bash
# 查看是什么进程
ps aux | grep admin

# 如果是 systemd 服务
systemctl list-units --all | grep admin

# 强制杀死
pkill -KILL -u admin
```

### 情况 2：文件锁死

**解决：**
```bash
# 检查文件系统
mount | grep "on / "

# 如果是只读，重新挂载
mount -o remount,rw /
```

### 情况 3：密码设置失败

**可能原因：** 密码太简单

**解决：**
```bash
# 使用复杂密码
# 例如：Admin@20260402
passwd admin
```

---

## 📝 下一步：修复 Django Admin

成功创建 admin 用户后，继续修复 Django Admin 显示问题：

### 快速修复流程

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

# 访问测试
# http://39.106.41.239/admin/
```

---

## 🔧 相关文档

我已经为您创建了完整的故障排除文档：

- **[`彻底解决-admin 被 Gunicorn 占用.md`](file://e:\EIMS2026\彻底解决-admin 被 Gunicorn 占用.md)** - 完整技术方案 ⭐⭐⭐⭐⭐
- **[`bat\快速修复-admin 被 Gunicorn 占用.sh`](file://e:\EIMS2026\bat\快速修复-admin 被 Gunicorn 占用.sh)** - 自动化脚本
- **[`紧急解决-admin 用户被进程占用.md`](file://e:\EIMS2026\紧急解决-admin 用户被进程占用.md)** - 快速解决方案

---

## 🎓 知识点总结

### Gunicorn 进程说明

```
supervisord (管理进程)
  └─ gunicorn (master process)
      ├─ gunicorn worker 1 (PID 5990)
      ├─ gunicorn worker 2 (PID 5991)
      ├─ gunicorn worker 3 (PID 5992)
      └─ gunicorn worker 4 (PID 7770)
```

这些进程都以 admin 用户身份运行，所以会占用用户。

### 正确的解决顺序

1. ✅ 先停止 Supervisor（管理者）
2. ✅ 再杀死工作进程
3. ✅ 最后删除用户

**错误做法：**
- ❌ 直接杀死进程（Supervisor 会重启它们）
- ❌ 只停止部分进程
- ❌ 不验证就删除

---

**文档创建时间：** 2026-04-02  
**适用场景：** admin 用户被 Gunicorn/Django 进程占用  
**预计用时：** 2-3 分钟
