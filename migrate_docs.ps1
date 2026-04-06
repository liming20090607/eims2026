# EIMS 文档整理和迁移脚本

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "EIMS 文档整理和迁移工具" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$sourceDir = "E:\EIMS2026"
$targetDir = "E:\EIMS_Documentation"

Write-Host "源目录：$sourceDir" -ForegroundColor Yellow
Write-Host "目标目录：$targetDir" -ForegroundColor Yellow
Write-Host ""

# 创建分类目录
Write-Host "正在创建分类目录..." -ForegroundColor Green
$subdirs = @(
    "01_部署指南",
    "02_Git 配置",
    "03_功能模块",
    "04_问题修复",
    "05_移动端优化",
    "06_脚本工具"
)

foreach ($subdir in $subdirs) {
    $path = Join-Path $targetDir $subdir
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "  ✅ $subdir" -ForegroundColor Green
    }
}
Write-Host ""

# 文件分类映射
$fileCategories = @{
    "01_部署指南" = @(
        "部署指南_阿里云.md", "部署检查清单.md", "README_部署说明.md", "部署方案_持续集成.md",
        "DEPLOYMENT_CHECKLIST.md", "DEPLOYMENT_GUIDE_COMPLETE.md", "DEPLOYMENT_CLEANUP_GUIDE.md",
        "阿里云部署指南.md", "手动部署步骤.md", "PowerShell 部署指南.md"
    )
    "02_Git 配置" = @(
        "Git 部署快速入门.md", "Git 安装指南.md", "Git 安装成功指南.md", "Git 仓库初始化完成.md",
        "Git 远程仓库配置指南.md", "配置远程仓库_快速指南.md", "Git 配置完成总结.md",
        "🎉Git 配置完成！开始使用.md", "README_配置远程仓库.md", "✅配置完成！下一步.md",
        "Git 推送解决方案.md"
    )
    "03_功能模块" = @(
        "用户账号管理功能使用指南.md", "用户账号管理功能部署说明.md", 
        "用户账号管理功能 - 完整修复总结.md", "用户账号管理功能 - 所有问题修复总结.md",
        "SMS_AUTH_IMPLEMENTATION.md", "SMS_QUICK_START.md"
    )
    "04_问题修复" = @(
        "模板路径修复说明.md", "URL 命名空间修复说明.md", "Django redirect 命名空间修复说明.md",
        "Admin 样式修复方案.md", "Django Admin 样式异常 - 完整修复方案.md",
        "Admin 静态文件 404 - 修复方案.md", "快速修复 Django Admin 样式.md",
        "Django Admin 样式问题 - 彻底修复方案.md", "Django Admin 样式问题 - 版本问题分析.md",
        "Django 版本对比 - 本地 vs 服务器.md", "升级服务器到 Django 5.2 - 可行性分析.md",
        "本地 Django 降级指南.md", "Django 降级成功报告.md", "服务器 Admin 样式问题 - 修复方案.md",
        "DROPDOWN_OTHER_PATTERN_GUIDE.md", "FORMULA_CALCULATION_SUMMARY.md",
        "FORMULA_CALCULATION_FIX_SUMMARY.md", "PERSONNEL_DROPDOWN_FIX.md", "PERSONNEL_DATA_GUIDE.md",
        "QUICK_FIX_PERSONNEL.md", "CLEANUP_PLAN.md", "CLEANUP_COMPLETE.md",
        "CLEANUP_SUMMARY.md", "CLEANUP_COMPLETE_REPORT.md"
    )
    "05_移动端优化" = @(
        "手机端显示优化 - 调整完成.md", "手机端满屏显示优化.md", "手机端抽屉菜单优化说明.md",
        "手机端智能抽屉菜单优化说明.md", "手机端智能抽屉菜单 -2 秒延迟关闭优化.md"
    )
    "06_脚本工具" = @(
        "deploy_tool.bat", "check_git.bat", "configure_remote.bat", "push.bat",
        "快速配置远程仓库.bat", "push_to_github.bat", "push_to_gitee.bat",
        "deploy_user_management.bat", "手动上传文件.bat", "上传文件.bat",
        "上传模板文件.bat", "上传所有文件.bat", "验证服务器文件.bat", "执行部署命令.bat",
        "检查服务器配置.bat", "修复 admin 样式.bat", "检查 Nginx 配置.bat",
        "快速修复 admin.bat", "快速修复 admin 样式.bat", "SSH 登录.bat",
        "手机端优化 - 完整部署.bat", "修复 admin 静态文件 404.bat", "彻底修复 admin 样式.bat",
        "禁用 admin 主题.bat", "检查 Django 版本.bat", "检查本地 Django 版本.bat",
        "升级服务器到 Django 5.2.bat", "快速检查服务器 Django 版本.bat",
        "降级本地 Django 版本.bat", "测试本地 Admin 样式.bat", "检查服务器 Admin 问题.bat",
        "修复服务器 Admin 样式.bat", "深度诊断服务器.bat", "重启云服务器.bat",
        "部署手机端抽屉菜单到服务器.bat", "部署手机端优化到服务器.bat",
        "部署手机端智能抽屉菜单.bat"
    )
}

# 统计
$totalFiles = 0
$movedFiles = 0
$failedFiles = 0

# 开始迁移
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "开始迁移文档..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

foreach ($category in $fileCategories.Keys) {
    $files = $fileCategories[$category]
    $categoryPath = Join-Path $targetDir $category
    
    Write-Host "[$category] 迁移文件中..." -ForegroundColor Yellow
    
    foreach ($file in $files) {
        $sourcePath = Join-Path $sourceDir $file
        $totalFiles++
        
        if (Test-Path $sourcePath) {
            try {
                Move-Item -Path $sourcePath -Destination $categoryPath -Force
                Write-Host "  ✅ $file" -ForegroundColor Green
                $movedFiles++
            } catch {
                Write-Host "  ❌ $file (失败：$_)" -ForegroundColor Red
                $failedFiles++
            }
        } else {
            Write-Host "  ⚠️  $file (不存在)" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
}

# 输出统计
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "迁移完成统计" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "处理文件总数：$totalFiles" -ForegroundColor White
Write-Host "成功移动文件数：$movedFiles" -ForegroundColor Green
Write-Host "失败文件数：$failedFiles" -ForegroundColor $(if ($failedFiles -gt 0) {"Red"} else {"Green"})
Write-Host ""
Write-Host "文档库位置：$targetDir" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 打开文档库
$open = Read-Host "是否打开文档库查看？(Y/N)"
if ($open -eq "Y" -or $open -eq "y") {
    explorer.exe $targetDir
}

Write-Host ""
Write-Host "迁移完成！" -ForegroundColor Green
