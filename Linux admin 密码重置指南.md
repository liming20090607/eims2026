# Linux admin 账号密码重置指南

## 📋 密码格式要求

### 阿里云 Linux 系统密码规则

| 要求 | 说明 |
|------|------|
| **长度** | 8-30 个字符 |
| **必须包含** | 大写字母（A-Z） |
| **必须包含** | 小写字母（a-z） |
| **必须包含** | 数字（0-9） |
| **必须包含** | 特殊字符（至少一个） |
| **允许的特殊字符** | `()~!@#$%^&*-_+=\|;:.:/?` |
| **不能包含** | 用户名（admin）的倒序或正序 |

### ✅ 密码示例

**符合要求的密码：**
- `Admin@2026`
- `Eims#1234`
- `Server$2026`
- `MyLinux@888`

**不符合要求的密码：**
- `admin123` ❌（包含用户名，无大写字母和特殊字符）
- `password` ❌（太简单，无大写和数字）
- `Admin2026` ❌（缺少特殊字符）
- `12345678` ❌（太简单）

---

## 🚀 密码重置方法

### 方法一：使用 root 用户重置（如果您还能登录 root）

#### 步骤 1：SSH 登录 root
```bash
ssh root@39.106.41.239
```

#### 步骤 2：重置 admin 密码
```bash
sudo passwd admin
```

#### 步骤 3：按提示输入新密码
```
New password:      # 输入新密码（不显示）
Retype new password: # 再次输入确认
```

#### 步骤 4：验证
```bash
# 退出 root
exit

# 使用 admin 登录测试
ssh admin@39.106.41.239
```

---

### 方法二：通过阿里云控制台重置（推荐）

#### 步骤 1：登录阿里云控制台

1. 访问：https://www.aliyun.com/
2. 登录您的阿里云账号
3. 进入 **控制台**

#### 步骤 2：找到 ECS 实例

1. 点击左侧菜单：**云服务器 ECS**
2. 在实例列表中找到：`39.106.41.239`
3. 点击实例 ID 进入详情页

#### 步骤 3：重置密码

**方式 A：使用 VNC 登录（如果 root 还能登录）**

1. 点击 **远程连接**
2. 选择 **VNC 登录**
3. 输入 root 密码登录
4. 执行命令：`passwd admin`

**方式 B：重置 root 密码（如果 root 也忘记了）**

1. 点击 **更多** → **密码/密钥** → **重置实例密码**
2. 输入新的 root 密码（符合上述格式要求）
3. 点击 **确认**
4. **重启实例**使密码生效

#### 步骤 4：重启实例（如果使用了方式 B）

1. 点击 **重启**
2. 确认重启
3. 等待 2-3 分钟直到服务器完全启动

#### 步骤 5：登录并重置 admin 密码

```bash
# 使用新 root 密码登录
ssh root@39.106.41.239

# 重置 admin 密码
passwd admin

# 输入新密码（两次）
```

---

### 方法三：单用户模式重置（高级用户）

⚠️ **警告：** 此方法需要重启服务器，可能导致服务中断，仅在其他方法无效时使用。

#### 步骤 1：通过阿里云 VNC 登录

1. 阿里云控制台 → ECS → 实例详情
2. 点击 **远程连接** → **VNC 登录**
3. 重启服务器

#### 步骤 2：进入 GRUB 菜单

在启动时快速按 `Esc` 或 `Shift` 键进入 GRUB 菜单

#### 步骤 3：编辑启动参数

1. 选择当前内核（通常是第一个）
2. 按 `e` 编辑启动参数
3. 找到以 `linux16` 或 `linux` 开头的行
4. 在行尾添加：`rd.break` 或 `init=/bin/bash`
5. 按 `Ctrl+X` 启动

#### 步骤 4：重新挂载并重置密码

```bash
# 重新挂载根目录为读写
mount -o remount,rw /sysroot

# 切换到根目录
chroot /sysroot

# 重置密码
passwd admin

# 输入新密码（两次）

# 创建重标记文件（SELinux）
touch /.autorelabel

# 退出
exit
exit
```

#### 步骤 5：等待系统重启

系统会自动重启，等待 SELinux 重新标记完成（可能需要几分钟）

---

## 🔧 使用脚本自动重置

### 创建重置脚本（本地）

我已为您创建脚本：

文件位置：[`bat\重置 admin 密码.sh`](file://e:\EIMS2026\bat\重置 admin 密码.sh)

```bash
#!/bin/bash
# 此脚本需要在服务器上以 root 身份执行

echo "======================================"
echo "重置 Linux admin 账号密码"
echo "======================================"
echo ""

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 错误：请使用 root 用户运行此脚本"
    exit 1
fi

# 提示输入新密码
read -s -p "请输入新密码：" password
echo ""
read -s -p "确认密码：" password2
echo ""

# 验证密码
if [ "$password" != "$password2" ]; then
    echo "❌ 两次输入的密码不一致！"
    exit 1
fi

if [ ${#password} -lt 8 ]; then
    echo "❌ 密码长度至少 8 位！"
    exit 1
fi

# 检查密码复杂度
if ! [[ "$password" =~ [A-Z] ]]; then
    echo "❌ 密码必须包含大写字母！"
    exit 1
fi

if ! [[ "$password" =~ [a-z] ]]; then
    echo "❌ 密码必须包含小写字母！"
    exit 1
fi

if ! [[ "$password" =~ [0-9] ]]; then
    echo "❌ 密码必须包含数字！"
    exit 1
fi

if ! [[ "$password" =~ [[:punct:]] ]]; then
    echo "❌ 密码必须包含特殊字符！"
    exit 1
fi

echo ""
echo "✅ 密码格式验证通过"
echo ""

# 重置密码
echo "$password" | passwd --stdin admin

if [ $? -eq 0 ]; then
    echo "✅ admin 账号密码重置成功！"
    echo ""
    echo "新密码：$password"
    echo ""
    echo "测试登录：ssh admin@39.106.41.239"
else
    echo "❌ 密码重置失败！"
fi
```

### 使用方法

#### 步骤 1：上传脚本
```powershell
# 在本地 PowerShell 执行
scp E:\EIMS2026\bat\重置 admin 密码.sh root@39.106.41.239:/tmp/
```

#### 步骤 2：SSH 登录 root
```bash
ssh root@39.106.41.239
```

#### 步骤 3：执行脚本
```bash
sudo bash /tmp/重置\ admin\ 密码.sh
```

---

## ✅ 验证密码重置成功

### 测试 1：本地 PowerShell 测试

```powershell
# Windows PowerShell
ssh admin@39.106.41.239
# 输入新密码
```

### 测试 2：使用脚本测试

我已创建测试脚本：[`bat\测试 SSH 登录.bat`](file://e:\EIMS2026\bat\测试 SSH 登录.bat)

```batch
@echo off
echo 正在测试 SSH 登录...
ssh admin@39.106.41.239
pause
```

### 测试 3：检查账号状态

```bash
# SSH 登录后
sudo su -

# 检查账号信息
id admin

# 检查密码过期时间
chage -l admin

# 检查账号是否锁定
passwd -S admin
```

**正常输出：**
```
uid=1001(admin) gid=1001(admin) groups=1001(admin),10(wheel)
Password expires: never
Password set: 2026-04-03
```

---

## 🔍 常见问题

### Q1: 为什么密码总是提示错误？

**可能原因：**
1. 密码格式不符合要求
2. 两次输入不一致
3. 键盘布局问题（大小写锁定）
4. 特殊字符转义问题

**解决方法：**
- 使用简单但符合要求的密码，如：`Admin@2026`
- 确保两次输入完全一致
- 检查 CapsLock 是否关闭

### Q2: 使用 `passwd --stdin admin` 报错

**错误信息：**
```
passwd: Authentication token manipulation error
```

**原因：** 密码太简单或不符合系统策略

**解决方法：**
```bash
# 方法 1：使用交互式 passwd
passwd admin

# 方法 2：使用 chpasswd
echo "admin:NewPassword@2026" | chpasswd

# 方法 3：临时禁用密码策略
passwd -d admin  # 删除密码
passwd admin     # 设置新密码
```

### Q3: 忘记 root 密码怎么办？

**解决方法：**
1. 使用阿里云控制台的 **重置实例密码** 功能
2. 重置 root 密码
3. 重启服务器
4. 登录后再重置 admin 密码

### Q4: 密码设置后还是登录不上？

**检查清单：**
- [ ] SSH 服务是否正常运行：`systemctl status sshd`
- [ ] 防火墙是否开放 22 端口
- [ ] 阿里云安全组是否开放 22 端口
- [ ] 账号是否被锁定：`passwd -S admin`
- [ ] SSH 配置是否允许密码登录：`/etc/ssh/sshd_config`

---

## 📊 密码管理最佳实践

### 密码复杂度建议

| 级别 | 要求 | 示例 |
|------|------|------|
| **基础** | 8 位，包含大小写、数字、特殊字符 | `Admin@123` |
| **推荐** | 12 位，随机组合 | `Eims#2026@Safe` |
| **高安全** | 16 位以上，完全随机 | `Kj8#mN2$pL5@qR9!` |

### 密码存储建议

1. **使用密码管理器**
   - KeePass
   - 1Password
   - LastPass
   - Bitwarden

2. **记录在安全位置**
   - 加密的文档
   - 物理笔记本（妥善保管）

3. **不要：**
   - ❌ 明文保存在电脑桌面
   - ❌ 通过微信/QQ 发送
   - ❌ 告诉多人

### 定期更换密码

- **建议周期：** 每 3-6 个月
- **强制更换：** 怀疑泄露时立即更换
- **检查命令：**
  ```bash
  # 查看密码策略
  cat /etc/login.defs | grep PASS
  
  # 查看账号密码信息
  chage -l admin
  ```

---

## 🛡️ 安全建议

### 1. 启用 SSH 密钥登录（更安全）

```bash
# 生成密钥（本地）
ssh-keygen -t rsa -b 4096

# 上传公钥到服务器
ssh-copy-id admin@39.106.41.239

# 禁用密码登录（可选）
sudo nano /etc/ssh/sshd_config
# 修改：PasswordAuthentication no
sudo systemctl restart sshd
```

### 2. 修改 SSH 端口（减少扫描）

```bash
# 修改 SSH 配置
sudo nano /etc/ssh/sshd_config
# 修改：Port 2222

# 重启 SSH
sudo systemctl restart sshd

# 更新阿里云安全组
# 添加端口 2222，关闭端口 22
```

### 3. 安装失败限制

```bash
# 安装 fail2ban
sudo yum install fail2ban -y

# 启动服务
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

---

## 📞 需要帮助？

如果以上方法都无法解决，请提供：

1. **当前使用的重置方法**
2. **完整的错误信息**
3. **密码格式（脱敏，如：A****@2026）**
4. **是否使用 root 登录**
5. **阿里云控制台截图**

---

**最后更新：** 2026-04-03  
**适用系统：** Alibaba Cloud Linux / CentOS 7+  
**账号：** admin (uid=1001)
