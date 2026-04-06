# 账号系统说明 - Linux vs Django

## 📋 两种完全不同的账号

您的理解是正确的！**之前创建的 admin 账号和登录系统的账号不是同一个东西**。

---

## 1️⃣ Linux 系统账号（SSH 账号）

### 用途
- **登录服务器操作系统**（CentOS/Alibaba Cloud Linux）
- **执行系统命令**（安装软件、启动服务、管理文件等）
- **服务器运维管理**

### 登录方式
```bash
ssh admin@39.106.41.239
# 输入 Linux 密码
```

### 账号信息
- **用户名：** `admin`（之前创建的）
- **存储位置：** Linux 系统 `/etc/passwd` 文件
- **密码：** Linux 系统密码（使用 `passwd admin` 设置）
- **权限：** 文件系统访问、服务管理、sudo 权限等

### 能做什么
- ✅ 查看和修改服务器文件
- ✅ 启动/停止服务（Gunicorn、Supervisor 等）
- ✅ 安装软件和依赖
- ✅ 查看系统日志
- ✅ 执行数据库操作

### 不能做什么
- ❌ 直接登录 EIMS 办公系统
- ❌ 访问 Django Admin 后台
- ❌ 管理业务数据（部门、项目、合同等）

---

## 2️⃣ Django 系统账号（Web 应用账号）

### 用途
- **登录 EIMS 协同 AI 办公系统**
- **访问 Django Admin 后台管理**
- **使用业务功能**（部门管理、项目管理、合同管理等）

### 登录方式
打开浏览器访问：
```
http://39.106.41.239:8000/admin/
```
在登录页面输入 Django 账号和密码

### 账号信息
- **用户名：** 在 Django 数据库中（如：admin、zhangsan 等）
- **存储位置：** Django 数据库 `auth_user` 表
- **密码：** Django 加密密码（使用 `create_superuser` 创建）
- **权限：** 由 Django 权限系统控制（模型权限、对象权限等）

### 能做什么
- ✅ 登录办公系统处理业务
- ✅ 在 Admin 后台管理数据
- ✅ 查看和编辑项目、合同、文档
- ✅ 管理用户和角色
- ✅ 审批流程操作

### 不能做什么
- ❌ 访问服务器文件系统
- ❌ 执行系统命令
- ❌ 修改服务器配置
- ❌ 查看系统日志

---

## 📊 详细对比表

| 特性 | Linux 账号 | Django 账号 |
|------|-----------|-----------|
| **用途** | 服务器管理 | 办公系统使用 |
| **登录协议** | SSH（端口 22） | HTTP/HTTPS（端口 8000） |
| **登录地址** | `ssh admin@39.106.41.239` | `http://39.106.41.239:8000/admin/` |
| **存储位置** | `/etc/passwd` | 数据库 `auth_user` 表 |
| **密码存储** | Linux 加密（/etc/shadow） | Django 加密（数据库） |
| **创建命令** | `useradd admin` | `python manage.py createsuperuser` |
| **修改密码** | `passwd admin` | Django Admin 后台或代码 |
| **权限范围** | 服务器操作系统 | Web 应用功能 |
| **账号示例** | `admin` | `admin`（可以同名，但完全不同） |

---

## 🔍 为什么会有两个账号？

### 分层架构设计

```
┌─────────────────────────────────────┐
│   用户层：Django 账号               │
│   - 办公系统用户                    │
│   - 管理员、普通员工、领导等        │
│   - 通过浏览器访问                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   应用层：Django 框架               │
│   - Web 应用逻辑                    │
│   - 业务数据处理                    │
│   - 运行在端口 8000                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   系统层：Linux 账号                │
│   - 服务器管理员                    │
│   - 运维人员                        │
│   - 通过 SSH 访问                   │
└─────────────────────────────────────┘
```

### 安全隔离
- **Linux 账号**管理服务器（操作系统层面）
- **Django 账号**管理业务（应用层面）
- 两者相互独立，互不影响

---

## 🎯 实际使用场景

### 场景 1：服务器运维
**需要：** Linux 账号

```bash
# SSH 登录服务器
ssh admin@39.106.41.239

# 启动服务
sudo systemctl start supervisord

# 查看日志
tail -f /var/log/eims/error.log
```

### 场景 2：办公系统使用
**需要：** Django 账号

```
1. 打开浏览器
2. 访问 http://39.106.41.239:8000/
3. 输入 Django 账号密码
4. 使用办公功能
```

### 场景 3：后台管理
**需要：** Django 超级管理员账号

```
1. 打开浏览器
2. 访问 http://39.106.41.239:8000/admin/
3. 输入 Django 超级管理员账号密码
4. 管理后台数据
```

---

## 🛠️ 账号管理

### Linux 账号管理

```bash
# 查看当前用户
whoami

# 查看所有用户
cat /etc/passwd

# 创建用户
sudo useradd -m -s /bin/bash newuser

# 设置密码
sudo passwd newuser

# 删除用户
sudo userdel -r newuser

# 修改用户信息
sudo usermod -aG wheel username  # 添加到 sudo 组
```

### Django 账号管理

```bash
# 创建超级管理员
cd /var/www/eims
source venv/bin/activate
python manage.py createsuperuser

# 查看所有用户
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()

# 修改密码
python manage.py changepassword username

# 删除用户
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.get(username='test').delete()
```

---

## ⚠️ 常见误区

### ❌ 误区 1：Linux 的 admin 账号可以登录 Django
**事实：** 不可以！这是两个完全不同的系统。

### ❌ 误区 2：Django 密码和 Linux 密码要一样
**事实：** 不需要，两者没有任何关系。

### ❌ 误区 3：删除 Linux 账号会影响 Django
**事实：** 不会，Django 账号存储在数据库中。

### ❌ 误区 4：Django 用户可以直接访问服务器
**事实：** 不可以，除非同时创建 Linux 账号。

---

## 📝 现在的情况

### 您已有的账号

1. **Linux 账号：**
   - 用户名：`admin`
   - 用途：SSH 登录服务器
   - 密码：您使用 `passwd admin` 设置的密码

2. **Django 账号：**
   - **需要确认是否已创建**
   - 用途：登录 Django Admin 后台
   - 密码：在创建 Django 用户时设置

---

## 🚀 下一步操作

### 1. 检查 Django 管理员账号

SSH 登录后执行：
```bash
sudo su -
bash /tmp/检查\ admin\ 账号.sh
```

或使用自动脚本（已创建）：
```bash
# 上传脚本
scp E:\EIMS2026\bat\检查 admin 账号.sh admin@39.106.41.239:/tmp/

# SSH 登录执行
ssh admin@39.106.41.239
sudo bash /tmp/检查\ admin\ 账号.sh
```

### 2. 如果没有 Django 管理员账号

使用脚本创建：
```bash
# 上传脚本
scp E:\EIMS2026\bat\创建 Django 管理员.sh admin@39.106.41.239:/tmp/

# SSH 登录执行
ssh admin@39.106.41.239
sudo bash /tmp/创建\ Django\ 管理员.sh
```

### 3. 手动创建 Django 管理员

```bash
# SSH 登录
ssh admin@39.106.41.239
sudo su -

cd /var/www/eims
source venv/bin/activate

# 创建超级管理员
python manage.py createsuperuser

# 按提示输入：
# Username: admin
# Email: （可选）
# Password: 输入密码
# Password (again): 确认密码
```

---

## ✅ 总结

| 账号类型 | 您是否有？ | 用途 | 登录方式 |
|---------|-----------|------|---------|
| **Linux** | ✅ 已创建 | 服务器管理 | SSH 端口 22 |
| **Django** | ❓ 待确认 | 办公系统 | Web 端口 8000 |

**重要提示：**
- 这是两个**完全独立**的账号系统
- 需要**分别管理**，不能混用
- 办公系统登录需要 Django 账号
- 服务器管理需要 Linux 账号

---

**最后更新：** 2026-04-03  
**适用系统：** EIMS（Django 4.2.7）+ Alibaba Cloud Linux
