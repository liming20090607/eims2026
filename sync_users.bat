@echo off
chcp 65001 >nul
echo ======================================
echo 同步用户账号数据从云服务器到本地
echo ======================================
echo.
echo 服务器: 39.106.41.239
echo 功能: 导出用户数据并导入到本地数据库
echo.
echo 提示：执行过程中需要输入服务器 root 密码
echo.
pause

echo.
echo [步骤 1/3] 导出服务器用户数据
echo ======================================
echo.
echo 正在 SSH 登录服务器并导出数据...
echo 请输入服务器 root 密码
echo.

ssh root@39.106.41.239 "cd /var/www/eims && source venv/bin/activate && python manage.py dumpdata auth.User auth.User.groups auth.User.user_permissions --indent 2 > /tmp/users_export.json && echo '导出完成' && wc -l /tmp/users_export.json"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ======================================
    echo 导出失败！请检查：
    echo 1. 网络连接是否正常
    echo 2. SSH 密码是否正确
    echo 3. 服务器是否可访问
    echo ======================================
    pause
    exit /b 1
)

echo.
echo [步骤 2/3] 下载数据文件到本地
echo ======================================
echo.
echo 正在下载文件...
echo 请输入服务器 root 密码
echo.

if not exist "fixtures" mkdir "fixtures"

scp root@39.106.41.239:/tmp/users_export.json fixtures\users_export.json

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ======================================
    echo 下载失败！
    echo ======================================
    pause
    exit /b 1
)

echo.
echo ✅ 文件下载成功

echo.
echo [步骤 3/3] 导入数据到本地数据库
echo ======================================
echo.

python manage.py loaddata fixtures\users_export.json

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ======================================
    echo 导入失败！
    echo ======================================
    pause
    exit /b 1
)

echo.
echo [验证] 检查导入结果
echo ======================================
echo.

python manage.py shell -c "from django.contrib.auth.models import User; print(f'用户总数: {User.objects.count()}'); users = User.objects.order_by('-id')[:5]; print('\n最新5个用户:'); [print(f'  - {u.username} (ID:{u.id})') for u in users]"

echo.
echo ======================================
echo ✅ 用户数据同步完成！
echo ======================================
echo.
echo 现在您可以：
echo 1. 访问本地用户管理页面: http://127.0.0.1:8000/user-management/
echo 2. 访问 Django Admin: http://127.0.0.1:8000/admin/
echo.
echo 清理临时文件...
if exist "fixtures\users_export.json" del "fixtures\users_export.json"
echo.
pause
