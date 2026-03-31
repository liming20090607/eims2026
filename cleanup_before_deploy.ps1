# EIMS 部署前清理脚本 - PowerShell 版本
# 用于删除开发环境的冗余文件，准备部署到生产环境

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "EIMS 部署前清理工具" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "此脚本将清理开发环境的临时文件" -ForegroundColor Yellow
Write-Host "清理前请确保已提交所有重要代码到 Git" -ForegroundColor Yellow
Write-Host ""

# 统计
$deletedCount = 0
$skippedCount = 0
$errorCount = 0

# 删除文件函数
function Remove-FilePattern {
    param(
        [string]$Pattern,
        [string]$Description
    )
    
    Write-Host "清理：$Description" -ForegroundColor Yellow
    
    $files = Get-ChildItem -Path . -Filter $Pattern -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        try {
            Remove-Item -Path $file.FullName -Force
            $script:deletedCount++
            Write-Host "  ✓ 已删除：$($file.Name)" -ForegroundColor Gray
        }
        catch {
            $script:errorCount++
            Write-Host "  ✗ 删除失败：$($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Write-Host ""
}

# 1. 清理测试文件
Write-Host "[1/8] 清理测试文件..." -ForegroundColor Cyan
Remove-FilePattern "test_*.py" "测试 Python 文件"

# 2. 清理调试文件
Write-Host "[2/8] 清理调试文件..." -ForegroundColor Cyan
Remove-FilePattern "debug_*.py" "调试 Python 文件"

# 3. 清理检查脚本
Write-Host "[3/8] 清理检查脚本..." -ForegroundColor Cyan
Remove-FilePattern "check_*.py" "检查脚本"

# 4. 清理 HTML 测试文件
Write-Host "[4/8] 清理 HTML 测试文件..." -ForegroundColor Cyan
Remove-FilePattern "test_*.html" "测试 HTML 文件"

# 5. 清理 Excel 测试文件
Write-Host "[5/8] 清理 Excel 测试文件..." -ForegroundColor Cyan
$excelFiles = Get-ChildItem -Path . -Filter "*.xlsx" -File -ErrorAction SilentlyContinue
foreach ($file in $excelFiles) {
    if ($file.Name -like "test_*" -or $file.Name -like "*test*") {
        try {
            Remove-Item -Path $file.FullName -Force
            $deletedCount++
            Write-Host "  ✓ 已删除：$($file.Name)" -ForegroundColor Gray
        }
        catch {
            $errorCount++
            Write-Host "  ✗ 删除失败：$($file.Name)" -ForegroundColor Red
        }
    }
}
Write-Host ""

# 6. 清理一次性迁移脚本（需要确认）
Write-Host "[6/8] 清理一次性迁移脚本..." -ForegroundColor Cyan
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

$scriptIndex = 0
foreach ($script in $oneTimeScripts) {
    if (Test-Path $script) {
        $scriptIndex++
        $response = Read-Host "删除 $script ? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            try {
                Remove-Item -Path $script -Force
                $deletedCount++
                Write-Host "  ✓ 已删除：$script" -ForegroundColor Gray
            }
            catch {
                $errorCount++
                Write-Host "  ✗ 删除失败：$script" -ForegroundColor Red
            }
        } else {
            $skippedCount++
            Write-Host "  - 跳过：$script" -ForegroundColor Green
        }
    }
}
Write-Host ""

# 7. 清理临时数据文件
Write-Host "[7/8] 清理临时数据文件..." -ForegroundColor Cyan
$otherFiles = @(
    "chinese_names_example.csv",
    "delete_old_tables.sql",
    "COMPACT_LAYOUT_OPTIMIZATION.md"
)

foreach ($file in $otherFiles) {
    if (Test-Path $file) {
        try {
            Remove-Item -Path $file -Force
            $deletedCount++
            Write-Host "  ✓ 已删除：$file" -ForegroundColor Gray
        }
        catch {
            $errorCount++
            Write-Host "  ✗ 删除失败：$file" -ForegroundColor Red
        }
    }
}
Write-Host ""

# 8. 清理 Windows 批处理文件（可选）
Write-Host "[8/8] 检查 Windows 批处理文件..." -ForegroundColor Cyan
$batFiles = Get-ChildItem -Path . -Filter "*.bat" -File -ErrorAction SilentlyContinue
$lnkFiles = Get-ChildItem -Path . -Filter "*.lnk" -File -ErrorAction SilentlyContinue

$keepBatFiles = @("restore_db.BAT", "setup_backup.BAT", "backup_auto.BAT", "run_server.BAT")

foreach ($file in $batFiles) {
    if ($keepBatFiles -notcontains $file.Name) {
        $response = Read-Host "删除 $($file.Name) ? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            try {
                Remove-Item -Path $file.FullName -Force
                $deletedCount++
                Write-Host "  ✓ 已删除：$($file.Name)" -ForegroundColor Gray
            }
            catch {
                $errorCount++
                Write-Host "  ✗ 删除失败：$($file.Name)" -ForegroundColor Red
            }
        } else {
            $skippedCount++
            Write-Host "  - 跳过：$($file.Name)" -ForegroundColor Green
        }
    }
}

foreach ($file in $lnkFiles) {
    try {
        Remove-Item -Path $file.FullName -Force
        $deletedCount++
        Write-Host "  ✓ 已删除：$($file.Name)" -ForegroundColor Gray
    }
    catch {
        $errorCount++
        Write-Host "  ✗ 删除失败：$($file.Name)" -ForegroundColor Red
    }
}
Write-Host ""

# 清理 __pycache__ 目录
Write-Host "清理 __pycache__ 目录..." -ForegroundColor Yellow
$pycacheDirs = Get-ChildItem -Path . -Directory -Filter "__pycache__" -Recurse -ErrorAction SilentlyContinue
foreach ($dir in $pycacheDirs) {
    try {
        Remove-Item -Path $dir.FullName -Recurse -Force
        $deletedCount++
        Write-Host "  ✓ 已删除：$($dir.FullName)" -ForegroundColor Gray
    }
    catch {
        $errorCount++
        Write-Host "  ✗ 删除失败：$($dir.FullName)" -ForegroundColor Red
    }
}
Write-Host ""

# 显示统计
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "✓ 清理完成！" -ForegroundColor Green
Write-Host ""
Write-Host "统计:" -ForegroundColor Cyan
Write-Host "  已删除：$deletedCount 个文件/目录" -ForegroundColor Yellow
Write-Host "  跳过：$skippedCount 个文件" -ForegroundColor Green
Write-Host "  错误：$errorCount 个文件" -ForegroundColor Red
Write-Host ""

# 显示保留的重要文件
Write-Host "保留的重要文件:" -ForegroundColor Cyan
Write-Host "  ✓ settings.py / settings_production.py" -ForegroundColor Green
Write-Host "  ✓ .env (不要提交到 Git)" -ForegroundColor Green
Write-Host "  ✓ urls.py, manage.py" -ForegroundColor Green
Write-Host "  ✓ requirements.txt" -ForegroundColor Green
Write-Host "  ✓ docs/ (所有项目文档)" -ForegroundColor Green
Write-Host "  ✓ backup_before_phase4.json" -ForegroundColor Green
Write-Host "  ✓ eims_app/ (主应用目录)" -ForegroundColor Green
Write-Host "  ✓ 所有应用目录 (approval/, contract/, project/ 等)" -ForegroundColor Green
Write-Host ""

# 下一步提示
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "  1. 检查 .gitignore 是否正确" -ForegroundColor White
Write-Host "  2. 确认 requirements.txt 包含所有依赖" -ForegroundColor White
Write-Host "  3. 初始化 Git 仓库（如未初始化）" -ForegroundColor White
Write-Host "  4. 提交代码：git add . && git commit -m '生产部署'" -ForegroundColor White
Write-Host "  5. 上传到服务器（Git/SCP/FTP）" -ForegroundColor White
Write-Host ""

Write-Host "部署文档参考:" -ForegroundColor Cyan
Write-Host "  - docs/01-项目文档/DEPLOYMENT_CHECKLIST.md" -ForegroundColor White
Write-Host "  - docs/01-项目文档/DEPLOYMENT_GUIDE_COMPLETE.md" -ForegroundColor White
Write-Host "  - DEPLOYMENT_CLEANUP_GUIDE.md" -ForegroundColor White
Write-Host ""
