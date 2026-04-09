#!/bin/bash
# =========================================
# EIMS2026 - 一键自动化部署脚本
# =========================================

set -e

SERVER_IP="39.106.41.239"
SERVER_USER="root"
SERVER_DIR="/var/www/eims"
GITEE_REMOTE="gitee"
BRANCH="master"

echo "========================================="
echo "  EIMS2026 - 一键自动化部署"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# 1. 推送到 Gitee
echo -e "\n[1/4] 推送代码到 Gitee..."
git add -A
git commit -m "auto: deploy $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
git push $GITEE_REMOTE $BRANCH
echo "✓ 代码推送完成"

# 2. SSH 到服务器执行部署
echo -e "\n[2/4] 连接到云服务器并拉取代码..."
ssh $SERVER_USER@$SERVER_IP "
    set -e
    cd $SERVER_DIR
    git pull $GITEE_REMOTE $BRANCH
    echo '✓ 代码拉取完成'
"
echo "✓ 代码更新完成"

# 3. 激活虚拟环境并迁移数据库
echo -e "\n[3/4] 数据库迁移..."
ssh $SERVER_USER@$SERVER_IP "
    set -e
    cd $SERVER_DIR
    source venv/bin/activate
    python manage.py makemigrations
    python manage.py migrate
    echo '✓ 数据库迁移完成'
"
echo "✓ 数据库迁移完成"

# 4. 收集静态文件并重启服务
echo -e "\n[4/4] 收集静态文件并重启服务..."
ssh $SERVER_USER@$SERVER_IP "
    set -e
    cd $SERVER_DIR
    source venv/bin/activate
    python manage.py collectstatic --noinput
    supervisorctl restart eims
    echo '✓ 静态文件收集完成'
    echo '✓ 服务重启完成'
"
echo "✓ 服务重启完成"

echo ""
echo "========================================="
echo "  ✅ 部署完成！"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="
echo ""
echo "验证部署："
echo "  1. 查看服务状态: ssh root@$SERVER_IP 'supervisorctl status eims'"
echo "  2. 查看日志: ssh root@$SERVER_IP 'tail -f $SERVER_DIR/logs/gunicorn.log'"
echo "  3. 浏览器访问: http://$SERVER_IP"
echo ""
