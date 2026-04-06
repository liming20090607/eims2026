# 检查服务器已安装软件

# 1. 检查 Nginx
echo "======================================"
echo "检查 Nginx"
echo "======================================"
systemctl status nginx | head -5
nginx -v

echo ""
echo "Nginx 配置："
ls -la /etc/nginx/conf.d/

echo ""
echo "======================================"

# 2. 检查 MySQL
echo "检查 MySQL"
echo "======================================"
systemctl status mysqld | head -5
mysql --version

echo ""
echo "MySQL 数据库列表："
mysql -u root -e "SHOW DATABASES;" 2>/dev/null || echo "需要密码才能查看"

echo ""
echo "======================================"

# 3. 检查 Python
echo "检查 Python"
echo "======================================"
python3 --version
python3.14 --version 2>/dev/null || echo "Python 3.14 未安装"

echo ""
echo "已安装的 Python 版本："
ls -la /usr/local/bin/python* 2>/dev/null || echo "未找到自定义 Python 安装"

echo ""
echo "======================================"

# 4. 检查 Git
echo "检查 Git"
echo "======================================"
git --version

echo ""
echo "======================================"

# 5. 检查 Supervisor
echo "检查 Supervisor"
echo "======================================"
systemctl status supervisord | head -5 2>/dev/null || systemctl status supervisor | head -5 2>/dev/null || echo "Supervisor 未安装或未运行"

echo ""
echo "======================================"

# 6. 检查 Gunicorn
echo "检查 Gunicorn"
echo "======================================"
which gunicorn 2>/dev/null || echo "Gunicorn 未全局安装"

echo ""
echo "======================================"

# 7. 检查项目目录
echo "检查项目目录"
echo "======================================"
ls -la /var/www/eims/ 2>/dev/null || echo "/var/www/eims 目录不存在"

echo ""
echo "检查宝塔面板项目目录："
ls -la /www/wwwroot/ 2>/dev/null || echo "/www/wwwroot 目录不存在（可能未使用宝塔）"

echo ""
echo "======================================"

# 8. 检查防火墙
echo "检查防火墙"
echo "======================================"
firewall-cmd --list-all 2>/dev/null || echo "firewalld 未运行"

echo ""
echo "======================================"

# 9. 检查端口占用
echo "检查端口占用"
echo "======================================"
echo "80 端口（HTTP）："
netstat -tlnp | grep :80 || echo "80 端口未被占用"

echo ""
echo "8000 端口（Django）："
netstat -tlnp | grep :8000 || echo "8000 端口未被占用"

echo ""
echo "3306 端口（MySQL）："
netstat -tlnp | grep :3306 || echo "3306 端口未被占用"

echo ""
echo "8888 端口（宝塔面板）："
netstat -tlnp | grep :8888 || echo "8888 端口未被占用"

echo ""
echo "======================================"

# 10. 检查磁盘空间
echo "检查磁盘空间"
echo "======================================"
df -h

echo ""
echo "======================================"

# 11. 检查内存
echo "检查内存使用"
echo "======================================"
free -h

echo ""
echo "======================================"

# 12. 检查运行中的服务
echo "检查运行中的服务"
echo "======================================"
systemctl list-units --type=service --state=running | grep -E "nginx|mysql|supervisor|gunicorn"

echo ""
echo "======================================"
