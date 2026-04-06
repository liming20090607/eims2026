@echo off
REM ========================================
REM Git 远程仓库配置助手
REM ========================================

echo ========================================
echo   Git 远程仓库配置助手
echo ========================================
echo.

REM 检查 Git 是否存在
"C:\Program Files\Git\bin\git.exe" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git 未安装或无法运行
    pause
    exit /b 1
)

echo ✅ Git 已安装
echo.

REM 检查是否在 Git 仓库中
if not exist ".git" (
    echo ❌ 当前目录不是 Git 仓库
    echo 请先运行：git init
    pause
    exit /b 1
)

echo ✅ 当前目录是 Git 仓库
echo.

REM 检查是否已配置远程
"C:\Program Files\Git\bin\git.exe" remote -v | findstr "origin" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  已存在远程仓库配置：
    "C:\Program Files\Git\bin\git.exe" remote -v
    echo.
    set /p change_remote=是否要修改远程仓库地址？(Y/N): 
    if /i not "%change_remote%"=="N" (
        "C:\Program Files\Git\bin\git.exe" remote remove origin
        echo ✅ 已删除原有远程仓库配置
        echo.
    ) else (
        goto :show_info
    )
)

echo 请选择远程仓库平台：
echo ----------------------------------------
echo 1. GitHub (https://github.com)
echo 2. Gitee 码云 (https://gitee.com)
echo 3. GitLab (https://gitlab.com)
echo 4. 其他/自定义
echo 5. 跳过配置
echo.
set /p platform=请输入选项 (1-5): 

if "%platform%"=="1" goto :github
if "%platform%"=="2" goto :gitee
if "%platform%"=="3" goto :gitlab
if "%platform%"=="4" goto :custom
if "%platform%"=="5" goto :end

:github
echo.
echo ========================================
echo   GitHub 仓库创建指南
echo ========================================
echo.
echo 请按以下步骤操作：
echo.
echo 1. 访问：https://github.com/new
echo 2. 输入仓库名：eims2026
echo 3. 选择可见性：
echo    - Private（私有，仅自己可见）
echo    - Public（公开，所有人可见）
echo 4. 不要勾选 "Add a README file"
echo 5. 不要勾选 "Add .gitignore"
echo 6. 不要勾选 "Choose a license"
echo 7. 点击 "Create repository"
echo.
echo 创建完成后，复制仓库地址（HTTPS）：
echo 格式：https://github.com/你的用户名/eims2026.git
echo.
set /p repo_url=请输入仓库地址：
if "%repo_url%"=="" (
    echo ❌ 未输入地址
    goto :github
)
goto :set_remote

:gitee
echo.
echo ========================================
echo   Gitee 仓库创建指南
echo ========================================
echo.
echo 请按以下步骤操作：
echo.
echo 1. 访问：https://gitee.com/new
echo 2. 输入仓库名：eims2026
echo 3. 选择可见性：
echo    - 私有（仅自己可见）
echo    - 公开（所有人可见）
echo 4. 不要勾选 "初始化 README"
echo 5. 不要勾选 "添加 .gitignore"
echo 6. 不要勾选 "开源许可协议"
echo 7. 点击 "创建"
echo.
echo 创建完成后，复制仓库地址（HTTPS）：
echo 格式：https://gitee.com/你的用户名/eims2026.git
echo.
set /p repo_url=请输入仓库地址：
if "%repo_url%"=="" (
    echo ❌ 未输入地址
    goto :gitee
)
goto :set_remote

:gitlab
echo.
echo ========================================
echo   GitLab 仓库创建指南
echo ========================================
echo.
echo 请按以下步骤操作：
echo.
echo 1. 访问：https://gitlab.com/projects/new
echo 2. 输入项目名：eims2026
echo 3. 选择可见性：
echo    - Private（私有）
echo    - Public（公开）
echo 4. 不要勾选 "Initialize repository with README"
echo 5. 点击 "Create project"
echo.
echo 创建完成后，复制仓库地址（HTTPS）：
echo 格式：https://gitlab.com/你的用户名/eims2026.git
echo.
set /p repo_url=请输入仓库地址：
if "%repo_url%"=="" (
    echo ❌ 未输入地址
    goto :gitlab
)
goto :set_remote

:custom
echo.
echo ========================================
echo   自定义远程仓库
echo ========================================
echo.
set /p repo_url=请输入远程仓库地址：
if "%repo_url%"=="" (
    echo ❌ 未输入地址
    goto :custom
)
goto :set_remote

:set_remote
echo.
echo 正在配置远程仓库...
echo 地址：%repo_url%
echo.

"C:\Program Files\Git\bin\git.exe" remote add origin %repo_url%
if %errorlevel% neq 0 (
    echo ❌ 配置失败
    echo 可能的原因：
    echo 1. 地址格式错误
    echo 2. 远程仓库已存在
    echo 3. 网络问题
    echo.
    pause
    exit /b 1
)

echo ✅ 远程仓库配置成功！
echo.
"C:\Program Files\Git\bin\git.exe" remote -v
echo.

REM 询问是否立即推送
set /p push_now=是否立即推送到远程仓库？(Y/N): 
if /i "%push_now%"=="N" goto :show_info
if /i "%push_now%"=="n" goto :show_info

echo.
echo 正在推送代码...
echo.

REM 推送代码
"C:\Program Files\Git\bin\git.exe" push -u origin master
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  推送失败，尝试推送到 main 分支...
    "C:\Program Files\Git\bin\git.exe" branch -M main
    "C:\Program Files\Git\bin\git.exe" push -u origin main
    if %errorlevel% neq 0 (
        echo.
        echo ❌ 推送失败
        echo 可能的原因：
        echo 1. 远程仓库不为空
        echo 2. 权限问题
        echo 3. 网络问题
        echo.
        echo 请检查远程仓库是否为空，然后手动执行：
        echo git push -u origin master
        echo.
        goto :show_info
    )
)

echo.
echo ✅ 推送成功！
echo.

:show_info
echo ========================================
echo   配置完成！
echo ========================================
echo.
echo 远程仓库信息：
"C:\Program Files\Git\bin\git.exe" remote -v
echo.
echo 当前分支：
"C:\Program Files\Git\bin\git.exe" branch
echo.
echo ========================================
echo   下一步操作
echo ========================================
echo.
echo 1. 在本地修改代码后：
echo    git add .
echo    git commit -m "修改说明"
echo    git push
echo.
echo 2. 使用部署工具：
echo    .\deploy_tool.bat
echo.
echo 3. 查看状态：
echo    git status
echo.
echo 4. 查看日志：
echo    git log --oneline
echo.
echo ========================================
echo.

:end
echo 按任意键退出...
pause >nul
exit /b
