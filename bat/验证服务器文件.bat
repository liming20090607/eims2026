@echo off
chcp 65001 >nul
echo ======================================
echo 验证服务器文件结构
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 查看 eims_app 目录结构...
ssh root@39.106.41.239 "ls -la /var/www/eims/eims_app/"

echo.
echo ======================================
echo 查看 forms 文件夹...
ssh root@39.106.41.239 "ls -la /var/www/eims/eims_app/forms/"

echo.
echo ======================================
echo 查看 views 文件夹...
ssh root@39.106.41.239 "ls -la /var/www/eims/eims_app/views/"

echo.
echo ======================================
echo 完成！
echo ======================================
echo.
echo 您看到服务器上已经有很多文件了吧？
echo 所以我们只需要上传新增的 6 个文件！
echo.
pause
