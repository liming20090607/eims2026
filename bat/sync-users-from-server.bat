@echo off
chcp 65001 >nul
echo ======================================
echo 同步云服务器用户账号数据到本地
echo ======================================
echo.
echo 服务器: 39.106.41.239
echo 用户: root
echo.
echo 步骤说明:
echo  1. SSH 登录服务器导出用户数据
echo  2. 下载导出的数据文件到本地
echo  3. 导入数据到本地数据库
echo.
echo 提示：执行过程中需要输入服务器 root 密码
echo.
pause

echo.
echo ======================================
echo 步骤 1: 导出服务器用户数据
echo ======================================
echo.
echo 正在 SSH 登录服务器并导出数据...
echo 请输入服务器 root 密码
echo.

ssh root@39.106.41.239 "cd /var/www/eims && source venv/bin/activate && python manage.py dumpdata auth.User eims_app.UserProfile --indent 2 > /tmp/users_export.json && echo '导出完成' && wc -l /tmp/users_export.json"

echo.
echo ======================================
echo 步骤 2: 下载数据文件到本地
echo ======================================
echo.
echo 正在下载文件...
echo 请输入服务器 root 密码
echo.

if not exist "eims_app\fixtures" mkdir "eims_app\fixtures"

scp root@39.106.41.239:/tmp/users_export.json eims_app\fixtures\users_export.json

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 文件下载成功
) else (
    echo.
    echo ❌ 文件下载失败
    pause
    exit /b 1
)

echo.
echo ======================================
echo 步骤 3: 导入数据到本地数据库
echo ======================================
echo.

cd /d "%~dp0.."
python manage.py loaddata eims_app/fixtures/users_export.json

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 数据导入成功
) else (
    echo.
    echo ❌ 数据导入失败
    pause
    exit /b 1
)

echo.
echo ======================================
echo 步骤 4: 验证导入结果
echo ======================================
echo.

python manage.py shell -c "from django.contrib.auth.models import User; from eims_app.models import UserProfile; print(f'用户账号数: {User.objects.count()}'); print(f'用户资料数: {UserProfile.objects.count()}'); print('\n最新用户:'); [print(f'  - {u.username} | 姓名: {getattr(u.userprofile, \"real_name\", \"-\")}') for u in User.objects.order_by('-id')[:10]]"

echo.
echo ======================================
echo ✅ 用户数据同步完成！
echo ======================================
echo.
echo 现在您可以访问:
echo   http://127.0.0.1:8000/admin/
echo   http://127.0.0.1:8000/user-management/
echo.
pause
