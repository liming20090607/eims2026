@echo off
chcp 65001 >nul
echo ======================================
echo 上传用户账号管理模板文件
echo ======================================
echo.
echo 提示：需要输入服务器密码（root 用户的密码）
echo.

echo 正在上传 user_management.html...
scp eims_app\templates\eims_app\user_management.html root@39.106.41.239:/var/www/eims/eims_app/templates/eims_app/

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================
    echo ✅ 上传成功！
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
) else (
    echo.
    echo ======================================
    echo ❌ 上传失败！
    echo ======================================
    echo.
    echo 请检查：
    echo 1. 密码是否正确
    echo 2. 服务器目录是否存在
    echo 3. 网络连接是否正常
    echo.
)

pause
