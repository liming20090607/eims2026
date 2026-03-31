@echo off
REM ========================================
REM Git 快速推送工具
REM ========================================

echo ========================================
echo   Git 快速推送工具
echo ========================================
echo.

REM 检查远程仓库
"C:\Program Files\Git\bin\git.exe" remote -v | findstr "origin" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未配置远程仓库
    echo.
    echo 请先运行配置工具：
    echo .\configure_remote.bat
    echo.
    pause
    exit /b 1
)

echo ✅ 远程仓库已配置
"C:\Program Files\Git\bin\git.exe" remote -v
echo.

REM 查看状态
echo 当前状态：
echo ----------------------------------------
"C:\Program Files\Git\bin\git.exe" status --short
echo.

REM 检查是否有变更
"C:\Program Files\Git\bin\git.exe" status --short | findstr "." >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  检测到有文件变更
    echo.
    set /p add_files=是否添加所有变更？(Y/N): 
    if /i "%add_files%"=="Y" (
        "C:\Program Files\Git\bin\git.exe" add .
        echo ✅ 文件已添加
        echo.
        
        set /p commit_msg=请输入提交信息（默认：Update project）：
        if "%commit_msg%"=="" set commit_msg=Update project
        
        "C:\Program Files\Git\bin\git.exe" commit -m "%commit_msg%"
        echo ✅ 提交完成
        echo.
    )
) else (
    echo ✅ 工作目录干净，没有变更
    echo.
)

REM 推送
set /p push_now=是否推送到远程仓库？(Y/N): 
if /i "%push_now%"=="N" goto :end
if /i "%push_now%"=="n" goto :end

echo.
echo 正在推送...
echo ----------------------------------------

"C:\Program Files\Git\bin\git.exe" push
if %errorlevel% equ 0 (
    echo.
    echo ✅ 推送成功！
    echo.
) else (
    echo.
    echo ⚠️  推送失败，尝试指定分支...
    echo.
    
    REM 检查当前分支
    "C:\Program Files\Git\bin\git.exe" branch | findstr "*" > branch_name.tmp
    set /p current_branch=<branch_name.tmp
    set current_branch=%current_branch:* =%
    del branch_name.tmp
    
    echo 当前分支：%current_branch%
    echo.
    
    "C:\Program Files\Git\bin\git.exe" push -u origin %current_branch%
    if %errorlevel% equ 0 (
        echo ✅ 推送成功！
        echo.
    ) else (
        echo ❌ 推送失败
        echo 请检查网络和权限设置
        echo.
    )
)

:end
echo ========================================
echo 按任意键退出...
pause >nul
exit /b
