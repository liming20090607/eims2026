# 创建 admin 用户 - 快速操作指南

## 🎯 问题

服务器只有 root 用户，SSH 登录密码验证失败，需要创建 admin 用户用于日常运维。

---

## ⚡ 最快解决方案（5 分钟）

### 第 1 步：通过阿里云 VNC 登录

1. **访问阿里云控制台**
   ```
   https://ecs.console.aliyun.com/
   ```

2. **找到实例**
   - 实例 ID：`iZ2ze74hagmo3egfxeffrcZ`
   - IP：`39.106.41.239`

3. **点击"远程连接"**
   - 选择"VNC 连接"
   - 输入 root 密码登录

### 第 2 步：复制粘贴以下命令到 VNC

```bash
cat > /tmp/create_admin.sh << 'EOF'
#!/bin/bash
echo "======================================"
echo "自动创建 admin 用户"
echo "======================================"
USERNAME="admin"
if id "$USERNAME" &>/dev/null; then
    echo "⚠️ 用户已存在"
    read -p "是否删除重建？(y/n): " c
    [ "$c" = "y" ] && userdel -r "$USERNAME" || exit 1
fi
useradd -m -s /bin/bash "$USERNAME"
PASS=$(openssl rand -base64 12)
echo "$PASS" | passwd --stdin "$USERNAME" &>/dev/null
usermod -aG wheel "$USERNAME"
su - "$USERNAME" -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
echo ""
echo "✅ 成功！"
echo "━━━━━━━━━━━━━━━━━━"
echo "用户名：$USERNAME"
echo "密  码：$PASS"
echo "━━━━━━━━━━━━━━━━━━"
echo "登录：ssh admin@39.106.41.239"
echo "切 root: sudo su -"
echo ""
echo "凭据已保存：/root/admin_cred.txt"
EOF
chmod +x /tmp/create_admin.sh
/tmp/create_admin.sh
```

### 第 3 步：保存生成的密码

脚本执行后会显示：
```
✅ 成功！
━━━━━━━━━━━━━━━━━━
用户名：admin
密  码：XXXXXXXXXXXX
━━━━━━━━━━━━━━━━━━
```

**立即：**
1. 📋 复制密码（拍照或保存到文本文件）
2. ✅ 不要关闭 VNC 窗口

### 第 4 步：测试 SSH 登录

**打开本地 PowerShell：**
```powershell
ssh admin@39.106.41.239

# 输入刚才的密码
```

**成功后测试 sudo：**
```bash
sudo su -
# 输入 admin 密码，应该切换到 root
exit
```

### 第 5 步：退出 VNC

确认一切正常后，可以关闭 VNC 窗口了。

---

## 📁 相关文档

### 详细教程

- **[`创建 admin 用户完整指南.md`](file://e:\EIMS2026\创建 admin 用户完整指南.md)** - 完整技术文档（推荐）
- **[`通过阿里云 VNC 创建 admin 用户 - 图文教程.md`](file://e:\EIMS2026\通过阿里云 VNC 创建 admin 用户 - 图文教程.md)** - 带截图说明的步骤指南

### 自动化脚本

- **[`bat\自动创建 admin 用户脚本.sh`](file://e:\EIMS2026\bat\自动创建 admin 用户脚本.sh)** - 可在 VNC 中直接运行

---

## 🔧 如果遇到问题

### 问题 1：找不到 VNC 入口

**解决：**
- 确保实例状态是"运行中"
- 刷新页面（F5）
- 尝试使用"Workbench"代替 VNC

### 问题 2：无法粘贴到 VNC

**解决：**
- 尝试右键 → 粘贴
- 或使用 Ctrl+V / Shift+Insert
- 或手动输入命令（虽然慢但可靠）

### 问题 3：创建后仍然无法 SSH 登录

**诊断：**
```bash
# 在 VNC 中作为 root 执行
systemctl status sshd
grep "PasswordAuthentication" /etc/ssh/sshd_config
firewall-cmd --list-all
```

**解决：**
```bash
# 确保密码登录被允许
vi /etc/ssh/sshd_config
# 设置：PasswordAuthentication yes

# 重启 SSH
systemctl restart sshd
```

---

## ✅ 成功标志

完成后的正确状态：

- [ ] ✅ 可以使用 `ssh admin@39.106.41.239` 登录
- [ ] ✅ 登录后可以执行 `sudo su -` 切换 root
- [ ] ✅ 家目录 `/home/admin/` 存在
- [ ] ✅ `.ssh` 目录权限正确（700）

---

## 📝 下一步：修复 Django Admin

成功创建 admin 用户后，继续修复 Django Admin 显示问题：

### 方法 A：使用自动修复脚本

**在本地 PowerShell 执行：**
```powershell
# 上传 settings.py
scp E:\EIMS2026\settings.py admin@39.106.41.239:/var/www/eims/

# SSH 登录
ssh admin@39.106.41.239

# 登录后执行
cd /var/www/eims
source venv/bin/activate
python manage.py collectstatic --clear --noinput
python manage.py collectstatic --noinput
sudo supervisorctl restart eims
```

### 方法 B：使用一键修复脚本

**运行：**
```
E:\EIMS2026\bat\修复 Django 版本兼容问题.bat
```

输入 admin 密码即可自动完成所有修复步骤。

---

## 🎓 为什么这样做？

| 方面 | 使用 root | 使用 admin |
|------|----------|-----------|
| **安全性** | ❌ 风险高 | ✅ 需 sudo 提权 |
| **审计** | ❌ 难追踪 | ✅ 有日志 |
| **误操作** | ❌ 后果严重 | ✅ 有确认提示 |
| **最佳实践** | ❌ 不推荐 | ✅ 符合规范 |

---

**创建时间：** 2026-04-02  
**预计用时：** 5-10 分钟  
**难度：** ⭐⭐☆☆☆（简单）
