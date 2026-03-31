@echo off
REM ========================================
REM EIMS Git 快速部署工具 - Windows 版本
REM ========================================

echo ========================================
echo   EIMS 自动部署工具
echo ========================================
echo.

REM 配置服务器信息（请修改为你的实际信息）
set SERVER_IP=你的服务器 IP
set SERVER_USER=root
set SERVER_PATH=/var/www/eims

echo 请选择操作：
echo.
echo 1. 初始化 Git 仓库（首次使用）
echo 2. 提交并推送代码
echo 3. 远程部署到服务器
echo 4. 查看 Git 状态
echo 5. 查看 Git 日志
echo 6. 退出
echo.
set /p choice=请输入选项 (1-6): 

if "%choice%"=="1" goto init_git
if "%choice%"=="2" goto push_code
if "%choice%"=="3" goto deploy
if "%choice%"=="4" goto status
if "%choice%"=="5" goto log
if "%choice%"=="6" goto end

:init_git
echo.
echo ========================================
echo   初始化 Git 仓库
echo ========================================
echo.
git init
git add .
git commit -m "Initial commit - EIMS project"
echo.
echo 现在请创建 GitHub/Gitee 仓库，然后执行：
echo git remote add origin 你的仓库地址
echo git push -u origin main
echo.
pause
goto menu

:push_code
echo.
echo ========================================
echo   提交并推送代码
echo ========================================
echo.
set /p message=请输入提交信息：
git add .
git commit -m "%message%"
git push origin main
echo.
echo ✅ 代码已推送！
echo.
set /p deploy_now=是否立即部署到服务器？(Y/N): 
if /i "%deploy_now%"=="Y" goto deploy
goto menu

:deploy
echo.
echo ========================================
echo   部署到服务器 (%SERVER_IP%)
echo ========================================
echo.
ssh %SERVER_USER%@%SERVER_IP% "cd %SERVER_PATH% && source venv/bin/activate && python manage.py migrate && python manage.py collectstatic --noinput && sudo systemctl restart eims && echo ✅ 部署完成！"
echo.
pause
goto menu

:status
echo.
echo ========================================
echo   Git 状态
echo ========================================
echo.
git status
echo.
pause
goto menu

:log
echo.
echo ========================================
echo   Git 提交日志
echo ========================================
echo.
git log --oneline -10
echo.
pause
goto menu

:end
echo.
echo 再见！
echo.
exit /b

:menu
