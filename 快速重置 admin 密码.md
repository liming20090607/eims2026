# 快速重置 admin 密码

## 🎯 密码格式要求

### 必须满足的条件

| 要求 | 说明 | 示例 |
|------|------|------|
| **长度** | 8-30 个字符 | ✅ `Admin@2026` (10 位) |
| **大写字母** | 至少 1 个 A-Z | ✅ **A**dmin@2026 |
| **小写字母** | 至少 1 个 a-z | ✅ A**dmin**@2026 |
| **数字** | 至少 1 个 0-9 | ✅ Admin@202**6** |
| **特殊字符** | 至少 1 个 | ✅ Admin**@**2026 |
| **允许的特殊字符** | `()~!@#$%^&*-_+=\|;:.:/?` | ✅ |
| **不能包含** | admin（用户名） | ❌ Admin@2026 |

### ✅ 推荐密码示例

```
Admin@2026
Eims#1234
Server$2026
Linux@8888
Cloud#2026
MyServer@123
```

---

## 🚀 快速重置步骤

### 前提条件

您需要能够以 **root 用户** SSH 登录服务器。

### 步骤 1：上传脚本

在本地 PowerShell 执行：
```powershell
scp E:\EIMS2026\bat\重置 admin 密码.sh root@39.106.41.239:/tmp/
```

### 步骤 2：SSH 登录 root

```bash
ssh root@39.106.41.239
```

### 步骤 3：执行脚本

```bash
sudo bash /tmp/重置\ admin\ 密码.sh
```

### 步骤 4：按提示操作

1. 输入新密码（符合上述格式）
2. 确认密码
3. 等待验证和设置
4. 记录成功信息

### 步骤 5：测试登录

```bash
# 退出 root
exit

# 使用 admin 登录
ssh admin@39.106.41.239
```

---

## 🔧 手动重置（不使用脚本）

### 方法 1：交互式设置

```bash
# SSH 登录 root
ssh root@39.106.41.239

# 执行 passwd 命令
passwd admin

# 按提示输入密码
New password:      # 输入新密码
Retype new password: # 再次输入
```

### 方法 2：一行命令

```bash
# 使用 chpasswd（适合脚本）
echo "admin:YourPassword@123" | chpasswd
```

### 方法 3：标准输入

```bash
# 使用 --stdin（需要密码符合策略）
echo "YourPassword@123" | passwd --stdin admin
```

---

## 🛠️ 阿里云控制台重置（如果 root 也忘记了）

### 步骤 1：登录阿里云

访问：https://www.aliyun.com/

### 步骤 2：找到 ECS 实例

1. 控制台 → 云服务器 ECS
2. 找到实例：`39.106.41.239`
3. 点击实例 ID

### 步骤 3：重置实例密码

1. 点击 **更多** → **密码/密钥** → **重置实例密码**
2. 输入新的 root 密码
3. 点击 **确认**

### 步骤 4：重启实例

1. 点击 **重启**
2. 等待 2-3 分钟

### 步骤 5：登录并重置 admin

```bash
# 使用新 root 密码登录
ssh root@39.106.41.239

# 重置 admin 密码
passwd admin
```

---

## ✅ 验证成功

### 测试 1：SSH 登录

```bash
ssh admin@39.106.41.239
# 输入新密码
```

### 测试 2：检查账号状态

```bash
# SSH 登录后
sudo su -

# 查看账号信息
id admin

# 查看密码状态
passwd -S admin
```

**正常输出：**
```
uid=1001(admin) gid=1001(admin) groups=1001(admin),10(wheel)
Password set: 2026-04-03
Password expires: never
```

### 测试 3：PowerShell 测试

```powershell
Test-NetConnection 39.106.41.239 -Port 22
```

**预期：** `TcpTestSucceeded : True`

---

## 🔍 常见问题

### Q1: 密码总是提示错误

**原因：**
- 密码格式不符合要求
- 两次输入不一致
- 键盘大小写锁定

**解决：**
```bash
# 使用简单但符合要求的密码
# 例如：Admin@2026

# 确保关闭 CapsLock

# 使用 chpasswd 方法
echo "admin:Admin@2026" | chpasswd
```

### Q2: 提示 Authentication token manipulation error

**原因：** 密码太简单或系统策略限制

**解决：**
```bash
# 方法 1：使用更复杂的密码
echo "admin:Eims#Safe2026" | chpasswd

# 方法 2：临时禁用密码策略
passwd -d admin  # 删除密码
passwd admin     # 设置新密码

# 方法 3：检查 PAM 配置
cat /etc/pam.d/passwd
```

### Q3: 账号被锁定

**检查：**
```bash
passwd -S admin
```

**输出：** `admin L 2026-04-03 0 99999 7 -1`（L 表示锁定）

**解锁：**
```bash
# 解锁账号
passwd -u admin

# 或直接重置密码
passwd admin
```

### Q4: 忘记 root 密码

**解决：** 使用阿里云控制台重置

1. 阿里云控制台 → ECS
2. 实例详情 → 重置实例密码
3. 重启服务器
4. 使用新 root 密码登录

---

## 📊 密码管理建议

### 密码复杂度等级

| 等级 | 长度 | 复杂度 | 示例 |
|------|------|--------|------|
| **基础** | 8 位 | 大小写 + 数字 + 特殊字符 | `Admin@123` |
| **推荐** | 12 位 | 随机组合 | `Eims#2026@Safe` |
| **高安全** | 16 位 + | 完全随机 | `Kj8#mN2$pL5@qR9!` |

### 密码存储

**推荐：**
- ✅ 密码管理器（KeePass、1Password）
- ✅ 加密文档
- ✅ 物理笔记本（妥善保管）

**不要：**
- ❌ 明文保存在电脑
- ❌ 通过微信/QQ 发送
- ❌ 告诉多人

### 更换周期

- **建议：** 每 3-6 个月
- **立即更换：** 怀疑泄露时
- **检查命令：**
  ```bash
  chage -l admin
  ```

---

## 🛡️ 安全加固建议

### 1. 启用 SSH 密钥

```bash
# 本地生成密钥
ssh-keygen -t rsa -b 4096

# 上传公钥
ssh-copy-id admin@39.106.41.239

# 可选：禁用密码登录
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
sudo systemctl restart sshd
```

### 2. 修改 SSH 端口

```bash
sudo nano /etc/ssh/sshd_config
# Port 2222
sudo systemctl restart sshd

# 更新阿里云安全组
# 添加 2222，关闭 22
```

### 3. 安装 fail2ban

```bash
sudo yum install fail2ban -y
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

---

## 📞 快速帮助

### 如果以上方法都无效

请提供以下信息：

1. **当前状态**
   - 能否登录 root？
   - 使用什么方法重置？

2. **错误信息**
   - 完整的错误提示
   - 密码格式（脱敏）

3. **系统信息**
   ```bash
   cat /etc/os-release
   passwd -S admin
   ```

4. **截图**
   - 阿里云控制台
   - SSH 终端输出

---

**最后更新：** 2026-04-03  
**适用系统：** Alibaba Cloud Linux / CentOS 7+  
**账号：** admin (uid=1001)
