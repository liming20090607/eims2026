@echo off
chcp 65001 >nul
echo ======================================
echo 彻底修复 Django Admin 样式问题
echo ======================================
echo.
echo 问题诊断：
echo 1. Django Admin 样式完全丢失
echo 2. 页面顶部有 3 个黑块（主题切换按钮）
echo 3. 只有纯 HTML，没有 CSS
echo.
echo 根本原因：
echo Django 5.2 新增了主题切换功能，导致样式加载异常
echo.
echo 解决方案：
echo 1. 禁用 Django 主题功能
echo 2. 重新收集静态文件
echo 3. 重启服务
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 正在执行修复...
ssh root@39.106.41.239 @"
cd /var/www/eims
source venv/bin/activate

echo '======================================'
echo '步骤 1: 修改 settings.py 禁用主题...'
echo '======================================'

# 在 settings.py 末尾添加禁用主题的配置
echo '' >> settings.py
echo '# 禁用 Django Admin 主题功能（Django 5.2+）' >> settings.py
echo 'USE_DARK_THEME = False' >> settings.py
echo 'ADMIN_SITE_HEADER = \"协同 AI 办公系统\"' >> settings.py

echo.
echo '======================================'
echo '步骤 2: 清空并重新收集静态文件...'
echo '======================================'
python manage.py collectstatic --clear --noinput
python manage.py collectstatic --noinput

echo.
echo '======================================'
echo '步骤 3: 设置权限...'
echo '======================================'
sudo chown -R admin:admin staticfiles
sudo chmod -R 755 staticfiles

echo.
echo '======================================'
echo '步骤 4: 重启服务...'
echo '======================================'
sudo supervisorctl restart eims

echo.
echo '======================================'
echo '步骤 5: 查看服务状态...'
echo '======================================'
sudo supervisorctl status eims

echo.
echo '======================================'
echo '修复完成！'
echo '======================================'
echo.
echo '请刷新浏览器：http://39.106.41.239:8000/admin/'
echo '按 Ctrl+F5 强制刷新'
"@

echo.
echo ======================================
echo 修复命令已执行！
echo ======================================
echo.
echo 请在浏览器中：
echo 1. 访问：http://39.106.41.239:8000/admin/
echo 2. 按 Ctrl+F5 强制刷新
echo 3. 查看样式是否正常
echo.
pause
