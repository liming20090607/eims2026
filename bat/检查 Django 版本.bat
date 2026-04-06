@echo off
chcp 65001 >nul
echo ======================================
echo 检查服务器 Django 版本
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 正在检查...
ssh root@39.106.41.239 @"
cd /var/www/eims
source venv/bin/activate

echo '======================================'
echo 'Django 版本信息'
echo '======================================'
python -m django --version

echo.
echo '======================================'
echo 'Python 版本'
echo '======================================'
python --version

echo.
echo '======================================'
echo '已安装的包'
echo '======================================'
pip list | findstr /i django

echo.
echo '======================================'
echo 'settings.py 中的配置'
echo '======================================'
grep -n 'USE_DARK_THEME\|ADMIN_SITE_HEADER' settings.py || echo '未找到相关配置'

echo.
echo '======================================'
echo '静态文件目录'
echo '======================================'
ls -la staticfiles/admin/css/ | head -10

echo.
echo '======================================'
echo '服务状态'
echo '======================================'
sudo supervisorctl status eims
"@

echo.
echo ======================================
echo 检查完成
echo ======================================
echo.
pause
