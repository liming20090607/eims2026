#!/bin/bash
echo "========================================"
echo "  EIMS 服务器环境检查"
echo "========================================"
echo ""

echo "1. Nginx 状态："
systemctl status nginx --no-pager 2>&1 | grep -E "Active|Loaded" || echo "❌ 未安装 Nginx"
echo ""

echo "2. MySQL 状态："
systemctl status mysqld --no-pager 2>&1 | grep -E "Active|Loaded" || echo "❌ 未安装 MySQL"
echo ""

echo "3. Python 版本："
python3 --version 2>&1 || echo "❌ 未安装 Python3"
ls -la /usr/local/bin/python* 2>&1 | head -3
echo ""

echo "4. Git 版本："
git --version 2>&1 || echo "❌ 未安装 Git"
echo ""

echo "5. 项目目录："
ls -la /www/wwwroot/ 2>&1 | head -10 || echo "/www/wwwroot 不存在"
echo ""

echo "6. 数据库列表："
mysql -u root -e "SHOW DATABASES;" 2>&1 || echo "需要密码"
echo ""

echo "7. 端口占用："
echo "   80 端口 (HTTP): $(netstat -tlnp 2>/dev/null | grep -c :80) 个进程"
echo "   8000 端口 (Django): $(netstat -tlnp 2>/dev/null | grep -c :8000) 个进程"
echo "   3306 端口 (MySQL): $(netstat -tlnp 2>/dev/null | grep -c :3306) 个进程"
echo "   8888 端口 (宝塔): $(netstat -tlnp 2>/dev/null | grep -c :8888) 个进程"
echo ""

echo "8. 磁盘空间："
df -h | grep -E "Filesystem|/dev/vda" | head -3
echo ""

echo "========================================"
echo "  检查完成！"
echo "========================================"
