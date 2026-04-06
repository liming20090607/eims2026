@echo off
chcp 65001 >nul
echo ======================================
echo 手动部署 - 上传文件到服务器
echo ======================================
echo.
echo 📤 开始上传文件...
echo.

set SERVER_IP=39.106.41.239
set SERVER_USER=root
set PROJECT_PATH=/var/www/eims

echo 提示：需要输入服务器密码（root 用户的密码）
echo.

:: 1. 上传表单文件
echo [1/6] 上传 form_user_management.py...
scp eims_app\forms\form_user_management.py %SERVER_USER%@%SERVER_IP%:%PROJECT_PATH%/eims_app/forms/
if %ERRORLEVEL% NEQ 0 ( echo   ✗ 失败！ & pause & exit /b 1 ) else echo   ✓ 成功

:: 2. 上传视图文件
echo [2/6] 上传 views_user_management.py...
scp eims_app\views\views_user_management.py %SERVER_USER%@%SERVER_IP%:%PROJECT_PATH%/eims_app/views/
if %ERRORLEVEL% NEQ 0 ( echo   ✗ 失败！ & pause & exit /b 1 ) else echo   ✓ 成功

:: 3. 上传模板文件
echo [3/6] 上传 user_management.html...
scp eims_app\templates\eims_app\user_management.html %SERVER_USER%@%SERVER_IP%:%PROJECT_PATH%/eims_app/templates/eims_app/
if %ERRORLEVEL% NEQ 0 ( echo   ✗ 失败！ & pause & exit /b 1 ) else echo   ✓ 成功

:: 4. 上传模板标签文件
echo [4/6] 上传 custom_filters.py...
scp eims_app\templatetags\custom_filters.py %SERVER_USER%@%SERVER_IP%:%PROJECT_PATH%/eims_app/templatetags/
if %ERRORLEVEL% NEQ 0 ( echo   ✗ 失败！ & pause & exit /b 1 ) else echo   ✓ 成功

:: 5. 上传 URL 配置文件
echo [5/6] 上传 urls.py...
scp eims_app\urls.py %SERVER_USER%@%SERVER_IP%:%PROJECT_PATH%/eims_app/
if %ERRORLEVEL% NEQ 0 ( echo   ✗ 失败！ & pause & exit /b 1 ) else echo   ✓ 成功

:: 6. 上传基础模板文件
echo [6/6] 上传 base.html...
scp eims_app\templates\base\base.html %SERVER_USER%@%SERVER_IP%:%PROJECT_PATH%/eims_app/templates/base/
if %ERRORLEVEL% NEQ 0 ( echo   ✗ 失败！ & pause & exit /b 1 ) else echo   ✓ 成功

echo.
echo ======================================
echo ✅ 所有文件上传成功！
echo ======================================
echo.
echo 下一步：
echo 1. SSH 登录服务器：ssh root@39.106.41.239
echo 2. 执行部署命令：
echo    cd /var/www/eims
echo    source venv/bin/activate
echo    python manage.py collectstatic --noinput
echo    python manage.py check
echo    sudo supervisorctl restart eims
echo.
echo 详细说明请查看：手动部署步骤.md
echo.
pause