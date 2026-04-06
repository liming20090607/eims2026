@echo off
chcp 65001 >nul
echo ======================================
echo 用户账号管理功能 - 完整文件上传
echo ======================================
echo.
echo 提示：每个文件上传时都需要输入密码
echo 请使用 root 用户的密码
echo.
echo 开始上传文件...
echo.

echo [1/6] 上传 form_user_management.py...
scp eims_app\forms\form_user_management.py root@39.106.41.239:/var/www/eims/eims_app/forms/
if %ERRORLEVEL% EQU 0 (echo   ✅ 成功) else (echo   ❌ 失败)
echo.

echo [2/6] 上传 views_user_management.py...
scp eims_app\views\views_user_management.py root@39.106.41.239:/var/www/eims/eims_app\views/
if %ERRORLEVEL% EQU 0 (echo   ✅ 成功) else (echo   ❌ 失败)
echo.

echo [3/6] 上传 user_management.html...
scp eims_app\templates\eims_app\user_management.html root@39.106.41.239:/var/www/eims/eims_app/templates/eims_app/
if %ERRORLEVEL% EQU 0 (echo   ✅ 成功) else (echo   ❌ 失败)
echo.

echo [4/6] 上传 custom_filters.py...
scp eims_app\templatetags\custom_filters.py root@39.106.41.239:/var/www/eims/eims_app/templatetags/
if %ERRORLEVEL% EQU 0 (echo   ✅ 成功) else (echo   ❌ 失败)
echo.

echo [5/6] 上传 urls.py...
scp eims_app\urls.py root@39.106.41.239:/var/www/eims/eims_app/
if %ERRORLEVEL% EQU 0 (echo   ✅ 成功) else (echo   ❌ 失败)
echo.

echo [6/6] 上传 base.html...
scp eims_app\templates\base\base.html root@39.106.41.239:/var/www/eims/eims_app/templates/base/
if %ERRORLEVEL% EQU 0 (echo   ✅ 成功) else (echo   ❌ 失败)
echo.

echo ======================================
echo 上传完成！
echo ======================================
echo.
echo 下一步：
echo 1. SSH 登录：ssh root@39.106.41.239
echo 2. 执行部署命令：
echo    cd /var/www/eims
echo    source venv/bin/activate
echo    python manage.py collectstatic --noinput
echo    python manage.py check
echo    sudo supervisorctl restart eims
echo.
pause
