@echo off
REM ========================================
REM Git 安装检测工具（批处理版本）
REM ========================================

echo ========================================
echo   Git 安装检测工具
echo ========================================
echo.

REM 使用完整路径测试 Git
"C:\Program Files\Git\bin\git.exe" --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git 已安装
    echo.
    "C:\Program Files\Git\bin\git.exe" --version
    echo.
    
    REM 检查 Git 配置
    echo 检查 Git 配置：
    echo ----------------------------------------
    "C:\Program Files\Git\bin\git.exe" config --global user.name
    "C:\Program Files\Git\bin\git.exe" config --global user.email
    echo ----------------------------------------
    echo.
    
    REM 检查是否在 Git 仓库中
    if exist ".git" (
        echo ✅ 当前目录是 Git 仓库
        echo.
        "C:\Program Files\Git\bin\git.exe" status --short
        echo.
        
        echo 是否要初始化提交？
        set /p init_commit=输入 Y 提交所有文件，输入 N 跳过：
        if /i "%init_commit%"=="Y" (
            call :init_commit
        )
    ) else (
        echo ⚠️  当前目录不是 Git 仓库
        echo.
        echo 是否要初始化 Git 仓库？
        set /p init_git=输入 Y 初始化，输入 N 跳过：
        if /i "%init_git%"=="Y" (
            call :init_git_repo
        )
    )
    
    echo.
    echo ========================================
    echo   Git 检测完成！
    echo ========================================
    echo.
) else (
    echo ❌ Git 无法运行
    echo.
    echo Git 已安装但无法运行，请检查：
    echo 1. 重新安装 Git
    echo 2. 确保安装时选择了正确的选项
    echo.
)

echo.
echo 按任意键退出...
pause >nul
exit /b

:init_git_repo
echo.
echo 初始化 Git 仓库...
echo ----------------------------------------

REM 创建 .gitignore 文件
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
"C:\Program Files\Git\bin\git.exe" init
echo ✅ Git 仓库已初始化
echo.

REM 添加所有文件
echo 添加所有文件到 Git...
"C:\Program Files\Git\bin\git.exe" add .
echo ✅ 文件已添加
echo.

REM 配置用户信息
"C:\Program Files\Git\bin\git.exe" config --global user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo 配置 Git 用户信息：
    echo ----------------------------------------
    set /p username=请输入用户名（用于 Git 提交）：
    "C:\Program Files\Git\bin\git.exe" config --global user.name "%username%"
    
    set /p email=请输入邮箱（用于 Git 提交）：
    "C:\Program Files\Git\bin\git.exe" config --global user.email "%email%"
    
    echo ✅ 用户信息已配置
    echo.
)

REM 首次提交
set /p commit_msg=请输入提交信息（默认：Initial commit）：
if "%commit_msg%"=="" set commit_msg=Initial commit

"C:\Program Files\Git\bin\git.exe" commit -m "%commit_msg%"
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
    echo   "C:\Program Files\Git\bin\git.exe" remote add origin %repo_url%
    echo   "C:\Program Files\Git\bin\git.exe" push -u origin main
    echo.
)

echo.
echo ✅ Git 仓库初始化完成！
echo.
exit /b

:init_commit
echo.
echo 提交所有文件...
echo ----------------------------------------

REM 添加所有文件
"C:\Program Files\Git\bin\git.exe" add .
echo ✅ 文件已添加
echo.

REM 提交
set /p commit_msg=请输入提交信息（默认：Update project）：
if "%commit_msg%"=="" set commit_msg=Update project

"C:\Program Files\Git\bin\git.exe" commit -m "%commit_msg%"
echo ✅ 提交完成
echo.

exit /b
