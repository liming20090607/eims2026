@echo off
chcp 65001 >nul
echo ======================================
echo 检查服务器配置
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 1. 检查 Nginx 配置...
ssh root@39.106.41.239 "cat /etc/nginx/nginx.conf 2>/dev/null || echo 'Nginx 未安装'"

echo.
echo ======================================
echo 2. 检查 Supervisor 状态...
ssh root@39.106.41.239 "sudo supervisorctl status eims"

echo.
echo ======================================
echo 3. 检查防火墙配置...
ssh root@39.106.41.239 "sudo firewall-cmd --list-all"

echo.
echo ======================================
echo 完成！
echo ======================================
echo.
echo 如果 Nginx 未安装，请使用 IP:端口方式访问：
echo http://39.106.41.239:8000/user-management/
echo.
pause
