# SSH 登录服务器的 5 种方式

**目标服务器**: `39.106.41.239`  
**用户名**: `root`  
**用途**: 执行数据迁移脚本

---

## 🎯 **方式 1：Windows PowerShell（推荐）** ⭐⭐⭐⭐⭐

### **适用场景**
- Windows 10/11 系统
- 最简单，无需安装额外软件
- 支持中文显示

---

### **操作步骤**

#### **1. 打开 PowerShell**

**方法 A**: 按 `Win + X`，选择"Windows PowerShell"或"终端"

**方法 B**: 
- 按 `Win + R`
- 输入 `powershell`
- 按回车

---

#### **2. SSH 登录**

在 PowerShell 中输入：

```powershell
ssh root@39.106.41.239
```

---

#### **3. 输入密码**

提示 `password:` 时输入服务器密码

**注意**：输入密码时不会显示任何字符（正常现象）

---

#### **4. 登录成功**

看到类似欢迎信息表示成功：

```
[root@iZbp1... ~]#
```

---

### **完整示例**

```powershell
PS C:\Users\YourName> ssh root@39.106.41.239
The authenticity of host '39.106.41.239 (39.106.41.239)' can't be established.
ECDSA key fingerprint is SHA256:xxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '39.106.41.239' (ECDSA) to the list of known hosts.
root@39.106.41.239's password: ********

Welcome to Alibaba Cloud ECS Linux...

[root@iZbp1... ~]#
```

---

## 🔧 **方式 2：Git Bash** ⭐⭐⭐⭐⭐

### **适用场景**
- 已安装 Git for Windows
- 习惯 Linux 命令环境
- 更好的兼容性

---

### **操作步骤**

#### **1. 打开 Git Bash**

- 右键点击桌面或文件夹
- 选择 "Git Bash Here"
- 或在开始菜单搜索 "Git Bash"

---

#### **2. SSH 登录**

```bash
ssh root@39.106.41.239
```

---

#### **3. 输入密码**

输入服务器密码（不显示）

---

### **优势**

✅ 支持所有 Linux 命令  
✅ 中文显示正常  
✅ 可以运行 shell 脚本  

---

## 💻 **方式 3：PuTTY（经典工具）** ⭐⭐⭐⭐

### **适用场景**
- 需要保存多个服务器配置
- 需要会话管理
- 喜欢图形界面

---

### **下载安装**

**下载地址**: https://www.putty.org/

或直接下载：https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html

---

### **配置步骤**

#### **1. 启动 PuTTY**

双击 `putty.exe`

---

#### **2. 填写服务器信息**

- **Host Name (or IP address)**: `39.106.41.239`
- **Port**: `22`
- **Connection type**: `SSH`

---

#### **3. 保存会话（可选）**

- **Saved Sessions**: 输入名称（如 "EIMS Server"）
- 点击 "Save"

下次直接双击会话名称即可连接

---

#### **4. 点击 "Open"**

弹出黑色窗口

---

#### **5. 登录**

```
login as: root
root@39.106.41.239's password: ********
```

---

### **PuTTY 优点**

✅ 免费开源  
✅ 轻量级  
✅ 可保存多个服务器  
✅ 支持密钥认证  

---

## 🌐 **方式 4：Xshell（专业工具）** ⭐⭐⭐⭐

### **适用场景**
- 需要强大功能
- 多标签管理
- 企业环境

---

### **下载**

官网：https://www.netsarang.com/products/xsh_overview.html

有免费的家庭/学校版本

---

### **配置步骤**

#### **1. 新建会话**

点击 "文件" → "新建"

---

#### **2. 填写连接信息**

- **名称**: EIMS 服务器
- **协议**: SSH
- **主机**: 39.106.41.239
- **端口号**: 22

---

#### **3. 用户身份验证**

- **方法**: Password
- **用户名**: root
- **密码**: （可保存）

---

#### **4. 连接**

双击会话或点击 "连接"

---

### **Xshell 优势**

✅ 多标签管理  
✅ 强大的复制粘贴  
✅ 支持中文  
✅ 会话管理器  

---

## 📱 **方式 5：Windows Terminal（现代化选择）** ⭐⭐⭐⭐⭐

### **适用场景**
- Windows 10/11
- 喜欢现代化界面
- 需要多标签

---

### **安装**

#### **从 Microsoft Store 安装**

1. 打开 Microsoft Store
2. 搜索 "Windows Terminal"
3. 点击 "获取" 安装

---

#### **或使用 PowerShell 安装**

```powershell
winget install --id Microsoft.WindowsTerminal_8wekyb3d8bbwe
```

---

### **配置 SSH**

#### **1. 打开 Windows Terminal**

---

#### **2. 新建标签页**

按 `Ctrl + Shift + T` 或点击 "+" 号

---

#### **3. 输入 SSH 命令**

```bash
ssh root@39.106.41.239
```

---

### **Windows Terminal 优势**

✅ 现代化界面  
✅ 多标签管理  
✅ 高度可定制  
✅ 支持 PowerShell、CMD、WSL  

---

## 🚀 **快速对比**

| 方式 | 难度 | 功能 | 推荐度 | 适用人群 |
|------|------|------|--------|----------|
| **PowerShell** | ⭐ 简单 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 所有人 |
| **Git Bash** | ⭐ 简单 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 开发者 |
| **PuTTY** | ⭐⭐ 中等 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 运维人员 |
| **Xshell** | ⭐⭐ 中等 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 专业人士 |
| **Windows Terminal** | ⭐ 简单 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 所有人 |

---

## 🎯 **针对您的情况（数据迁移）**

### **最推荐的方式**

#### **方案 A：使用 PowerShell（最简单）**

```powershell
# 1. 按 Win + R
# 2. 输入 powershell
# 3. 按回车

# 4. 输入
ssh root@39.106.41.239

# 5. 输入密码

# 6. 登录后执行
bash /root/import_data_fix_encoding.sh
```

---

#### **方案 B：使用 Git Bash（更专业）**

```bash
# 1. 右键桌面 → Git Bash Here

# 2. 输入
ssh root@39.106.41.239

# 3. 输入密码

# 4. 登录后执行
bash /root/import_data_fix_encoding.sh
```

---

## 📋 **详细操作指南**

### **使用 PowerShell 完整流程**

#### **步骤 1：打开 PowerShell**

按 `Win + X`，选择 "Windows PowerShell"

---

#### **步骤 2：首次连接**

```powershell
ssh root@39.106.41.239
```

**首次连接会提示**：
```
The authenticity of host '39.106.41.239' can't be established.
ECDSA key fingerprint is SHA256:xxxxx.
Are you sure you want to continue connecting (yes/no)? yes
```

输入 `yes` 并回车

---

#### **步骤 3：输入密码**

```
root@39.106.41.239's password:
```

输入密码（不会显示），按回车

---

#### **步骤 4：登录成功**

看到 `[root@iZbp1... ~]#` 表示成功

---

#### **步骤 5：执行数据迁移脚本**

```bash
bash /root/import_data_fix_encoding.sh
```

等待完成

---

#### **步骤 6：退出**

```bash
exit
```

---

## ⚠️ **常见问题**

### **Q1: "ssh" 不是可识别的命令？**

**A**: Windows 功能未启用

**解决方法**：

#### **方法 A：启用 OpenSSH**

1. 设置 → 应用 → 可选功能
2. 点击 "添加功能"
3. 搜索 "OpenSSH"
4. 安装 "OpenSSH 客户端"
5. 重启 PowerShell

---

#### **方法 B：使用 Git Bash**

如果已安装 Git，直接用 Git Bash 即可

---

### **Q2: 连接超时？**

**A**: 检查网络和防火墙

```powershell
# 测试连接
ping 39.106.41.239

# 如果能 ping 通但 SSH 失败
# 检查服务器安全组是否开放 22 端口
```

---

### **Q3: 密码错误？**

**A**: 确认密码正确，注意大小写

如果是阿里云服务器：
- 可以在阿里云控制台重置密码
- 或使用密钥对登录

---

### **Q4: 中文乱码？**

**A**: 设置编码为 UTF-8

**PowerShell**:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

**或在设置中调整**

---

## 🎊 **总结**

### **对于数据迁移任务，推荐**

**首选**: **PowerShell** 或 **Git Bash**

**理由**：
- ✅ 无需安装额外软件
- ✅ 简单易用
- ✅ 支持中文
- ✅ 可以直接运行脚本

---

### **快速开始**

```powershell
# 1. 打开 PowerShell（Win + R → powershell）

# 2. 输入
ssh root@39.106.41.239

# 3. 输入密码

# 4. 执行
bash /root/import_data_fix_encoding.sh
```

**就这么简单！** 🚀

---

**位置**: `E:\EIMS2026\bat\SSH 登录方式完全指南.md`  
**状态**: ✅ 立即可用  
**下一步**: 选择一种方式，SSH 登录服务器！

---

**选择最适合您的方式，5 分钟完成 SSH 登录和数据迁移！** ✨
