# EIMS 本地 MySQL 安装配置指南

## 📋 方案 A：安装 MySQL 本地数据库

### 第一步：下载 MySQL 8.0

**官方下载地址：**
https://dev.mysql.com/downloads/mysql/8.0.html

**推荐下载：**
- MySQL Installer for Windows (mysql-installer-community-8.0.xx.msi)
- 选择 "Developer Default" 或 "Server only" 安装类型

### 第二步：安装 MySQL

1. **运行安装程序**
   - 双击下载的 `.msi` 文件
   - 选择安装类型：`Developer Default`（推荐）或 `Server only`

2. **配置 MySQL Server**
   - Config Type: `Development Computer`
   - TCP/IP Port: `3306`
   - Root Password: **设置为 `root123`**（与服务器一致）
   
3. **Windows Service**
   - ✅ Configure MySQL Server as a Windows Service
   - Service Name: `MySQL80`
   - ✅ Start the MySQL Server at System Startup

4. **完成安装**
   - Apply Configuration → Execute
   - Finish

### 第三步：验证安装

打开 PowerShell 或 CMD：

```powershell
# 测试 MySQL 连接
mysql -u root -proot123

# 如果成功，会进入 MySQL 命令行，输入 exit 退出
exit
```

### 第四步：创建 EIMS 数据库

```powershell
mysql -u root -proot123 -e "CREATE DATABASE eims DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -proot123 -e "SHOW DATABASES;"
```

### 第五步：安装 Python MySQL 驱动

在项目目录下执行：

```powershell
cd e:\EIMS2026
pip install pymysql cryptography
```

### 第六步：配置 Django 使用 MySQL

我已为您创建了 [settings_local_mysql.py](file:///e:/EIMS2026/settings_local_mysql.py) 配置文件，内容已配置好使用本地 MySQL。

### 第七步：迁移数据库结构

```powershell
cd e:\EIMS2026
python manage.py migrate --settings=settings_local_mysql
```

### 第八步：导出 SQLite 数据（可选）

如果想保留现有 SQLite 数据：

```powershell
python manage.py dumpdata --natural-foreign --natural-primary --indent=2 --output sqlite_backup.json
```

### 第九步：导入数据到 MySQL（可选）

```powershell
python manage.py loaddata sqlite_backup.json --settings=settings_local_mysql
```

---

## 🚀 启动开发服务器

```powershell
# 使用 MySQL 配置启动
python manage.py runserver --settings=settings_local_mysql
```

或修改 [settings.py](file:///e:/EIMS2026/settings.py) 的最后一行：

```python
# 注释掉原来的
# DEBUG = True

# 添加这一行
from .settings_local_mysql import *
```

---

## 📊 切换回 SQLite（如需）

只需修改 [settings.py](file:///e:/EIMS2026/settings.py)：

```python
# 注释掉 MySQL 配置
# from .settings_local_mysql import *

# 恢复原来的
DEBUG = True
```

---

## ✅ 验证配置

```powershell
cd e:\EIMS2026
python manage.py check --settings=settings_local_mysql
python manage.py showmigrations --settings=settings_local_mysql
```

---

## 🔧 常见问题

### 问题 1：找不到 mysql 命令

**解决：** 将 MySQL bin 目录添加到系统 PATH

```
C:\Program Files\MySQL\MySQL Server 8.0\bin
```

### 问题 2：pip install pymysql 失败

**解决：**

```powershell
pip install --upgrade pip
pip install pymysql cryptography
```

### 问题 3：迁移时提示表已存在

**解决：** 如果数据库是全新的，删除并重建：

```powershell
mysql -u root -proot123 -e "DROP DATABASE eims;"
mysql -u root -proot123 -e "CREATE DATABASE eims DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
python manage.py migrate --settings=settings_local_mysql
```

---

**现在请按照上述步骤操作，有任何问题随时告诉我！** 🚀
