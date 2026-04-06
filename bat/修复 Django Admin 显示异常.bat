@echo off
chcp 65001 >nul
echo ======================================
echo 修复 Django Admin 后台显示异常
echo ======================================
echo.
echo 问题诊断：
echo   - 本地开发：Django 5.2
echo   - 服务器：Django 4.2.7
echo   - 不兼容配置：USE_DARK_THEME（仅 Django 5.2+ 支持）
echo.
echo 解决方案：
echo   1. 上传修复后的 settings.py
echo   2. SSH 登录并重新收集静态文件
echo   3. 重启服务
echo.
echo ======================================
echo 请选择执行方式：
echo ======================================
echo 1. 自动上传并修复（推荐）⭐⭐⭐⭐⭐
echo 2. 手动上传 settings.py
echo 3. 查看修复步骤说明
echo Q. 退出
echo ======================================
echo.

set /p choice="请输入选择："

if /i "%choice%"=="1" goto auto_fix
if /i "%choice%"=="2" goto manual_upload
if /i "%choice%"=="3" goto show_steps
if /i "%choice%"=="Q" goto end
if /i "%choice%"=="q" goto end

echo.
echo ❌ 无效输入，请重新运行脚本
pause
goto end

:auto_fix
echo.
echo ======================================
echo 自动上传并修复
echo ======================================
echo.

echo 正在上传 settings.py...
scp E:\EIMS2026\settings.py admin@39.106.41.239:/var/www/eims/

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 上传失败，请检查：
    echo   1. admin 用户是否可以 SSH 登录
    echo   2. 密码是否正确
    echo   3. 网络连接是否正常
    echo.
    pause
    goto end
)

echo.
echo ✅ settings.py 上传成功！
echo.
echo ======================================
echo 下一步操作
echo ======================================
echo.
echo 请 SSH 登录服务器并执行以下命令：
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ssh admin@39.106.41.239
echo.
echo # 登录后切换到 root
echo sudo su -
echo.
echo # 进入项目目录
echo cd /var/www/eims
echo source venv/bin/activate
echo.
echo # 验证 settings.py 语法
echo python -c "import settings; print('OK')"
echo.
echo # 重新收集静态文件
echo python manage.py collectstatic --clear --noinput
echo python manage.py collectstatic --noinput
echo.
echo # 重启服务
echo supervisorctl restart eims
echo.
echo # 访问测试
echo # http://39.106.41.239/admin/
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 或者，运行一键修复脚本：
echo   bat\修复 Django 版本兼容问题.bat
echo.
pause
goto end

:manual_upload
echo.
echo ======================================
echo 手动上传 settings.py
echo ======================================
echo.

echo 方法 1：使用 SCP 上传
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo scp E:\EIMS2026\settings.py admin@39.106.41.239:/var/www/eims/
echo.

echo 方法 2：使用 FTP/SFTP 工具
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 1. 打开 FileZilla 或其他 FTP 客户端
echo 2. 连接到服务器：39.106.41.239
echo 3. 用户名：admin
echo 4. 上传文件：settings.py → /var/www/eims/
echo.

echo 方法 3：通过 SSH 复制粘贴
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 1. SSH 登录：ssh admin@39.106.41.239
echo 2. sudo su - 切换到 root
echo 3. cd /var/www/eims
echo 4. vi settings.py
echo 5. 删除所有内容（dd 或 :%d）
echo 6. 粘贴新内容（按 i 进入插入模式，粘贴，按 ESC，:wq 保存）
echo.

pause
goto end

:show_steps
echo.
echo ======================================
echo 完整修复步骤
echo ======================================
echo.

echo 📋 修复流程
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 第 1 步：上传修复后的 settings.py
echo   - 已修复无效的 USE_DARK_THEME 配置
echo   - 使用 Django 4.2.7 兼容的 Admin 配置
echo.
echo 第 2 步：SSH 登录服务器
echo   ssh admin@39.106.41.239
echo.
echo 第 3 步：重新收集静态文件
echo   cd /var/www/eims
echo   source venv/bin/activate
echo   python manage.py collectstatic --clear --noinput
echo   python manage.py collectstatic --noinput
echo.
echo 第 4 步：重启 Gunicorn 服务
echo   supervisorctl restart eims
echo.
echo 第 5 步：验证修复
echo   访问：http://39.106.41.239/admin/
echo   按 Ctrl+F5 强制刷新
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✅ 预期结果：
echo   - Admin 后台样式正常显示
echo   - 顶部标题显示"协同 AI 办公系统"
echo   - 无黑块、无乱码
echo.

pause
goto end

:end
