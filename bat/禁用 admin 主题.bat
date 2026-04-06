@echo off
chcp 65001 >nul
echo ======================================
echo 禁用 Django Admin 主题功能
echo ======================================
echo.
echo 说明：
echo Django 5.2 新增了主题切换功能，导致样式异常
echo 此脚本会禁用主题功能，使用经典样式
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 正在修改 settings.py...
ssh root@39.106.41.239 @"
cd /var/www/eims
source venv/bin/activate

echo '步骤 1: 检查是否已添加配置...'
if grep -q 'USE_DARK_THEME' settings.py; then
    echo '配置已存在，跳过...'
else
    echo '添加禁用主题配置...'
    echo '' >> settings.py
    echo '# 禁用 Django Admin 主题功能（Django 5.2+）' >> settings.py
    echo 'USE_DARK_THEME = False' >> settings.py
    echo 'ADMIN_SITE_HEADER = \"协同 AI 办公系统\"' >> settings.py
    echo '配置已添加！'
fi

echo.
echo '步骤 2: 重启服务...'
sudo supervisorctl restart eims

echo.
echo '步骤 3: 查看服务状态...'
sudo supervisorctl status eims

echo.
echo '======================================'
echo '禁用主题完成！'
echo '======================================'
echo.
echo '请刷新浏览器：http://39.106.41.239:8000/admin/'
echo '按 Ctrl+F5 强制刷新'
"@

echo.
echo ======================================
echo 禁用主题命令已执行！
echo ======================================
echo.
echo 请在浏览器中：
echo 1. 访问：http://39.106.41.239:8000/admin/
echo 2. 按 Ctrl+F5 强制刷新
echo 3. 查看黑块是否消失
echo.
pause
