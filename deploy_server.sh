# =========================================
# 协同 AI 办公系统 - 服务器部署脚本
# 请在服务器上执行此脚本
# =========================================

set -e  # 遇到错误立即退出

echo "========================================="
echo "  协同 AI 办公系统 - 开始部署"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# 1. 进入项目目录
echo -e "\n[1/8] 进入项目目录..."
cd /var/www/eims

# 2. 拉取最新代码
echo -e "\n[2/8] 拉取最新代码..."
git pull gitee master
echo "✓ 代码更新完成"

# 3. 激活虚拟环境
echo -e "\n[3/8] 激活虚拟环境..."
source /var/www/eims/venv/bin/activate
echo "✓ 虚拟环境已激活"

# 4. 安装/更新 Python 依赖
echo -e "\n[4/8] 更新 Python 依赖..."
pip install -r requirements.txt
echo "✓ 依赖更新完成"

# 5. 数据库迁移
echo -e "\n[5/8] 数据库迁移..."
python manage.py makemigrations
python manage.py migrate
echo "✓ 数据库迁移完成"

# 6. 收集静态文件
echo -e "\n[6/8] 收集静态文件..."
python manage.py collectstatic --noinput
echo "✓ 静态文件收集完成"

# 7. 重启 Gunicorn 服务
echo -e "\n[7/8] 重启 Gunicorn 服务..."
supervisorctl restart eims
echo "✓ Gunicorn 已重启"

# 8. 检查服务状态
echo -e "\n[8/8] 检查服务状态..."
supervisorctl status eims
systemctl status nginx --no-pager | head -n 5

echo ""
echo "========================================="
echo "  ✅ 部署完成！"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="
echo ""
echo "请执行以下命令验证部署："
echo "  1. 测试 Gunicorn: curl http://127.0.0.1:8000"
echo "  2. 查看日志: tail -f /var/www/eims/logs/gunicorn.log"
echo "  3. 浏览器访问: http://39.106.41.239"
echo ""
