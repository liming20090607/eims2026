@echo off
chcp 65001 >nul
echo ======================================
echo 升级服务器到 Django 5.2
echo ======================================
echo.
echo 说明：
echo 将服务器 Django 升级到 5.2 版本
echo 并禁用主题功能以解决样式问题
echo.
echo 警告：
echo 1. 升级前请备份服务器
echo 2. 升级后需要测试所有功能
echo 3. 如遇问题请回滚到 4.2
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 正在执行升级...
ssh root@39.106.41.239 @"
cd /var/www/eims
source venv/bin/activate

echo '======================================'
echo '步骤 1: 查看当前 Django 版本...'
echo '======================================'
python -m django --version

echo.
echo '======================================'
echo '步骤 2: 卸载当前 Django...'
echo '======================================'
pip uninstall -y django

echo.
echo '======================================'
echo '步骤 3: 安装 Django 5.2...'
echo '======================================'
pip install django==5.2

echo.
echo '======================================'
echo '步骤 4: 验证安装...'
echo '======================================'
python -m django --version

echo.
echo '======================================'
echo '步骤 5: 禁用主题功能...'
echo '======================================'

# 检查是否已添加配置
if grep -q 'USE_DARK_THEME' settings.py; then
    echo '主题配置已存在，跳过...'
else
    echo '添加禁用主题配置...'
    echo '' >> settings.py
    echo '# 禁用 Django Admin 主题功能（Django 5.2+）' >> settings.py
    echo 'USE_DARK_THEME = False' >> settings.py
    echo 'ADMIN_SITE_HEADER = \"协同 AI 办公系统\"' >> settings.py
    echo '配置已添加！'
fi

echo.
echo '======================================'
echo '步骤 6: 清空并重新收集静态文件...'
echo '======================================'
python manage.py collectstatic --clear --noinput
python manage.py collectstatic --noinput

echo.
echo '======================================'
echo '步骤 7: 设置权限...'
echo '======================================'
sudo chown -R admin:admin staticfiles
sudo chmod -R 755 staticfiles

echo.
echo '======================================'
echo '步骤 8: 重启服务...'
echo '======================================'
sudo supervisorctl restart eims

echo.
echo '======================================'
echo '步骤 9: 查看服务状态...'
echo '======================================'
sudo supervisorctl status eims

echo.
echo '======================================'
echo '升级完成！'
echo '======================================'
echo.
echo 'Django 版本：5.2'
echo '主题功能：已禁用'
echo '请刷新浏览器：http://39.106.41.239:8000/admin/'
echo '按 Ctrl+F5 强制刷新'
echo.
echo '注意：请测试所有功能确保正常！'
"@

echo.
echo ======================================
echo Django 升级命令已执行！
echo ======================================
echo.
echo 请在浏览器中：
echo 1. 访问：http://39.106.41.239:8000/admin/
echo 2. 按 Ctrl+F5 强制刷新
echo 3. 查看样式是否正常
echo 4. 测试所有功能
echo.
echo 如遇问题，请运行：降级 Django 版本.bat
echo.
pause
