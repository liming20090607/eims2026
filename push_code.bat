@echo off
chcp 65001 >nul
echo ======================================
echo   Git 推送代码到 GitHub/Gitee
echo ======================================
echo.

REM 切换到项目根目录
cd /d "%~dp0"

echo 请选择操作：
echo.
echo 1. 推送到 GitHub
echo 2. 推送到 Gitee
echo 3. 查看 Git 状态
echo 4. 退出
echo.
set /p choice=请输入选项 (1-4): 

if "%choice%"=="1" (
    echo.
    echo 🚀 正在推送到 GitHub...
    call bat\push_to_github.bat
) else if "%choice%"=="2" (
    echo.
    echo 🚀 正在推送到 Gitee...
    call bat\push_to_gitee.bat
) else if "%choice%"=="3" (
    echo.
    echo 📊 Git 状态:
    call bat\check_git.bat
) else if "%choice%"=="4" (
    echo.
    echo 👋 再见！
    exit /b
) else (
    echo.
    echo ❌ 无效选择
)

pause
