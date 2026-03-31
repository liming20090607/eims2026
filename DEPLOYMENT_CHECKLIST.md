# EIMS 项目部署前检查与清理报告

**生成时间**: 2026-03-26  
**目标环境**: 阿里云 MySQL 生产服务器

---

## 📋 一、数据库配置检查（重要！）

### ✅ 当前状态
- **开发环境**: SQLite (db.sqlite3)
- **生产配置**: 已准备好 MySQL 配置
- **配置文件**: `.env` 和 `settings_production.py`

### 🔧 需要调整的配置

#### 1. **修改 .env 文件**（生产环境）

打开 `.env` 文件，找到第 18-22 行，取消注释并修改：

```ini
# 生产环境：若使用 MySQL，取消下方注释并修改对应信息【生产需修改】
DB_NAME="eims_db"          # 生产环境 MySQL 数据库名称
DB_USER="eims_user"        # 生产环境 MySQL 用户名
DB_PASSWORD="your_password" # 生产环境 MySQL 密码
DB_HOST="localhost"        # 生产环境 MySQL 主机（本地为 localhost）
DB_PORT="3306"             # 生产环境 MySQL 端口（默认 3306）
```

#### 2. **修改 settings.py 或使用 production 配置**

**选项 A: 使用现有配置（推荐）**
- 上传 `settings_production.py` 到服务器
- 重命名为 `settings.py`
- 确保 `.env` 文件中已配置 MySQL 信息

**选项 B: 手动修改当前 settings.py**

将第 65-70 行从：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

改为：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'eims_db'),
        'USER': os.getenv('DB_USER', 'eims_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

#### 3. **安装 MySQL 驱动**

在服务器上执行：
```bash
pip install pymysql==1.1.0
```

或在 `requirements.txt` 中已包含该依赖。

---

## 🗑️ 二、需要清理的冗余文件

### 📌 测试文件（可删除）

以下文件用于开发和调试，生产环境不需要：

```
test_auth_backend.py
test_chinese_login.py
test_import_mapping.py
test_login_simple.py
test_one_person_multi_project.py
test_personnel.py
test_personnel_urls.py
test_template.py
test_workflow.py
debug_detailed.py
debug_import_tool.py
debug_personnel.py
check_pagination.py
check_personnel.py
check_subpanels.py
check_urls.py
```

**删除命令**（在服务器上）：
```bash
rm test_*.py debug_*.py check_*.py
```

### 📌 临时脚本文件（建议保留但可归档）

这些是一次性使用的脚本，生产环境可以删除：

```
add_is_deleted_field.py
add_remark_field.py
create_import_templates.py
fix_contract_table_complete.py
fix_personnel_db.py
manage_user_names.py
migrate_file_manage.py
migrate_old_data.py
recreate_contract_table.py
reset_file_manage.py
set_user_chinese_names.py
update_db.py
update_publish_time.py
```

### 📌 备份文件（建议保留）

```
backup_before_phase4.json          # 重要数据备份，建议保留
delete_old_tables.sql              # SQL 脚本，可选保留
```

### 📌 文档文件（建议保留）

所有 `.md` 文档都是项目说明，建议保留：
```
DROPDOWN_OTHER_PATTERN_GUIDE.md
COMPACT_LAYOUT_OPTIMIZATION.md
docs/ 文件夹下的所有文档
```

### 📌 批处理文件（按需保留）

Windows 专用脚本，Linux 服务器不需要：
```
get_ip.bat
run_server.BAT
setup_env.BAT
start_server.bat
start_server.bat.lnk
restore_db.BAT
setup_backup.BAT
backup_auto.BAT
```

Linux 替代方案已存在：
```
start_prod.sh           # ✓ 保留（生产启动脚本）
backup_db.sh           # ✓ 保留（备份脚本）
增强版部署脚本.sh       # ✓ 保留（部署脚本）
```

---

## 📦 三、文档组织情况

### ✅ 已整理的文档结构

```
docs/
├── 01-项目文档/          ✓ 168 个核心文档
├── 02-功能说明/          ✓ 已创建（待填充）
├── 03-部署指南/          ✓ 已创建（待填充）
├── 04-问题修复/          ✓ 2 个文档
├── 05-优化记录/          ✓ 4 个文档
├── 06-测试调试/          ✓ 已创建（待填充）
└── 07-快速指南/          ✓ 3 个文档
```

### 📝 根目录重要文档

```
✓ README.md                      - 项目说明
✓ QUICK_START.md                 - 快速开始指南
✓ 文档快速索引.md                - 文档导航
✓ DOCUMENT_ORGANIZATION_COMPLETE.md - 文档整理报告
```

**结论**: 文档已分类整理完成，无需额外操作！

---

## 🔐 四、安全配置检查

### ⚠️ 必须修改的配置

#### 1. **SECRET_KEY**（重要！）

在 `.env` 文件中生成新的密钥：

```bash
# 在服务器上执行
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

将生成的密钥复制到 `.env` 文件第 11 行：
```ini
SECRET_KEY="生成的新密钥"
```

#### 2. **ALLOWED_HOSTS**

在 `.env` 文件第 13 行添加服务器 IP/域名：
```ini
ALLOWED_HOSTS="your_server_ip,your_domain.com,localhost,127.0.0.1"
```

#### 3. **DEBUG 模式**

在 `.env` 文件第 8 行设置为 False：
```ini
DEBUG=False
```

---

## 📋 五、部署清单

### ✅ 部署前准备

- [ ] 1. 清理测试文件（test_*.py, debug_*.py, check_*.py）
- [ ] 2. 清理 Windows 批处理文件（可选）
- [ ] 3. 修改 `.env` 文件中的 MySQL 配置
- [ ] 4. 生成新的 SECRET_KEY
- [ ] 5. 设置 ALLOWED_HOSTS
- [ ] 6. 关闭 DEBUG 模式
- [ ] 7. 安装 MySQL 驱动（pymysql）
- [ ] 8. 创建 MySQL 数据库和用户

### 🚀 部署步骤

1. **上传项目到服务器**
   ```bash
   # 使用 scp 或 git
   scp -r EIMS2026 user@server:/path/to/
   ```

2. **配置 Python 虚拟环境**
   ```bash
   cd /path/to/EIMS2026
   python -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   # 编辑 .env 文件
   nano .env
   # 修改 MySQL 配置、SECRET_KEY、ALLOWED_HOSTS、DEBUG
   ```

4. **数据库迁移**
   ```bash
   # 创建 MySQL 数据库
   mysql -u root -p
   CREATE DATABASE eims_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'eims_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON eims_db.* TO 'eims_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   
   # 执行迁移
   python manage.py migrate
   ```

5. **收集静态文件**
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **创建超级用户**
   ```bash
   python manage.py createsuperuser
   ```

7. **启动服务**
   ```bash
   # 开发环境
   python manage.py runserver 0.0.0.0:8000
   
   # 生产环境（使用 Gunicorn）
   pip install gunicorn
   gunicorn --workers 3 --bind 0.0.0.0:8000 wsgi:application
   ```

---

## 🎯 六、关键文件清单

### ✅ 必须保留的核心文件

```
✓ settings.py / settings_production.py
✓ .env
✓ urls.py
✓ wsgi.py
✓ asgi.py
✓ manage.py
✓ requirements.txt
✓ requirements.prod.txt
✓ .gitignore
```

### ✅ 应用文件夹

```
✓ eims_app/
✓ approval/
✓ contract/
✓ core/
✓ document/
✓ project/
✓ utils/
```

### ✅ 模板和静态文件

```
✓ templates/
✓ static/
✓ staticfiles/
✓ media/
```

---

## 📊 七、文件大小分析

### 大型文件检查

- `db.sqlite3`: 776 KB（开发数据库，生产环境不需要上传）
- `backup_before_phase4.json`: 141 KB（重要备份，建议保留）
- `debug_import_tool.py`: 33 KB（调试工具，可删除）
- `create_import_templates.py`: 18 KB（一次性脚本，可删除）

---

## ⚡ 八、快速部署脚本

使用现有的部署脚本：

```bash
# 增强版部署脚本
chmod +x 增强版部署脚本.sh
./增强版部署脚本.sh

# 或者使用标准脚本
./start_prod.sh
```

---

## 🔍 九、验证检查

部署后执行以下检查：

```bash
# 1. 检查 Django 配置
python manage.py check --deploy

# 2. 检查数据库连接
python manage.py dbshell

# 3. 检查静态文件
python manage.py find_static admin/css/base.css

# 4. 测试启动
python manage.py runserver --insecure
```

---

## 📞 十、常见问题

### Q1: MySQL 连接失败？
**A**: 检查 `.env` 文件中的数据库配置，确保：
- 数据库已创建
- 用户权限已授予
- pymysql 已安装

### Q2: 静态文件 404？
**A**: 执行 `python manage.py collectstatic --noinput`

### Q3: 权限错误？
**A**: 确保文件夹权限正确：
```bash
chown -R www-data:www-data /path/to/EIMS2026
chmod -R 755 /path/to/EIMS2026
```

---

## ✅ 总结

### 需要删除的文件：
- ✓ 10 个 test_*.py 文件
- ✓ 3 个 debug_*.py 文件
- ✓ 4 个 check_*.py 文件
- ✓ 9 个 Windows .bat 文件（可选）

### 必须修改的配置：
- ✓ `.env` 中的 MySQL 配置（5 处）
- ✓ `.env` 中的 SECRET_KEY
- ✓ `.env` 中的 ALLOWED_HOSTS
- ✓ `.env` 中的 DEBUG=False

### 文档状态：
- ✓ 已完整分类整理
- ✓ 无需额外操作

### 数据库切换：
- ✓ 从 SQLite 切换到 MySQL
- ✓ 需要修改 `.env` 配置
- ✓ 需要安装 pymysql
- ✓ 需要创建 MySQL 数据库

---

**下一步行动**: 
1. 按照本报告的"部署清单"逐项检查
2. 删除冗余文件
3. 修改配置文件
4. 上传到服务器
5. 执行部署步骤

祝部署顺利！🎉
