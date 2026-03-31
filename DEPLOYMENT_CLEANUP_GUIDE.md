# 🧹 EIMS 部署前清理指南

## 📋 文件分类清单

### ✅ **必须保留的核心文件**

#### 1. Django 项目核心
```
✅ manage.py
✅ settings.py
✅ settings_production.py (或 settings.prod.py)
✅ urls.py
✅ asgi.py
✅ wsgi.py
✅ .env (但不应提交到 Git)
✅ requirements.txt
✅ requirements.prod.txt
```

#### 2. 应用目录
```
✅ eims_app/          (主应用)
✅ approval/          (审批模块)
✅ contract/          (合同模块)
✅ core/              (核心模块)
✅ document/          (文档模块)
✅ file_manage/       (文件管理)
✅ project/           (项目模块)
✅ utils/             (工具函数)
```

#### 3. 模板和静态资源
```
✅ templates/         (HTML 模板)
✅ static/            (静态资源 - 开发环境)
✅ staticfiles/       (生产环境收集目录 - 已在.gitignore)
```

#### 4. 文档
```
✅ docs/              (所有项目文档)
✅ readme.txt
```

#### 5. 备份相关（建议保留）
```
✅ backup_before_phase4.json  (数据备份)
✅ backup_db.sh               (数据库备份脚本)
✅ restore_db.BAT             (数据库恢复)
✅ setup_backup.BAT           (备份设置)
✅ backup_auto.BAT            (自动备份)
```

---

### 🗑️ **可以删除的文件**

#### 1. 测试文件（全部删除）
```python
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
test_import.xlsx
```

#### 2. 调试文件（全部删除）
```python
debug_detailed.py
debug_import_tool.py
debug_personnel.py
```

#### 3. 检查脚本（全部删除）
```python
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

#### 4. 一次性迁移脚本（已完成后删除）
```python
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

#### 5. 临时数据导入脚本（完成后删除）
```python
create_import_templates.py
direct_import.py
fix_import_data.py
import_employees_to_personnel.py
quick_start.py
quick_test_personnel.py
verify_personnel.py
verify_personnel_dropdown.py
```

#### 6. Windows 批处理文件（可选删除）
```batch
get_ip.bat
restart_clean.bat
run_server.BAT (已有 start_server.bat)
setup_env.BAT
```

#### 7. 其他临时文件
```
chinese_names_example.csv
delete_old_tables.sql
test.xlsx
COMPACT_LAYOUT_OPTIMIZATION.md (空文件)
```

---

### 📦 **建议保留的开发工具**

#### 1. 服务器启动相关
```bash
✅ start_server.bat       (Windows 启动脚本)
✅ start_server.py        (Python 启动脚本)
✅ run_comprehensive_tests.py  (综合测试)
```

#### 2. 部署脚本
```bash
✅ cleanup_for_deploy.sh  (清理脚本 - 部署时使用)
✅ setup_mysql.sh         (MySQL 设置)
✅ start_prod.sh          (生产环境启动)
✅ 增强版部署脚本.sh       (增强部署)
```

#### 3. 初始化脚本
```bash
✅ init_workflow.py       (工作流初始化)
✅ setup_department.py    (部门设置)
```

---

## 🚀 **清理方法**

### 方法 1：使用清理脚本（推荐）

在 PowerShell 中执行：

```powershell
# 1. 先查看将要删除的文件
Get-ChildItem -Path . -Filter "test_*.py" | Select-Object Name
Get-ChildItem -Path . -Filter "debug_*.py" | Select-Object Name
Get-ChildItem -Path . -Filter "check_*.py" | Select-Object Name

# 2. 执行清理（手动删除）
# 见下方的删除命令
```

### 方法 2：手动删除（最安全）

创建删除脚本 `cleanup_before_deploy.ps1`：

```powershell
# EIMS 部署前清理脚本 - PowerShell 版本

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "EIMS 部署前清理工具" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$deletedCount = 0
$skippedCount = 0

# 删除文件函数
function Remove-FilePattern {
    param($Pattern, $Description)
    
    Write-Host "清理：$Description" -ForegroundColor Yellow
    
    $files = Get-ChildItem -Path . -Filter $Pattern -File
    foreach ($file in $files) {
        Remove-Item -Path $file.FullName -Force
        $script:deletedCount++
        Write-Host "  已删除：$($file.Name)" -ForegroundColor Gray
    }
}

# 1. 清理测试文件
Remove-FilePattern "test_*.py" "测试文件"

# 2. 清理调试文件
Remove-FilePattern "debug_*.py" "调试文件"

# 3. 清理检查脚本
Remove-FilePattern "check_*.py" "检查脚本"

# 4. 清理一次性脚本（需要确认）
$oneTimeScripts = @(
    "add_is_deleted_field.py",
    "add_remark_field.py",
    "fix_contract_table_complete.py",
    "fix_personnel_db.py",
    "manage_user_names.py",
    "migrate_file_manage.py",
    "migrate_old_data.py",
    "recreate_contract_table.py",
    "reset_file_manage.py",
    "set_user_chinese_names.py",
    "update_db.py",
    "update_publish_time.py"
)

Write-Host ""
Write-Host "以下是一次性脚本，是否删除？" -ForegroundColor Yellow
foreach ($script in $oneTimeScripts) {
    if (Test-Path $script) {
        $response = Read-Host "删除 $script ? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Remove-Item -Path $script -Force
            $deletedCount++
            Write-Host "  已删除：$script" -ForegroundColor Gray
        } else {
            $skippedCount++
            Write-Host "  跳过：$script" -ForegroundColor Green
        }
    }
}

# 5. 清理其他临时文件
$otherFiles = @(
    "chinese_names_example.csv",
    "delete_old_tables.sql",
    "test.xlsx",
    "COMPACT_LAYOUT_OPTIMIZATION.md"
)

foreach ($file in $otherFiles) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Force
        $deletedCount++
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "✓ 清理完成！" -ForegroundColor Green
Write-Host ""
Write-Host "统计:" -ForegroundColor Cyan
Write-Host "  已删除：$deletedCount 个文件" -ForegroundColor Yellow
Write-Host "  跳过：$skippedCount 个文件" -ForegroundColor Green
Write-Host ""

Write-Host "保留的重要文件:" -ForegroundColor Cyan
Write-Host "  ✓ settings.py / settings_production.py"
Write-Host "  ✓ .env (不要提交到 Git)"
Write-Host "  ✓ urls.py, manage.py"
Write-Host "  ✓ requirements.txt"
Write-Host "  ✓ docs/ (所有文档)"
Write-Host "  ✓ backup_before_phase4.json"
Write-Host ""
```

---

## 📝 **清理后的文件清单**

### 清理后应该保留的文件：

```
EIMS2026/
├── .env                          # 环境变量（不提交）
├── .env.prod.example            # 示例配置
├── .env.production.example      # 示例配置
├── .gitignore                   # Git 忽略文件
├── asgi.py                      # ASGI 配置
├── backup_before_phase4.json    # 数据备份
├── backup_db.sh                 # 备份脚本
├── cleanup_for_deploy.sh        # 清理脚本
├── db.sqlite3                   # SQLite 数据库（生产环境用 MySQL）
├── docs/                        # 项目文档
├── eims_app/                    # 主应用
├── manage.py                    # Django 管理脚本
├── package-lock.json            # Node.js 依赖
├── package.json                 # Node.js 配置
├── requirements.prod.txt        # 生产环境依赖
├── requirements.txt             # 依赖列表
├── requirements 的说明.txt       # 依赖说明
├── restore_db.BAT               # 数据库恢复
├── run_comprehensive_tests.py   # 综合测试
├── settings.prod.py             # 生产环境配置
├── settings.py                  # 开发环境配置
├── settings_production.py       # 生产环境配置
├── setup_backup.BAT             # 备份设置
├── setup_department.py          # 部门设置
├── start_prod.sh                # 生产启动脚本
├── start_server.bat             # 开发启动脚本
├── start_server.py              # Python 启动脚本
├── urls.py                      # URL 配置
├── wsgi.py                      # WSGI 配置
├── 增强版部署脚本.sh             # 增强部署脚本
├── approval/                    # 审批模块
├── contract/                    # 合同模块
├── core/                        # 核心模块
├── document/                    # 文档模块
├── file_manage/                 # 文件管理
├── project/                     # 项目模块
├── static/                      # 静态资源
├── templates/                   # 模板文件
└── utils/                       # 工具函数
```

---

## ⚠️ **注意事项**

### 1. 数据库文件
- `db.sqlite3` - 开发环境数据库，**生产环境应使用 MySQL**
- 部署时不需要上传，在服务器上重新创建

### 2. 环境变量
- `.env` - 包含敏感信息，**不要提交到 Git**
- `.env.prod.example` - 示例配置，可以提交
- 生产环境需要创建新的 `.env` 文件

### 3. 媒体文件
- `media/` - 用户上传的文件，已在 `.gitignore`
- 部署时按需上传

### 4. 日志文件
- `logs/` - 日志目录，已在 `.gitignore`
- 不需要上传

### 5. 备份目录
- `backup/` - 自动备份文件，已在 `.gitignore`
- 文件很大，不需要上传

---

## 🎯 **推荐清理步骤**

### Step 1: 本地清理（Windows）

1. **运行清理脚本**
   ```powershell
   cd E:\EIMS2026
   .\cleanup_before_deploy.ps1
   ```

2. **手动检查**
   ```powershell
   # 查看是否还有测试文件
   Get-ChildItem -Recurse -Filter "test_*.py"
   
   # 查看临时文件
   Get-ChildItem -Recurse -Filter "*.tmp"
   ```

### Step 2: 更新 .gitignore

确保 `.gitignore` 包含：

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
env/

# Django
db.sqlite3
*.db
media/
staticfiles/
.env
logs/
backup/

# 系统文件
.DS_Store
Thumbs.db
.idea/
.vscode/
*.swp
*.swo
*.log
```

### Step 3: Git 初始化

```bash
cd E:\EIMS2026
git init
git add .
git commit -m "生产环境部署 - 清理后的代码"
```

### Step 4: 上传到服务器

选择一种方式：
- **Git**: 推送到 GitHub/Gitee，然后服务器拉取
- **SCP**: `scp -r E:\EIMS2026 root@服务器 IP:/home/eims`
- **FTP**: 使用 FileZilla 上传

---

## 📊 **清理效果对比**

### 清理前
- 文件数：约 100+ 个
- 总大小：约 50MB+（包含 backup 目录）
- 混乱度：高（各种测试、调试文件混杂）

### 清理后
- 文件数：约 60 个
- 总大小：约 5MB（不含 backup/media）
- 混乱度：低（结构清晰）

---

## ✅ **清理完成检查**

清理完成后，确认：

- [ ] 所有 `test_*.py` 文件已删除
- [ ] 所有 `debug_*.py` 文件已删除
- [ ] 所有 `check_*.py` 文件已删除
- [ ] 一次性迁移脚本已删除
- [ ] 临时数据文件已删除
- [ ] `.gitignore` 配置正确
- [ ] `requirements.txt` 完整
- [ ] 核心文件都已保留
- [ ] 文档目录完整

---

## 🚀 **下一步：部署到服务器**

清理完成后，参考以下文档进行部署：

1. [`docs/01-项目文档/DEPLOYMENT_CHECKLIST.md`](file://e:\EIMS2026\docs\01-项目文档\DEPLOYMENT_CHECKLIST.md) - 部署检查清单
2. [`docs/01-项目文档/DEPLOYMENT_GUIDE_COMPLETE.md`](file://e:\EIMS2026\docs\01-项目文档\DEPLOYMENT_GUIDE_COMPLETE.md) - 完整部署指南
3. [`docs/01-项目文档/阿里云部署步骤.md`](file://e:\EIMS2026\docs\01-项目文档\阿里云部署步骤.md) - 阿里云部署步骤

---

**创建时间**: 2026-03-30  
**状态**: ✅ 已完成  
**预计清理时间**: 10-15 分钟
