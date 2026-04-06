@echo off
chcp 65001 >nul
echo ======================================
echo SSH 登录阿里云服务器 (39.106.41.239)
echo ======================================
echo.
echo 请选择登录方式：
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 1. 使用 admin 用户登录（推荐）⭐⭐⭐⭐⭐
echo    - 适用于日常运维
echo    - 可通过 sudo su - 切换 root
echo.
echo 2. 使用 root 用户登录
echo    - 需要 root 密码
echo    - 直接获得最高权限
echo.
echo 3. 测试网络连接
echo    - 检查服务器是否可达
echo    - 检查端口是否开放
echo.
echo Q. 退出
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set /p choice="请输入选择："

if /i "%choice%"=="1" goto login_admin
if /i "%choice%"=="2" goto login_root
if /i "%choice%"=="3" goto test_connection
if /i "%choice%"=="Q" goto end
if /i "%choice%"=="q" goto end

echo.
echo ❌ 无效输入，请重新运行脚本
pause
goto end

:login_admin
echo.
echo ======================================
echo 使用 admin 用户登录
echo ======================================
echo.
echo 提示：
echo - 输入密码时不会显示字符
echo - 登录后执行 'sudo su -' 可切换 root
echo - 按 Ctrl+D 或输入 exit 退出
echo.
echo 正在连接...
ssh admin@39.106.41.239
goto end

:login_root
echo.
echo ======================================
echo 使用 root 用户登录
echo ======================================
echo.
echo 提示：
echo - 输入密码时不会显示字符
echo - 拥有最高权限，请谨慎操作
echo - 按 Ctrl+D 或输入 exit 退出
echo.
echo 正在连接...
ssh root@39.106.41.239
goto end

:test_connection
echo.
echo ======================================
echo 测试网络连接
echo ======================================
echo.

echo 1. 测试基本连通性...
ping -n 4 39.106.41.239
echo.

echo 2. 测试 SSH 端口 (22)...
powershell -Command "Test-NetConnection -ComputerName 39.106.41.239 -Port 22"
echo.

echo 3. 测试应用端口 (8000)...
powershell -Command "Test-NetConnection -ComputerName 39.106.41.239 -Port 8000"
echo.

echo ======================================
echo 测试结果
echo ======================================
echo.
echo 如果所有测试都通过，说明网络正常
echo 如果失败，请检查：
echo 1. 服务器是否在运行
echo 2. 阿里云安全组设置
echo 3. 防火墙配置
echo.

pause
goto end

:end
