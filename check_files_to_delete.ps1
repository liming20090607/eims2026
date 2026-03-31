# EIMS 项目文件检查清单
# 运行此脚本查看可以删除的文件

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "EIMS 项目文件检查" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$totalCount = 0

# 1. 测试文件
Write-Host "[测试文件]" -ForegroundColor Yellow
$testFiles = Get-ChildItem -Path . -Filter "test_*.py" -File -ErrorAction SilentlyContinue
foreach ($file in $testFiles) {
    Write-Host "  - $($file.Name)" -ForegroundColor Gray
    $totalCount++
}
$testHtmlFiles = Get-ChildItem -Path . -Filter "test_*.html" -File -ErrorAction SilentlyContinue
foreach ($file in $testHtmlFiles) {
    Write-Host "  - $($file.Name)" -ForegroundColor Gray
    $totalCount++
}
Write-Host "  小计：$($testFiles.Count + $testHtmlFiles.Count) 个文件" -ForegroundColor Cyan
Write-Host ""

# 2. 调试文件
Write-Host "[调试文件]" -ForegroundColor Yellow
$debugFiles = Get-ChildItem -Path . -Filter "debug_*.py" -File -ErrorAction SilentlyContinue
foreach ($file in $debugFiles) {
    Write-Host "  - $($file.Name)" -ForegroundColor Gray
    $totalCount++
}
Write-Host "  小计：$($debugFiles.Count) 个文件" -ForegroundColor Cyan
Write-Host ""

# 3. 检查脚本
Write-Host "[检查脚本]" -ForegroundColor Yellow
$checkFiles = Get-ChildItem -Path . -Filter "check_*.py" -File -ErrorAction SilentlyContinue
foreach ($file in $checkFiles) {
    Write-Host "  - $($file.Name)" -ForegroundColor Gray
    $totalCount++
}
Write-Host "  小计：$($checkFiles.Count) 个文件" -ForegroundColor Cyan
Write-Host ""

# 4. 一次性迁移脚本
Write-Host "[一次性迁移脚本]" -ForegroundColor Yellow
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

$count = 0
foreach ($script in $oneTimeScripts) {
    if (Test-Path $script) {
        Write-Host "  - $script" -ForegroundColor Gray
        $count++
        $totalCount++
    }
}
Write-Host "  小计：$count 个文件" -ForegroundColor Cyan
Write-Host ""

# 5. 临时数据文件
Write-Host "[临时数据文件]" -ForegroundColor Yellow
$otherFiles = @(
    "chinese_names_example.csv",
    "delete_old_tables.sql",
    "COMPACT_LAYOUT_OPTIMIZATION.md"
)

$count = 0
foreach ($file in $otherFiles) {
    if (Test-Path $file) {
        Write-Host "  - $file" -ForegroundColor Gray
        $count++
        $totalCount++
    }
}
Write-Host "  小计：$count 个文件" -ForegroundColor Cyan
Write-Host ""

# 6. Excel 测试文件
Write-Host "[Excel 测试文件]" -ForegroundColor Yellow
$excelFiles = Get-ChildItem -Path . -Filter "*.xlsx" -File -ErrorAction SilentlyContinue
foreach ($file in $excelFiles) {
    if ($file.Name -like "*test*") {
        Write-Host "  - $($file.Name)" -ForegroundColor Gray
        $totalCount++
    }
}
Write-Host "  小计：$($excelFiles.Count) 个文件" -ForegroundColor Cyan
Write-Host ""

# 7. Windows 批处理文件（非必需）
Write-Host "[Windows 批处理文件 - 可选删除]" -ForegroundColor Yellow
$batFiles = Get-ChildItem -Path . -Filter "*.bat" -File -ErrorAction SilentlyContinue
$keepBatFiles = @("restore_db.BAT", "setup_backup.BAT", "backup_auto.BAT", "run_server.BAT", "start_server.bat")

foreach ($file in $batFiles) {
    if ($keepBatFiles -notcontains $file.Name) {
        Write-Host "  - $($file.Name)" -ForegroundColor Gray
        $totalCount++
    }
}

$lnkFiles = Get-ChildItem -Path . -Filter "*.lnk" -File -ErrorAction SilentlyContinue
foreach ($file in $lnkFiles) {
    Write-Host "  - $($file.Name)" -ForegroundColor Gray
    $totalCount++
}
Write-Host "  小计：$($batFiles.Count + $lnkFiles.Count - ($keepBatFiles.Count)) 个文件" -ForegroundColor Cyan
Write-Host ""

# 8. __pycache__ 目录
Write-Host "[__pycache__ 目录]" -ForegroundColor Yellow
$pycacheDirs = Get-ChildItem -Path . -Directory -Filter "__pycache__" -Recurse -ErrorAction SilentlyContinue
Write-Host "  共找到：$($pycacheDirs.Count) 个 __pycache__ 目录" -ForegroundColor Cyan
Write-Host ""

# 总结
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "总计可以删除的文件数：$totalCount" -ForegroundColor Yellow
Write-Host ""

Write-Host "建议操作:" -ForegroundColor Cyan
Write-Host "  1. 运行清理脚本：.\cleanup_before_deploy.ps1" -ForegroundColor White
Write-Host "  2. 或手动删除上述文件" -ForegroundColor White
Write-Host ""

Write-Host "保留的重要文件（不要删除）:" -ForegroundColor Green
Write-Host "  ✓ settings.py / settings_production.py" 
Write-Host "  ✓ .env (但不提交到 Git)"
Write-Host "  ✓ urls.py, manage.py"
Write-Host "  ✓ requirements.txt"
Write-Host "  ✓ docs/ (所有项目文档)"
Write-Host "  ✓ eims_app/ 及所有应用目录"
Write-Host "  ✓ backup_before_phase4.json"
Write-Host ""
