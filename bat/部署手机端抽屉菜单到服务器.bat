@echo off
chcp 65001 >nul
echo ======================================
echo 部署手机端抽屉式菜单到服务器
echo ======================================
echo.
echo 说明：
echo 部署抽屉式侧边栏功能
echo - 默认隐藏侧边栏，内容满屏
echo - 点击汉堡菜单展开侧边栏
echo - 点击遮罩层关闭侧边栏
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 正在上传文件...
scp eims_app\templates\base\base.html root@39.106.41.239:/var/www/eims/eims_app/templates/base/base.html
scp static\css\style.css root@39.106.41.239:/var/www/eims/static/css/style.css

echo.
echo 上传完成！正在执行部署命令...
ssh root@39.106.41.239 @"
cd /var/www/eims
source venv/bin/activate

echo '======================================'
echo '步骤 1: 收集静态文件'
echo '======================================'
python manage.py collectstatic --clear --noinput

echo.
echo '======================================'
echo '步骤 2: 设置权限'
echo '======================================'
sudo chown -R admin:admin staticfiles
sudo chmod -R 755 staticfiles

echo.
echo '======================================'
echo '步骤 3: 重启服务'
echo '======================================'
sudo supervisorctl restart eims

echo.
echo '======================================'
echo '步骤 4: 查看服务状态'
echo '======================================'
sudo supervisorctl status eims

echo.
echo '======================================'
echo '部署完成！'
echo '======================================'
"@

echo.
echo ======================================
echo 部署完成！
echo ======================================
echo.
echo 请在手机浏览器中访问：
echo http://39.106.41.239:8000/
echo.
echo 按 Ctrl+F5 强制刷新
echo.
echo 现在可以：
echo 1. 点击汉堡菜单（三）展开侧边栏
echo 2. 点击遮罩层关闭侧边栏
echo 3. 页面默认满屏显示
echo.
pause
