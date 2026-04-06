# 查找 MySQL 密码的快速脚本
# 请在服务器上执行此命令

# 1. 查看 .env 文件中的密码
echo "=== 检查 .env 文件 ==="
cat /var/www/eims/.env | grep DB_PASSWORD

# 2. 查看 settings.py 中的密码
echo -e "\n=== 检查 settings.py 文件 ==="
cat /var/www/eims/settings.py | grep -A 5 "PASSWORD"

# 3. 查看 settings_production.py 中的密码
echo -e "\n=== 检查 settings_production.py 文件 ==="
cat /var/www/eims/settings_production.py | grep -A 5 "PASSWORD"

# 4. 查看 Supervisor 配置文件
echo -e "\n=== 检查 Supervisor 配置 ==="
cat /etc/supervisord.d/eims.ini | grep -i password

# 5. 查看 Gunicorn 启动脚本
echo -e "\n=== 检查启动脚本 ==="
cat /var/www/eims/start_gunicorn.sh | grep -i password
