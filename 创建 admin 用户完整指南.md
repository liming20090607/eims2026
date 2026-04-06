# 在服务器上创建 admin 用户 - 完整指南

## 🎯 问题背景

**当前情况：**
- 服务器只有 root 用户
- 想创建 admin 用户用于日常运维
- 提高安全性（避免直接使用 root）

---

## ⚡ 快速操作步骤

### 方法 1：通过阿里云控制台 VNC 登录创建（推荐）⭐⭐⭐⭐⭐

#### 步骤 1：通过 VNC 登录服务器

1. **访问阿里云控制台**
   ```
   https://ecs.console.aliyun.com/
   ```

2. **找到您的实例**
   - 实例 ID：`iZ2ze74hagmo3egfxeffrcZ`
   - IP 地址：`39.106.41.239`

3. **点击"远程连接"**
   - 选择"VNC 连接"或"Workbench"
   - 输入 root 密码
   - 成功登录后进入命令行界面

#### 步骤 2：创建 admin 用户（复制粘贴以下命令）

```bash
# 1. 创建 admin 用户
useradd -m -s /bin/bash admin

# 2. 设置 admin 用户密码
passwd admin
# 系统会提示您输入两次密码

# 3. 将 admin 添加到 wheel 组（CentOS/Alibaba Cloud Linux）
usermod -aG wheel admin

# 4. 或者添加到 sudo 组（Ubuntu/Debian）
# usermod -aG sudo admin

# 5. 验证 sudoers 配置
visudo
# 确保有以下这行（通常默认就有）：
# %wheel ALL=(ALL) ALL

# 6. 查看创建的用户
id admin

# 7. 查看用户目录
ls -la /home/admin/
```

#### 步骤 3：测试 SSH 登录

**在本地 PowerShell 中测试：**
```powershell
# 使用新创建的 admin 用户登录
ssh admin@39.106.41.239

# 输入刚才设置的密码
```

**成功后切换到 root：**
```bash
# 登录后执行
sudo su -

# 输入 admin 用户的密码
# 应该能成功切换到 root
```

---

### 方法 2：使用自动化脚本一键创建

#### 创建自动创建脚本

**在 VNC 登录界面执行以下命令：**

```bash
# 复制整个脚本内容
cat > /root/create_admin_user.sh << 'EOF'
#!/bin/bash

echo "======================================"
echo "创建 admin 用户脚本"
echo "======================================"
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 错误：请使用 root 用户运行此脚本"
    exit 1
fi

# 设置用户名
USERNAME="admin"

# 检查用户是否已存在
if id "$USERNAME" &>/dev/null; then
    echo "⚠️  警告：用户 $USERNAME 已存在"
    read -p "是否删除并重新创建？(y/n): " confirm
    if [ "$confirm" = "y" ]; then
        userdel -r "$USERNAME"
        echo "✅ 已删除旧用户 $USERNAME"
    else
        echo "❌ 取消操作"
        exit 1
    fi
fi

# 创建用户
echo "正在创建用户 $USERNAME..."
useradd -m -s /bin/bash "$USERNAME"

if [ $? -eq 0 ]; then
    echo "✅ 用户创建成功"
else
    echo "❌ 用户创建失败"
    exit 1
fi

# 设置随机密码
RANDOM_PASS=$(openssl rand -base64 12)
echo "$RANDOM_PASS" | passwd --stdin "$USERNAME" &>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 密码设置成功"
else
    echo "❌ 密码设置失败"
    exit 1
fi

# 添加到 wheel 组（sudo 权限）
usermod -aG wheel "$USERNAME"

if [ $? -eq 0 ]; then
    echo "✅ 已添加到 wheel 组（sudo 权限）"
else
    echo "❌ 添加组失败"
    exit 1
fi

# 显示用户信息
echo ""
echo "======================================"
echo "✅ admin 用户创建成功！"
echo "======================================"
echo ""
echo "📋 登录信息："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "用户名：admin"
echo "密  码：$RANDOM_PASS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  重要提示："
echo "1. 请立即复制上面的密码"
echo "2. 首次登录后建议修改密码"
echo "3. 使用 'sudo su -' 切换 root"
echo ""
echo "🔧 登录命令："
echo "ssh admin@39.106.41.239"
echo ""

# 保存密码到文件（可选）
echo "用户名：admin" > /root/admin_credentials.txt
echo "密码：$RANDOM_PASS" >> /root/admin_credentials.txt
chmod 600 /root/admin_credentials.txt
echo "💾 凭据已保存到：/root/admin_credentials.txt"
echo ""

EOF

# 给脚本执行权限
chmod +x /root/create_admin_user.sh

# 运行脚本
/root/create_admin_user.sh
```

---

## 📋 手动创建详细步骤（逐步执行）

如果您想手动一步步执行，请按顺序运行以下命令：

### 1. 创建用户账户

```bash
# 创建用户并创建家目录
useradd -m -s /bin/bash admin

# 解释参数：
# -m : 创建家目录 (/home/admin)
# -s : 设置登录 shell (/bin/bash)
```

### 2. 设置密码

```bash
# 交互式设置密码（推荐）
passwd admin

# 或使用非交互式（适合脚本）
echo "您的密码" | passwd --stdin admin
```

### 3. 配置 sudo 权限

```bash
# 添加到 wheel 组（CentOS/Alibaba Cloud Linux）
usermod -aG wheel admin

# 验证组成员身份
groups admin

# 应该看到：admin : admin wheel
```

### 4. 验证 sudoers 配置

```bash
# 编辑 sudoers 文件
visudo

# 确保有以下行（通常第 83 行左右）：
# %wheel ALL=(ALL) ALL

# 如果注释了（前面有 #），删除 # 号
# 保存退出（:wq）
```

### 5. 测试 sudo 权限

```bash
# 切换到 admin 用户
su - admin

# 测试 sudo 权限
sudo whoami

# 应该输出：root
# 第一次使用会要求输入密码

# 返回 root 用户
exit
```

### 6. 创建 SSH 目录（可选但推荐）

```bash
# 切换到 admin 用户
su - admin

# 创建 .ssh 目录
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 创建 authorized_keys 文件（如果使用密钥登录）
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 返回 root
exit
```

---

## 🔐 安全加固建议

### 1. 禁用 root SSH 直接登录

**编辑 SSH 配置文件：**
```bash
vi /etc/ssh/sshd_config
```

**修改以下内容：**
```bash
# 找到这一行
PermitRootLogin yes

# 改为
PermitRootLogin no

# 或者允许密钥登录但不允许密码登录
PermitRootLogin prohibit-password
```

**重启 SSH 服务：**
```bash
systemctl restart sshd
```

### 2. 修改 SSH 端口（可选）

```bash
# 编辑 sshd_config
vi /etc/ssh/sshd_config

# 添加或修改
Port 2222

# 重启 SSH
systemctl restart sshd

# 登录时使用
ssh -p 2222 admin@39.106.41.239
```

### 3. 安装 fail2ban 防暴力破解

```bash
# 安装
yum install epel-release -y
yum install fail2ban -y

# 启动服务
systemctl enable fail2ban
systemctl start fail2ban

# 查看状态
systemctl status fail2ban
```

### 4. 配置防火墙（firewalld）

```bash
# 如果使用 firewalld
systemctl enable firewalld
systemctl start firewalld

# 开放 SSH 端口
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-port=8000/tcp

# 如果使用非标准 SSH 端口
# firewall-cmd --permanent --add-port=2222/tcp

# 重载配置
firewall-cmd --reload

# 查看规则
firewall-cmd --list-all
```

---

## ✅ 验证清单

创建完成后，请逐一验证：

### 基础验证

- [ ] admin 用户已创建
  ```bash
  id admin
  # 应显示：uid=1001(admin) gid=1001(admin) groups=1001(admin),10(wheel)
  ```

- [ ] 家目录存在
  ```bash
  ls -la /home/admin/
  # 应显示：total 20, drwx------, .bashrc, .bash_profile 等
  ```

- [ ] sudo 权限正常
  ```bash
  su - admin
  sudo whoami
  # 应输出：root
  ```

### SSH 登录验证

- [ ] 本地 SSH 登录成功
  ```powershell
  ssh admin@39.106.41.239
  ```

- [ ] 可以切换到 root
  ```bash
  sudo su -
  ```

- [ ] root 直接登录被禁止（如果已配置）
  ```powershell
  ssh root@39.106.41.239
  # 应显示：Permission denied
  ```

---

## 🐛 常见问题解决

### 问题 1：创建用户失败

**错误：** `useradd: user 'admin' already exists`

**解决：**
```bash
# 删除现有用户
userdel -r admin

# 重新创建
useradd -m -s /bin/bash admin
```

---

### 问题 2：sudo 权限不足

**错误：** `user is not in the sudoers file`

**解决：**
```bash
# 作为 root 执行
visudo

# 添加这行（如果不存在）
admin ALL=(ALL) ALL

# 或者添加到 wheel 组
usermod -aG wheel admin
```

---

### 问题 3：SSH 登录仍然失败

**可能原因：**
1. 密码错误
2. SSH 配置限制
3. 防火墙阻止

**诊断步骤：**
```bash
# 1. 检查 SSH 服务状态
systemctl status sshd

# 2. 检查 SSH 配置
grep -E "PasswordAuthentication|PermitRootLogin" /etc/ssh/sshd_config

# 3. 检查防火墙
firewall-cmd --list-all

# 4. 查看详细日志
tail -f /var/log/secure
```

---

### 问题 4：忘记密码

**解决：**
```bash
# 作为 root，重置 admin 密码
passwd admin

# 输入新密码两次
```

---

## 📝 后续操作建议

### 成功创建 admin 用户后：

1. **立即测试 SSH 登录**
   ```powershell
   ssh admin@39.106.41.239
   ```

2. **运行 Django Admin 修复脚本**
   ```bash
   # 上传修复后的 settings.py
   cd /var/www/eims
   
   # 激活虚拟环境
   source venv/bin/activate
   
   # 重新收集静态文件
   python manage.py collectstatic --clear --noinput
   python manage.py collectstatic --noinput
   
   # 重启服务
   sudo supervisorctl restart eims
   ```

3. **保存凭据**
   - 将 admin 密码保存在安全的地方
   - 考虑使用密码管理器

---

## 🎓 知识点总结

### 为什么使用普通用户而不是 root？

| 方面 | root 用户 | admin 用户 |
|------|----------|-----------|
| **安全性** | ❌ 风险高，完全权限 | ✅ 需要 sudo 提权 |
| **审计** | ❌ 难以追踪操作者 | ✅ sudo 有日志记录 |
| **误操作** | ❌ 容易误删系统文件 | ✅ 有确认提示 |
| **暴力破解** | ❌ 主要攻击目标 | ✅ 多一层保护 |

### Linux 用户管理命令

```bash
# 创建用户
useradd -m -s /bin/bash username

# 删除用户
userdel -r username

# 修改密码
passwd username

# 添加到组
usermod -aG groupname username

# 查看用户信息
id username

# 查看所有用户
cat /etc/passwd
```

---

**文档创建时间：** 2026-04-02  
**适用系统：** CentOS / Alibaba Cloud Linux  
**相关文档：** `SSH 登录问题 - 快速解决指南.md`
