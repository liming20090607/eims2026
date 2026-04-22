#!/bin/bash
# MySQL密码重置脚本 - 在云服务器上直接运行

echo "========================================="
echo "重置 MySQL root 密码"
echo "========================================="
echo ""

NEW_PASSWORD="mysql2026!"

echo "步骤 1: 停止 MySQL..."
systemctl stop mysqld
sleep 2

echo "步骤 2: 以安全模式启动..."
mysqld_safe --skip-grant-tables &
sleep 4

echo "步骤 3: 重置密码..."
mysql -u root <<EOF
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '$NEW_PASSWORD';
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$NEW_PASSWORD';
FLUSH PRIVILEGES;
EOF

echo "步骤 4: 重启 MySQL..."
kill $(cat /var/run/mysqld/mysqld.pid 2>/dev/null) 2>/dev/null || pkill -9 mysqld_safe
sleep 2
systemctl start mysqld
sleep 4

echo "步骤 5: 测试密码..."
mysql -u root -p"$NEW_PASSWORD" -e "SELECT 'Password reset successful!' AS result;" 2>&1

echo ""
echo "步骤 6: 更新 .env 文件..."
sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=\"$NEW_PASSWORD\"/" /var/www/eims/.env
grep DB_PASSWORD /var/www/eims/.env

echo ""
echo "步骤 7: 重启 Gunicorn..."
pkill -9 -f gunicorn || true
sleep 2
cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 --daemon wsgi:application
sleep 3

echo ""
echo "步骤 8: 测试网站..."
curl -o /dev/null -s -w "HTTP状态码: %{http_code}\n" http://127.0.0.1:8000/login/

echo ""
echo "========================================="
echo "✅ 完成！密码已重置为: $NEW_PASSWORD"
echo "========================================="
