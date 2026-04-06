@echo off
chcp 65001 >nul
cls

echo.
echo ========================================
echo   Git 远程仓库配置助手
echo ========================================
echo.
echo 当前状态:
echo - Git 仓库：已初始化
echo - 首次提交：已完成
echo - 远程仓库：未配置
echo.
echo ----------------------------------------
echo.

REM 检查是否已配置
"C:\Program Files\Git\bin\git.exe" remote -v | findstr "origin" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  已存在远程仓库配置
    "C:\Program Files\Git\bin\git.exe" remote -v
    echo.
    set /p change=是否修改？(Y/N): 
    if /i "%change%"=="Y" (
        "C:\Program Files\Git\bin\git.exe" remote remove origin
        echo ✅ 已删除原配置
        echo.
    ) else (
        goto :end
    )
)

echo 请选择平台:
echo.
echo 1. GitHub (推荐 - 国际领先平台)
echo 2. Gitee 码云 (推荐 - 国内速度快)
echo 3. GitLab
echo 4. 其他/自定义
echo 5. 跳过配置
echo.

set /p platform=输入选项 (1-5): 

if "%platform%"=="1" goto :github
if "%platform%"=="2" goto :gitee
if "%platform%"=="3" goto :gitlab
if "%platform%"=="4" goto :custom
if "%platform%"=="5" goto :end

echo ❌ 无效选项
pause
goto :end

:github
echo.
echo ========================================
echo   创建 GitHub 仓库
echo ========================================
echo.
echo 步骤:
echo 1. 访问：https://github.com/new
echo 2. 仓库名：eims2026
echo 3. 选择 Private 或 Public
echo 4. 不要勾选任何初始化选项
echo 5. 点击 Create repository
echo.
echo 复制仓库地址 (HTTPS):
echo 格式：https://github.com/用户名/eims2026.git
echo.
goto :input_url

:gitee
echo.
echo ========================================
echo   创建 Gitee 仓库
echo ========================================
echo.
echo 步骤:
echo 1. 访问：https://gitee.com/new
echo 2. 仓库名：eims2026
echo 3. 选择私有或公开
echo 4. 不要勾选任何初始化选项
echo 5. 点击 创建
echo.
echo 复制仓库地址 (HTTPS):
echo 格式：https://gitee.com/用户名/eims2026.git
echo.
goto :input_url

:gitlab
echo.
echo ========================================
echo   创建 GitLab 仓库
echo ========================================
echo.
echo 步骤:
echo 1. 访问：https://gitlab.com/projects/new
echo 2. 项目名：eims2026
echo 3. 选择 Private 或 Public
echo 4. 不要勾选 Initialize with README
echo 5. 点击 Create project
echo.
echo 复制仓库地址 (HTTPS):
echo 格式：https://gitlab.com/用户名/eims2026.git
echo.
goto :input_url

:custom
echo.
echo ========================================
echo   自定义仓库
echo ========================================
echo.

:input_url
set /p url=请输入仓库地址：
if "%url%"=="" (
    echo ❌ 地址不能为空
    goto :input_url
)

echo.
echo 正在配置...
"C:\Program Files\Git\bin\git.exe" remote add origin %url%
if %errorlevel% neq 0 (
    echo ❌ 配置失败
    pause
    goto :end
)

echo ✅ 配置成功!
echo.
"C:\Program Files\Git\bin\git.exe" remote -v
echo.

set /p push=是否立即推送？(Y/N): 
if /i "%push%"=="N" goto :end
if /i "%push%"=="n" goto :end

echo.
echo 正在推送代码...
"C:\Program Files\Git\bin\git.exe" push -u origin master
if %errorlevel% equ 0 (
    echo.
    echo ✅ 推送成功!
    echo.
) else (
    echo.
    echo ⚠️  推送到 master 失败，尝试推送到 main...
    "C:\Program Files\Git\bin\git.exe" branch -M main
    "C:\Program Files\Git\bin\git.exe" push -u origin main
    if %errorlevel% equ 0 (
        echo.
        echo ✅ 推送成功!
        echo.
    ) else (
        echo.
        echo ❌ 推送失败
        echo 可能原因:
        echo - 远程仓库不为空
        echo - 权限问题
        echo - 网络问题
        echo.
        echo 请检查后手动执行:
        echo git push -u origin master
        echo.
    )
)

:end
echo.
echo ========================================
echo   配置完成!
echo ========================================
echo.
echo 下一步:
echo 1. 修改代码后：git add . ^&^& git commit -m "说明" ^&^& git push
echo 2. 使用工具：push.bat
echo 3. 查看状态：git status
echo.
echo 按任意键退出...
pause >nul
exit /b
