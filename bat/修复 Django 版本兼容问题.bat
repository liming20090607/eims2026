@echo off
chcp 65001 >nul
echo ======================================
echo 修复 Django 版本兼容问题
echo ======================================
echo.
echo 问题诊断：
echo   - 本地开发：Django 5.2
echo   - 服务器：Django 4.2.7
echo   - 不兼容配置：USE_DARK_THEME（仅 Django 5.2+ 支持）
echo.
echo 解决方案：
echo   1. 删除不兼容的 USE_DARK_THEME 配置
echo   2. 使用 Django 4.2 兼容的 Admin 配置
echo   3. 重新收集静态文件
echo   4. 重启服务
echo.
echo ======================================
echo 请输入服务器密码（root 用户的密码）：
echo ======================================
echo.

echo 正在连接服务器并执行修复...
ssh root@39.106.41.239 @"
cd /var/www/eims
source venv/bin/activate

echo '======================================'
echo '步骤 1: 备份当前配置...'
echo '======================================'
BACKUP_FILE=\"settings.py.backup.\$(date +%%Y%%m%%d_%%H%%M%%S)\"
cp settings.py \"\$BACKUP_FILE\"
echo \"已备份：\$BACKUP_FILE\"

echo.
echo '======================================'
echo '步骤 2: 修复 settings.py...'
echo '======================================'

# 删除无效的末尾行
sed -i '/^USE_DARK_THEME/d' settings.py
sed -i \"/^'''\\\$/d\" settings.py
sed -i \"/^'# 禁用 Django Admin/d\" settings.py

# 确保添加正确的配置（如果不存在）
if ! grep -q 'ADMIN_SITE_HEADER' settings.py; then
    echo '' >> settings.py
    echo '# Django Admin 配置（4.2.7 兼容）' >> settings.py
    echo \"ADMIN_SITE_HEADER = '协同 AI 办公系统'\" >> settings.py
    echo \"ADMIN_SITE_TITLE = '协同 AI 办公系统 - 后台管理'\" >> settings.py
    echo '已添加兼容配置！'
else
    echo 'ADMIN_SITE_HEADER 配置已存在，跳过...'
fi

echo.
echo '查看 settings.py 末尾内容:'
tail -10 settings.py

echo.
echo '======================================'
echo '步骤 3: 检查 Django 配置语法...'
echo '======================================'
python -c \"import settings; print('✅ settings.py 语法正确')\" || echo '❌ settings.py 有语法错误！'

echo.
echo '======================================'
echo '步骤 4: 清空并重新收集静态文件...'
echo '======================================'
echo '清空旧的静态文件...'
python manage.py collectstatic --clear --noinput

echo.
echo '重新收集静态文件...'
python manage.py collectstatic --noinput

echo.
echo '检查静态文件目录:'
ls -la staticfiles/ | head -10

echo.
echo '检查 Admin CSS 文件:'
if [ -f staticfiles/admin/css/base.css ]; then
    echo '✅ base.css 存在'
    ls -la staticfiles/admin/css/base.css
else
    echo '❌ base.css 不存在！'
fi

echo.
echo '======================================'
echo '步骤 5: 设置权限...'
echo '======================================'
chown -R admin:admin staticfiles
chmod -R 755 staticfiles

echo '权限设置完成'
ls -ld staticfiles

echo.
echo '======================================'
echo '步骤 6: 重启服务...'
echo '======================================'
sudo supervisorctl restart eims

echo.
echo '等待服务启动...'
sleep 3

echo.
echo '======================================'
echo '步骤 7: 查看服务状态...'
echo '======================================'
sudo supervisorctl status eims

echo.
echo '======================================'
echo '步骤 8: 检查 Django 版本...'
echo '======================================'
python -m django --version

echo.
echo '======================================'
echo '✅ 修复完成！'
echo '======================================'
echo.
echo '请按以下步骤验证：'
echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
echo '1. 打开浏览器访问：'
echo '   http://39.106.41.239/admin/'
echo ''
echo '2. 按 Ctrl+F5 强制刷新缓存'
echo ''
echo '3. 检查以下内容：'
echo '   ✅ 页面样式正常显示（非纯 HTML）'
echo '   ✅ 顶部标题显示\"协同 AI 办公系统\"'
echo '   ✅ 左侧导航栏正常'
echo '   ✅ 表单样式正常'
echo '   ✅ 无黑块或乱码'
echo ''
echo '4. 登录测试（使用您的管理员账号）'
echo ''
echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
echo.
echo '如有问题，请查看日志：'
echo '  - Django 日志：journalctl -u eims -n 50'
echo '  - Nginx 日志：tail -f /var/log/nginx/error.log'
echo '  - Python 日志：tail -f /var/www/eims/logs/error.log'
echo.
echo '备份文件位置：/var/www/eims/settings.py.backup.*'
echo.
"@

pause
