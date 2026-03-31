@echo off
REM ========================================
REM Git 安装检测工具
REM ========================================

echo ========================================
echo   Git 安装检测工具
echo ========================================
echo.

REM 测试 Git 是否可用
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git 已安装
    echo.
    git --version
    echo.
    
    REM 检查 Git 配置
    echo 检查 Git 配置：
    echo ----------------------------------------
    git config --global user.name
    git config --global user.email
    echo ----------------------------------------
    echo.
    
    REM 检查是否在 Git 仓库中
    if exist ".git" (
        echo ✅ 当前目录是 Git 仓库
        echo.
        git status --short
    ) else (
        echo ⚠️  当前目录不是 Git 仓库
        echo.
        echo 是否要初始化 Git 仓库？
        set /p init_git=输入 Y 初始化，输入 N 跳过：
        if /i "%init_git%"=="Y" (
            call :init_git_repo
        )
    )
) else (
    echo ❌ Git 未安装或未添加到 PATH
    echo.
    echo ========================================
    echo   Git 安装指南
    echo ========================================
    echo.
    echo 方法 1：从官网下载安装（推荐）
    echo ----------------------------------------
    echo 1. 访问：https://git-scm.com/download/win
    echo 2. 下载 Windows 版本
    echo 3. 运行安装程序
    echo 4. 安装时选择以下选项：
    echo    - 使用 Git Bash
    echo    - 使用 Windows 默认控制台
    echo    - 使用 Git 附带的工具
    echo    - 使用 Windows 默认的加密库
    echo    - 不换行符自动转换
    echo    - 使用 Windows 默认的终端模拟器
    echo    - 启用文件系统缓存
    echo    - 启用实验性选项
    echo 5. 完成安装后，重新打开 PowerShell
    echo 6. 运行此脚本再次检测
    echo.
    echo 方法 2：使用 GitHub Desktop（包含 Git）
    echo ----------------------------------------
    echo 1. 访问：https://desktop.github.com
    echo 2. 下载并安装 GitHub Desktop
    echo 3. Git 会自动包含在内
    echo.
    echo 方法 3：使用 Scoop 安装（高级用户）
    echo ----------------------------------------
    echo 1. 如果已安装 Scoop
    echo 2. 运行：scoop install git
    echo.
    echo ========================================
)

echo.
echo 按任意键退出...
pause >nul
exit /b

:init_git_repo
echo.
echo 初始化 Git 仓库...
echo ----------------------------------------

REM 检查是否有 .gitignore 文件
if not exist ".gitignore" (
    echo 创建 .gitignore 文件...
    (
        echo venv/
        echo __pycache__/
        echo *.pyc
        echo *.pyo
        echo *.pyd
        echo .Python
        echo db.sqlite3
        echo media/
        echo staticfiles/
        echo .env
        echo *.log
        echo .DS_Store
        echo Thumbs.db
    ) > .gitignore
    echo ✅ .gitignore 已创建
    echo.
)

REM 初始化 Git 仓库
git init
echo ✅ Git 仓库已初始化
echo.

REM 添加所有文件
echo 添加所有文件到 Git...
git add .
echo ✅ 文件已添加
echo.

REM 配置用户信息（如果未配置）
git config --global user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo 配置 Git 用户信息：
    echo ----------------------------------------
    set /p username=请输入用户名（用于 Git 提交）：
    git config --global user.name "%username%"
    
    set /p email=请输入邮箱（用于 Git 提交）：
    git config --global user.email "%email%"
    
    echo ✅ 用户信息已配置
    echo.
)

REM 首次提交
set /p commit_msg=请输入提交信息（默认：Initial commit）：
if "%commit_msg%"=="" set commit_msg=Initial commit

git commit -m "%commit_msg%"
echo ✅ 首次提交完成
echo.

echo 是否创建远程仓库并推送？
set /p create_remote=输入 Y 创建，输入 N 跳过：
if /i "%create_remote%"=="Y" (
    echo.
    echo 请选择远程仓库平台：
    echo 1. GitHub (https://github.com)
    echo 2. Gitee (https://gitee.com)
    echo 3. 其他
    set /p platform_choice=输入选项 (1-3):
    
    if "%platform_choice%"=="1" set repo_url=https://github.com/你的用户名/eims2026.git
    if "%platform_choice%"=="2" set repo_url=https://gitee.com/你的用户名/eims2026.git
    if "%platform_choice%"=="3" set /p repo_url=请输入远程仓库地址：
    
    echo.
    echo 远程仓库地址：%repo_url%
    echo.
    echo 请手动修改上面的地址为实际的仓库地址
    echo 然后执行以下命令：
    echo   git remote add origin %repo_url%
    echo   git push -u origin main
    echo.
)

echo.
echo ✅ Git 仓库初始化完成！
echo.
exit /b
