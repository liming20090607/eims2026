@echo off
chcp 65001 >nul
echo ======================================
echo 上传修复后的 settings.py 到服务器
echo ======================================
echo.
echo 文件说明：
echo   - 已删除无效的 USE_DARK_THEME 配置
echo   - 已添加 Django 4.2.7 兼容的 Admin 配置
echo   - 已修复语法错误
echo.
echo ======================================
echo 请输入服务器密码（root 用户的密码）：
echo ======================================
echo.

echo 正在上传 settings.py...
scp E:\EIMS2026\settings.py root@39.106.41.239:/var/www/eims/

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================
    echo ✅ 上传成功！
    echo ======================================
    echo.
    echo 下一步操作：
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo 1. SSH 登录服务器：
    echo    ssh root@39.106.41.239
    echo.
    echo 2. 验证文件内容：
    echo    cd /var/www/eims
    echo    tail -10 settings.py
    echo.
    echo 3. 检查语法：
    echo    source venv/bin/activate
    echo    python -c "import settings; print('OK')"
    echo.
    echo 4. 重新收集静态文件：
    echo    python manage.py collectstatic --clear --noinput
    echo    python manage.py collectstatic --noinput
    echo.
    echo 5. 重启服务：
    echo    sudo supervisorctl restart eims
    echo.
    echo 6. 访问测试：
    echo    http://39.106.41.239/admin/
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.
    echo 或者，运行另一个脚本自动执行上述步骤：
    echo   bat\修复 Django 版本兼容问题.bat
    echo.
) else (
    echo.
    echo ======================================
    echo ❌ 上传失败，请检查：
    echo   1. 网络连接
    echo   2. 服务器密码
    echo   3. SSH 服务状态
    echo ======================================
)

pause
