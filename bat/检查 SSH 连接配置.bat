@echo off
chcp 65001 >nul
echo ======================================
echo 检查 SSH 连接配置
echo ======================================
echo.
echo 正在检查本地配置...
echo.

echo 1. 检查本地 hosts 文件
echo ------------------------------------
findstr /C:"39.106.41.239" C:\Windows\System32\drivers\etc\hosts || echo 未在 hosts 文件中找到 39.106.41.239

echo.
echo 2. 测试网络连接
echo ------------------------------------
ping -n 4 39.106.41.239

echo.
echo 3. 测试 SSH 端口 (8000)
echo ------------------------------------
powershell -Command "Test-NetConnection -ComputerName 39.106.41.239 -Port 8000"

echo.
echo 4. 测试 SSH 端口 (22)
echo ------------------------------------
powershell -Command "Test-NetConnection -ComputerName 39.106.41.239 -Port 22"

echo.
echo ======================================
echo 诊断完成
echo ======================================
echo.
echo 请检查以下项目：
echo 1. 服务器密码是否正确（区分大小写）
echo 2. 服务器是否正在运行
echo 3. SSH 服务是否启动
echo 4. 防火墙设置
echo.

pause
