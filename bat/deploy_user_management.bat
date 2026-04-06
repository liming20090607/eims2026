@echo off
chcp 65001 >nul
echo ======================================
echo 部署用户账号管理功能
echo ======================================
echo.
echo 📦 开始部署到生产服务器...
echo.

set SERVER_IP=39.106.41.239
set SERVER_USER=admin
set PROJECT_PATH=/var/www/eims

echo 1️⃣  准备部署文件...
echo.

:: 创建临时目录
set DEPLOY_DIR=%TEMP%\eims_user_mgmt_deploy
if not exist "%DEPLOY_DIR%" mkdir "%DEPLOY_DIR%"

:: 复制文件
echo 复制文件到临时目录...
xcopy /E /I /Y eims_app\forms\form_user_management.py "%DEPLOY_DIR%\eims_app\forms\"
xcopy /E /I /Y eims_app\views\views_user_management.py "%DEPLOY_DIR%\eims_app\views\"
xcopy /E /I /Y eims_app\templates\eims_app\user_management.html "%DEPLOY_DIR%\eims_app\templates\eims_app\"
xcopy /E /I /Y eims_app\templatetags\custom_filters.py "%DEPLOY_DIR%\eims_app\templatetags\"
xcopy /E /I /Y eims_app\urls.py "%DEPLOY_DIR%\eims_app\"
xcopy /E /I /Y eims_app\templates\base\base.html "%DEPLOY_DIR%\eims_app\templates\base\"

echo.
echo 2️⃣  上传文件到服务器...
echo.

:: 使用 scp 上传（需要安装 Git Bash 或 WSL）
cd "%DEPLOY_DIR%"
scp -r * %SERVER_USER%@%SERVER_IP%:%PROJECT_PATH%/

if %ERRORLEVEL% EQU 0 (
    echo   ✓ 文件上传成功
) else (
    echo   ✗ 文件上传失败
    pause
    exit /b 1
)

echo.
echo 3️⃣  在服务器上执行部署命令...
echo.

:: SSH 连接执行命令
ssh %SERVER_USER%@%SERVER_IP% "cd %PROJECT_PATH%; source venv/bin/activate; python manage.py collectstatic --noinput; python manage.py check; sudo supervisorctl restart eims; sudo supervisorctl status eims"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================
    echo ✅ 部署成功！
    echo ======================================
    echo.
    echo  访问地址：
    echo    http://xietongai.com.cn/user-management/
    echo.
    echo 🔐 登录信息：
    echo    用户名：admin
    echo    密码：Admin2026!
    echo.
) else (
    echo.
    echo ======================================
    echo ❌ 部署失败！
    echo ======================================
    pause
    exit /b 1
)

:: 清理临时文件
rmdir /S /Q "%DEPLOY_DIR%"

echo 📝 详细说明请查看：用户账号管理功能使用指南.md
pause
