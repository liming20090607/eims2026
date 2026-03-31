# 🧹 EIMS 部署前清理总结

## 📊 可以删除的文件清单

### 1. 测试文件（约 13 个）
```
test_auth_backend.py
test_chinese_login.py
test_formula.html
test_import_mapping.py
test_login_simple.py
test_monthly_report_reminder.py
test_one_person_multi_project.py
test_pagination.py
test_permission.html
test_personnel.py
test_personnel_urls.py
test_template.py
test_total_count.py
test_workflow.py
```

### 2. 调试文件（约 3 个）
```
debug_detailed.py
debug_import_tool.py
debug_personnel.py
```

### 3. 检查脚本（约 9 个）
```
check_dates.py
check_excel_data.py
check_excel_headers.py
check_pagination.py
check_personnel.py
check_personnel_data.py
check_projects.py
check_subpanels.py
check_urls.py
```

### 4. 一次性迁移脚本（12 个）
```
add_is_deleted_field.py
add_remark_field.py
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

### 5. 临时数据文件（3 个）
```
chinese_names_example.csv
delete_old_tables.sql
COMPACT_LAYOUT_OPTIMIZATION.md
```

### 6. Excel 测试文件
```
test_import.xlsx
```

### 7. Windows 批处理文件（可选）
```
get_ip.bat
restart_clean.bat
setup_env.BAT
```

### 8. __pycache__ 目录
所有 `__pycache__` 目录（多个）

---

## ✅ 必须保留的核心文件

### Django 核心
- ✅ manage.py
- ✅ settings.py
- ✅ settings_production.py
- ✅ urls.py
- ✅ asgi.py
- ✅ wsgi.py
- ✅ requirements.txt
- ✅ requirements.prod.txt

### 应用目录
- ✅ eims_app/
- ✅ approval/
- ✅ contract/
- ✅ core/
- ✅ document/
- ✅ file_manage/
- ✅ project/
- ✅ utils/

### 模板和静态资源
- ✅ templates/
- ✅ static/
- ✅ staticfiles/ (已在.gitignore)

### 文档
- ✅ docs/ (所有项目文档)
- ✅ readme.txt

### 备份相关
- ✅ backup_before_phase4.json
- ✅ backup_db.sh
- ✅ restore_db.BAT
- ✅ setup_backup.BAT
- ✅ backup_auto.BAT

### 部署工具
- ✅ cleanup_for_deploy.sh
- ✅ setup_mysql.sh
- ✅ start_prod.sh
- ✅ 增强版部署脚本.sh

### 开发工具（建议保留）
- ✅ start_server.bat
- ✅ start_server.py
- ✅ run_comprehensive_tests.py
- ✅ init_workflow.py
- ✅ setup_department.py

---

## 🚀 快速清理步骤

### 方法 1：使用 PowerShell 脚本（推荐）

```powershell
# 1. 以管理员身份打开 PowerShell
# 2. 执行以下命令允许脚本运行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. 运行清理脚本：
cd E:\EIMS2026
.\cleanup_before_deploy.ps1
```

### 方法 2：手动删除

在文件资源管理器中：
1. 按 `test_*.py` 搜索并删除
2. 按 `debug_*.py` 搜索并删除
3. 按 `check_*.py` 搜索并删除
4. 删除上述清单中的文件

### 方法 3：使用命令提示符

```cmd
cd E:\EIMS2026

# 删除测试文件
del test_*.py /Q
del test_*.html /Q

# 删除调试文件
del debug_*.py /Q

# 删除检查脚本
del check_*.py /Q

# 删除 __pycache__
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
```

---

## 📝 更新 .gitignore

已更新 `.gitignore`，新增以下规则：

```gitignore
# 测试文件
test_*.py
test_*.html

# 调试文件
debug_*.py

# 检查脚本
check_*.py

# 临时数据文件
*.csv
*.xlsx
*.sql

# 一次性脚本（可选）
# add_*.py
# fix_*.py
# migrate_*.py
# update_*.py
```

---

## 📦 清理后效果

### 清理前
- 文件数：~100+ 个
- 总大小：~50MB+ (含 backup)
- 结构：混乱

### 清理后
- 文件数：~60 个
- 总大小：~5MB (不含 backup/media)
- 结构：清晰

---

## ✅ 清理完成检查清单

- [ ] 所有 `test_*.py` 文件已删除
- [ ] 所有 `debug_*.py` 文件已删除
- [ ] 所有 `check_*.py` 文件已删除
- [ ] 一次性迁移脚本已删除（或保留）
- [ ] 临时数据文件已删除
- [ ] `__pycache__` 目录已清理
- [ ] `.gitignore` 已更新
- [ ] `requirements.txt` 完整
- [ ] 核心文件都已保留
- [ ] 文档目录完整

---

## 🎯 下一步：部署到服务器

### 1. Git 初始化

```bash
cd E:\EIMS2026
git init
git add .
git commit -m "生产环境部署 - 清理后的代码"
```

### 2. 上传到服务器

**选择一种方式：**

#### Git 方式（推荐）
```bash
# 本地
git remote add origin <仓库地址>
git push -u origin main

# 服务器
cd /home
git clone <仓库地址> eims
```

#### SCP 方式
```bash
# 压缩
Compress-Archive E:\EIMS2026 E:\EIMS2026.zip

# 上传
scp E:\EIMS2026.zip root@服务器 IP:/home/

# 服务器解压
cd /home
unzip EIMS2026.zip
```

#### FTP 方式
使用 FileZilla 上传到 `/home/eims/`

### 3. 服务器配置

参考文档：
- [`docs/01-项目文档/DEPLOYMENT_CHECKLIST.md`](docs/01-项目文档/DEPLOYMENT_CHECKLIST.md)
- [`docs/01-项目文档/DEPLOYMENT_GUIDE_COMPLETE.md`](docs/01-项目文档/DEPLOYMENT_GUIDE_COMPLETE.md)

---

## 📋 重要提醒

### 数据库
- ❌ 不要上传 `db.sqlite3`
- ✅ 在服务器上创建 MySQL 数据库
- ✅ 修改 `settings.py` 使用 MySQL

### 环境变量
- ❌ 不要上传 `.env` 文件
- ✅ 在服务器上创建新的 `.env`
- ✅ 设置 `DEBUG=False`
- ✅ 生成新的 `SECRET_KEY`
- ✅ 设置 `ALLOWED_HOSTS`

### 媒体文件
- ❌ 不要上传 `media/` 目录（除非需要迁移数据）
- ✅ 在服务器上按需创建

### 日志文件
- ❌ 不要上传 `logs/` 目录
- ✅ 在服务器上自动创建

---

## 🎉 完成！

清理完成后，您的项目应该：
- ✅ 结构清晰
- ✅ 文件精简
- ✅ 适合部署
- ✅ 易于维护

**预计清理时间**: 10-15 分钟  
**预计部署时间**: 30-60 分钟

---

**创建时间**: 2026-03-30  
**状态**: ✅ 准备就绪
