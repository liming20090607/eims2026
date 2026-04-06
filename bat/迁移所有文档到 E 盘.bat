@echo off
chcp 65001 >nul
echo ======================================
echo EIMS 文档整理和迁移工具
echo ======================================
echo.
echo 正在整理和迁移所有文档到 E:\EIMS_Documentation
echo.

:: 设置源目录和目标目录
set SOURCE_DIR=E:\EIMS2026
set TARGET_DIR=E:\EIMS_Documentation

echo 源目录：%SOURCE_DIR%
echo 目标目录：%TARGET_DIR%
echo.

:: 创建子目录
echo 正在创建分类目录...
if not exist "%TARGET_DIR%\01_部署指南" mkdir "%TARGET_DIR%\01_部署指南"
if not exist "%TARGET_DIR%\02_Git 配置" mkdir "%TARGET_DIR%\02_Git 配置"
if not exist "%TARGET_DIR%\03_功能模块" mkdir "%TARGET_DIR%\03_功能模块"
if not exist "%TARGET_DIR%\04_问题修复" mkdir "%TARGET_DIR%\04_问题修复"
if not exist "%TARGET_DIR%\05_移动端优化" mkdir "%TARGET_DIR%\05_移动端优化"
if not exist "%TARGET_DIR%\06_脚本工具" mkdir "%TARGET_DIR%\06_脚本工具"
echo ✅ 目录创建完成
echo.

:: 计数器
set /a total=0
set /a moved=0

echo ======================================
echo 开始迁移文档...
echo ======================================
echo.

:: 1. 部署指南类
echo [1] 迁移部署指南文档...
for %%f in (
    "部署指南_阿里云.md"
    "部署检查清单.md"
    "README_部署说明.md"
    "部署方案_持续集成.md"
    "DEPLOYMENT_CHECKLIST.md"
    "DEPLOYMENT_GUIDE_COMPLETE.md"
    "DEPLOYMENT_CLEANUP_GUIDE.md"
    "阿里云部署指南.md"
    "手动部署步骤.md"
    "PowerShell 部署指南.md"
) do (
    if exist "%SOURCE_DIR%\%%f" (
        echo   移动：%%f
        move "%SOURCE_DIR%\%%f" "%TARGET_DIR%\01_部署指南\" >nul
        set /a moved+=1
    )
)
set /a total+=11
echo.

:: 2. Git 配置类
echo [2] 迁移 Git 配置文档...
for %%f in (
    "Git 部署快速入门.md"
    "Git 安装指南.md"
    "Git 安装成功指南.md"
    "Git 仓库初始化完成.md"
    "Git 远程仓库配置指南.md"
    "配置远程仓库_快速指南.md"
    "Git 配置完成总结.md"
    "🎉Git 配置完成！开始使用.md"
    "README_配置远程仓库.md"
    "✅配置完成！下一步.md"
    "Git 推送解决方案.md"
) do (
    if exist "%SOURCE_DIR%\%%f" (
        echo   移动：%%f
        move "%SOURCE_DIR%\%%f" "%TARGET_DIR%\02_Git 配置\" >nul
        set /a moved+=1
    )
)
set /a total+=11
echo.

:: 3. 功能模块类
echo [3] 迁移功能模块文档...
for %%f in (
    "用户账号管理功能使用指南.md"
    "用户账号管理功能部署说明.md"
    "用户账号管理功能 - 完整修复总结.md"
    "用户账号管理功能 - 所有问题修复总结.md"
    "SMS_AUTH_IMPLEMENTATION.md"
    "SMS_QUICK_START.md"
) do (
    if exist "%SOURCE_DIR%\%%f" (
        echo   移动：%%f
        move "%SOURCE_DIR%\%%f" "%TARGET_DIR%\03_功能模块\" >nul
        set /a moved+=1
    )
)
set /a total+=6
echo.

:: 4. 问题修复类
echo [4] 迁移问题修复文档...
for %%f in (
    "模板路径修复说明.md"
    "URL 命名空间修复说明.md"
    "Django redirect 命名空间修复说明.md"
    "Admin 样式修复方案.md"
    "Django Admin 样式异常 - 完整修复方案.md"
    "Admin 静态文件 404 - 修复方案.md"
    "快速修复 Django Admin 样式.md"
    "Django Admin 样式问题 - 彻底修复方案.md"
    "Django Admin 样式问题 - 版本问题分析.md"
    "Django 版本对比 - 本地 vs 服务器.md"
    "升级服务器到 Django 5.2 - 可行性分析.md"
    "本地 Django 降级指南.md"
    "Django 降级成功报告.md"
    "服务器 Admin 样式问题 - 修复方案.md"
    "DROPDOWN_OTHER_PATTERN_GUIDE.md"
    "FORMULA_CALCULATION_SUMMARY.md"
    "FORMULA_CALCULATION_FIX_SUMMARY.md"
    "PERSONNEL_DROPDOWN_FIX.md"
    "PERSONNEL_DATA_GUIDE.md"
    "QUICK_FIX_PERSONNEL.md"
    "CLEANUP_PLAN.md"
    "CLEANUP_COMPLETE.md"
    "CLEANUP_SUMMARY.md"
    "CLEANUP_COMPLETE_REPORT.md"
) do (
    if exist "%SOURCE_DIR%\%%f" (
        echo   移动：%%f
        move "%SOURCE_DIR%\%%f" "%TARGET_DIR%\04_问题修复\" >nul
        set /a moved+=1
    )
)
set /a total+=24
echo.

:: 5. 移动端优化类
echo [5] 迁移移动端优化文档...
for %%f in (
    "手机端显示优化 - 调整完成.md"
    "手机端满屏显示优化.md"
    "手机端抽屉菜单优化说明.md"
    "手机端智能抽屉菜单优化说明.md"
    "手机端智能抽屉菜单 -2 秒延迟关闭优化.md"
) do (
    if exist "%SOURCE_DIR%\%%f" (
        echo   移动：%%f
        move "%SOURCE_DIR%\%%f" "%TARGET_DIR%\05_移动端优化\" >nul
        set /a moved+=1
    )
)
set /a total+=5
echo.

:: 6. 脚本工具类（.bat 文件）
echo [6] 迁移脚本工具...
for %%f in (
    "deploy_tool.bat"
    "check_git.bat"
    "configure_remote.bat"
    "push.bat"
    "快速配置远程仓库.bat"
    "push_to_github.bat"
    "push_to_gitee.bat"
    "deploy_user_management.bat"
    "手动上传文件.bat"
    "上传文件.bat"
    "上传模板文件.bat"
    "上传所有文件.bat"
    "验证服务器文件.bat"
    "执行部署命令.bat"
    "检查服务器配置.bat"
    "修复 admin 样式.bat"
    "检查 Nginx 配置.bat"
    "快速修复 admin.bat"
    "快速修复 admin 样式.bat"
    "SSH 登录.bat"
    "手机端优化 - 完整部署.bat"
    "修复 admin 静态文件 404.bat"
    "彻底修复 admin 样式.bat"
    "禁用 admin 主题.bat"
    "检查 Django 版本.bat"
    "检查本地 Django 版本.bat"
    "升级服务器到 Django 5.2.bat"
    "快速检查服务器 Django 版本.bat"
    "降级本地 Django 版本.bat"
    "测试本地 Admin 样式.bat"
    "检查服务器 Admin 问题.bat"
    "修复服务器 Admin 样式.bat"
    "深度诊断服务器.bat"
    "重启云服务器.bat"
    "部署手机端抽屉菜单到服务器.bat"
    "部署手机端优化到服务器.bat"
    "部署手机端智能抽屉菜单.bat"
) do (
    if exist "%SOURCE_DIR%\%%f" (
        echo   移动：%%f
        move "%SOURCE_DIR%\%%f" "%TARGET_DIR%\06_脚本工具\" >nul
        set /a moved+=1
    )
)
set /a total+=37
echo.

echo ======================================
echo 迁移完成统计
echo ======================================
echo 处理文件总数：%total%
echo 成功移动文件数：%moved%
echo.
echo 文档库位置：%TARGET_DIR%
echo ======================================
echo.

pause
