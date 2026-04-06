@echo off
chcp 65001 >nul
echo ======================================
echo 检查 Nginx 配置
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 查看 Nginx 配置文件...
ssh root@39.106.41.239 "cat /etc/nginx/nginx.conf"

echo.
echo ======================================
echo 查看 Nginx 站点配置...
ssh root@39.106.41.239 "ls -la /etc/nginx/conf.d/"

echo.
echo ======================================
echo 完成！
echo ======================================
echo.
pause
