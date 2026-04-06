# 通过阿里云 VNC 创建 admin 用户 - 图文教程

## 🎯 目标

使用 root 用户通过阿里云控制台 VNC 登录服务器，创建 admin 用户用于日常 SSH 登录。

---

## ⚡ 操作步骤（5 分钟完成）

### 步骤 1：登录阿里云控制台

1. **访问阿里云**
   ```
   https://ecs.console.aliyun.com/
   ```

2. **登录账号**
   - 输入您的阿里云账号和密码
   - 完成验证码验证

---

### 步骤 2：找到您的 ECS 实例

1. **在左侧菜单选择**
   ```
   实例与镜像 → 实例
   ```

2. **选择地域**
   - 如果您的实例在北京，选择"华北 2（北京）"
   - 根据实际购买地域选择

3. **找到实例**
   - 实例 ID：`iZ2ze74hagmo3egfxeffrcZ`
   - IP 地址：`39.106.41.239`
   - 状态应该是"运行中"

---

### 步骤 3：远程连接 VNC

1. **点击"远程连接"按钮**
   - 在实例操作列
   - 点击"远程连接"

2. **选择连接方式**
   - 选择"VNC 连接"或"Workbench"
   - 首次使用可能需要设置 VNC 密码

3. **输入 VNC 密码**
   - 如果是第一次使用，系统会提示您设置 VNC 密码
   - 记住这个密码，下次还要用

4. **成功进入服务器桌面**
   - 应该看到类似 Linux 命令行界面
   - 显示类似：`[root@iZ2ze74hagmo3egfxeffrcZ ~]#`

---

### 步骤 4：执行自动创建脚本

**方法 A：一键复制粘贴（推荐）** ⭐⭐⭐⭐⭐

**复制以下完整内容：**
```bash
curl -o /tmp/create_admin.sh https://raw.githubusercontent.com/your-repo/scripts/main/create_admin.sh && bash /tmp/create_admin.sh
```

或者使用本地脚本：

**复制以下内容到 VNC 窗口：**

```bash
cat > /root/create_admin_user.sh << 'SCRIPT_END'
#!/bin/bash
echo "======================================"
echo "自动创建 admin 用户"
echo "======================================"
USERNAME="admin"
if id "$USERNAME" &>/dev/null; then
    echo "⚠️ 用户已存在，删除并重新创建..."
    userdel -r "$USERNAME"
fi
useradd -m -s /bin/bash "$USERNAME"
RANDOM_PASS=$(openssl rand -base64 12)
echo "$RANDOM_PASS" | passwd --stdin "$USERNAME" &>/dev/null
usermod -aG wheel "$USERNAME"
su - "$USERNAME" -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
echo ""
echo "✅ 创建成功！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "用户名：$USERNAME"
echo "密  码：$RANDOM_PASS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SSH 登录：ssh admin@39.106.41.239"
echo "切换 root: sudo su -"
echo ""
SCRIPT_END

chmod +x /root/create_admin_user.sh
/root/create_admin_user.sh
```

**如何复制粘贴到 VNC：**
1. 选中上面的所有代码（从 `cat` 到最后一行）
2. 按 `Ctrl+C` 复制
3. 在 VNC 窗口中右键点击，选择"粘贴"
4. 或直接按 `Ctrl+V` 或 `Shift+Insert`
5. 按回车执行

---

**方法 B：手动逐步执行**

如果您想手动一步步来：

```bash
# 第 1 步：创建用户
useradd -m -s /bin/bash admin

# 第 2 步：设置密码
passwd admin
# 输入两次密码（不显示字符）

# 第 3 步：添加 sudo 权限
usermod -aG wheel admin

# 第 4 步：验证
id admin
# 应显示：groups=1001(admin),10(wheel)

# 第 5 步：配置 SSH
su - admin
mkdir -p ~/.ssh
chmod 700 ~/.ssh
exit

# 第 6 步：测试
ssh admin@localhost
# 输入刚才设置的密码
```

---

### 步骤 5：保存生成的密码

**脚本执行成功后会显示：**
```
✅ 创建成功！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用户名：admin
密  码：AbC123XyZ!@# (示例，实际是随机密码)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SSH 登录：ssh admin@39.106.41.239
切换 root: sudo su -
```

**立即做以下事情：**
1. ✅ **复制密码**（用手机拍照或复制到文本文件）
2. ✅ **保存到安全地方**（密码管理器或加密文件）
3. ✅ **不要关闭 VNC 窗口**（先测试登录）

---

### 步骤 6：测试 SSH 登录

**不要关闭 VNC 窗口**，在本地 PowerShell 中测试：

```powershell
# 打开新的 PowerShell 窗口
ssh admin@39.106.41.239

# 输入刚才保存的密码
```

**如果成功登录，会看到：**
```
[admin@iZ2ze74hagmo3egfxeffrcZ ~]$
```

**测试切换到 root：**
```bash
sudo su -

# 输入 admin 密码
# 应该看到：[root@iZ2ze74hagmo3egfxeffrcZ ~]#
```

---

### 步骤 7：退出 VNC

确认 SSH 登录成功后：

**在 VNC 中输入：**
```bash
exit
```

或直接关闭浏览器标签页

---

## ✅ 验证清单

完成后请逐一检查：

- [ ] **admin 用户已创建**
  ```powershell
  ssh admin@39.106.41.239
  # 能成功登录
  ```

- [ ] **sudo 权限正常**
  ```bash
  sudo su -
  # 输入密码后能切换到 root
  ```

- [ ] **家目录存在**
  ```bash
  ls -la /home/admin/
  # 应该有 .ssh, .bashrc 等文件
  ```

- [ ] **可以上传修复脚本**
  ```powershell
  scp E:\EIMS2026\bat\修复 Django 版本兼容问题.bat admin@39.106.41.239:/home/admin/
  ```

---

## 🐛 常见问题解决

### 问题 1：找不到"远程连接"按钮

**解决：**
1. 确认实例状态是"运行中"
2. 刷新页面（F5）
3. 检查是否有权限（子账号可能需要授权）
4. 尝试使用"Workbench"代替 VNC

---

### 问题 2：VNC 连接黑屏

**解决：**
1. 按几下回车键激活屏幕
2. 等待几秒让系统加载
3. 如果仍然黑屏，关闭重连
4. 检查实例是否正常运行

---

### 问题 3：无法粘贴到 VNC

**解决：**
1. 尝试不同的粘贴方式：
   - 右键 → 粘贴
   - Ctrl+V
   - Shift+Insert
2. 如果使用 Workbench，直接拖拽文件进去
3. 或者手动输入命令（虽然慢但可靠）

---

### 问题 4：创建用户失败

**错误：** `useradd: user already exists`

**解决：**
```bash
# 删除现有用户
userdel -r admin

# 重新创建
useradd -m -s /bin/bash admin
passwd admin
usermod -aG wheel admin
```

---

### 问题 5：密码设置失败

**错误：** `passwd: Authentication token manipulation error`

**解决：**
```bash
# 检查文件系统是否只读
mount | grep "on / "

# 如果是只读，重新挂载为读写
mount -o remount,rw /

# 再次尝试设置密码
passwd admin
```

---

## 🔒 安全建议（可选但推荐）

### 1. 禁用 root SSH 直接登录

**在 VNC 中执行：**
```bash
# 编辑 SSH 配置
vi /etc/ssh/sshd_config

# 找到这行并修改
PermitRootLogin no

# 重启 SSH 服务
systemctl restart sshd
```

### 2. 修改 SSH 端口

```bash
# 编辑 sshd_config
vi /etc/ssh/sshd_config

# 添加或修改
Port 2222

# 重启 SSH
systemctl restart sshd

# 以后登录使用
ssh -p 2222 admin@39.106.41.239
```

### 3. 安装 fail2ban

```bash
yum install epel-release -y
yum install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

---

## 📝 下一步：修复 Django Admin

成功创建 admin 用户后，您可以：

### 1. 上传修复后的 settings.py

**在本地 PowerShell 执行：**
```powershell
scp E:\EIMS2026\settings.py admin@39.106.41.239:/var/www/eims/

# 输入 admin 密码
```

### 2. SSH 登录并执行修复

```bash
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
```

### 3. 验证修复

访问：`http://39.106.41.239/admin/`
按 `Ctrl+F5` 强制刷新

---

## 🎓 知识点总结

### VNC vs SSH

| 特性 | VNC | SSH |
|------|-----|-----|
| **用途** | 图形化远程桌面 | 命令行远程登录 |
| **安全性** | 较低 | 较高 |
| **速度** | 较慢 | 较快 |
| **日常使用** | 仅紧急维护 | 推荐日常运维 |

### 为什么创建 admin 用户？

1. ✅ **提高安全性** - 避免直接使用 root
2. ✅ **审计追踪** - sudo 有日志记录
3. ✅ **防止误操作** - 需要确认才能提权
4. ✅ **最佳实践** - 符合 Linux 安全规范

---

## 📞 需要帮助？

如果遇到问题：

1. **截图 VNC 中的错误信息**
2. **记录执行的命令和输出**
3. **检查阿里云控制台实例状态**
4. **查看相关文档**：
   - `创建 admin 用户完整指南.md`
   - `SSH 登录问题 - 快速解决指南.md`

---

**文档创建时间：** 2026-04-02  
**适用场景：** 阿里云 ECS CentOS/Alibaba Cloud Linux  
**预计用时：** 5-10 分钟
