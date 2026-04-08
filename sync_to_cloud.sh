#!/bin/bash
# EIMS 数据同步脚本 - 从本地同步到云服务器
# 使用方法: bash sync_to_cloud.sh

set -e  # 遇到错误立即退出

echo "========================================="
echo "EIMS 数据同步到云服务器"
echo "========================================="
echo ""

# 配置变量
SERVER_USER="root"
SERVER_IP="39.106.41.239"
SERVER_PATH="/var/www/eims"
GIT_REPO="https://gitee.com/liming20090607/eims2026.git"
MYSQL_PASSWORD="root123"  # MySQL root密码
MYSQL_DB="eims"  # 数据库名
SERVER_DB="backup_before_sync_$(date +%Y%m%d_%H%M%S).json"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}步骤 0: 设置MySQL root密码（如果还未设置）${NC}"
echo "-----------------------------------------"
echo "请先在服务器上执行 setup_mysql_root_password.sh 脚本"
echo "命令: ssh ${SERVER_USER}@${SERVER_IP} 'bash -s' < setup_mysql_root_password.sh"
echo ""
read -p "MySQL root密码已设置？(y/n): " mysql_ready
if [ "$mysql_ready" != "y" ] && [ "$mysql_ready" != "Y" ]; then
    echo "请先设置MySQL密码后再继续"
    exit 1
fi
echo ""

echo -e "${YELLOW}步骤 1: 备份服务器当前数据${NC}"
echo "-----------------------------------------"
ssh ${SERVER_USER}@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && MYSQL_PWD=${MYSQL_PASSWORD} mysqldump -u root ${MYSQL_DB} > ${SERVER_PATH}/backup_before_sync_$(date +%Y%m%d_%H%M%S).sql"
echo -e "${GREEN}✓ 服务器数据库已备份到: backup_before_sync_*.sql${NC}"
echo ""

echo -e "${YELLOW}步骤 2: 推送本地代码到 Gitee${NC}"
echo "-----------------------------------------"
echo "请确保本地代码已提交并推送到 Gitee 仓库"
echo "仓库地址: ${GIT_REPO}"
echo ""
echo "如果尚未推送，请先执行："
echo "  git add ."
echo "  git commit -m 'Sync to cloud'"
echo "  git push origin main"
echo ""
read -p "代码已推送到 Gitee？(y/n): " git_ready
if [ "$git_ready" != "y" ] && [ "$git_ready" != "Y" ]; then
    echo "请先推送代码到 Gitee 后再继续"
    exit 1
fi
echo -e "${GREEN}✓ 确认代码已推送到 Gitee${NC}"
echo ""

echo -e "${YELLOW}步骤 3: 在服务器拉取最新代码（从 Gitee）${NC}"
echo "-----------------------------------------"
# 在服务器上拉取最新代码
ssh ${SERVER_USER}@${SERVER_IP} "cd ${SERVER_PATH} && git pull origin main"
echo -e "${GREEN}✓ 代码已从 Gitee 同步到服务器${NC}"
echo ""

echo -e "${YELLOW}步骤 4: 导出并同步本地数据库${NC}"
echo "-----------------------------------------"
# 导出本地SQLite数据
echo "正在导出本地数据库..."
python manage.py dumpdata --natural-foreign --natural-primary --indent=2 > local_data.json
echo -e "${GREEN}✓ 本地数据已导出${NC}"

# 传输到服务器
echo "正在传输数据到服务器..."
scp local_data.json ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/local_data.json
echo -e "${GREEN}✓ 数据已传输到服务器${NC}"

# 在服务器上导入数据到MySQL
echo "正在导入数据到MySQL数据库..."
ssh ${SERVER_USER}@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && python manage.py loaddata local_data.json"
echo -e "${GREEN}✓ 数据导入完成${NC}"
echo ""

echo -e "${YELLOW}步骤 5: 同步媒体文件${NC}"
echo "-----------------------------------------"
rsync -avz --progress media/ ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/media/
echo -e "${GREEN}✓ 媒体文件同步完成${NC}"
echo ""

echo -e "${YELLOW}步骤 6: 更新服务器配置${NC}"
echo "-----------------------------------------"
ssh ${SERVER_USER}@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && python manage.py collectstatic --noinput"
echo -e "${GREEN}✓ 静态文件已收集${NC}"

ssh ${SERVER_USER}@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && python manage.py migrate --noinput"
echo -e "${GREEN}✓ 数据库迁移完成${NC}"
echo ""

echo -e "${YELLOW}步骤 7: 重启服务${NC}"
echo "-----------------------------------------"
ssh ${SERVER_USER}@${SERVER_IP} "supervisorctl restart eims"
echo -e "${GREEN}✓ Gunicorn 服务已重启${NC}"

ssh ${SERVER_USER}@${SERVER_IP} "systemctl restart nginx"
echo -e "${GREEN}✓ Nginx 服务已重启${NC}"
echo ""

echo -e "${YELLOW}步骤 8: 清理临时文件${NC}"
echo "-----------------------------------------"
rm -f local_data.json
ssh ${SERVER_USER}@${SERVER_IP} "rm -f ${SERVER_PATH}/local_data.json"
echo -e "${GREEN}✓ 临时文件已清理${NC}"
echo ""

echo "========================================="
echo -e "${GREEN}✓ 同步完成！${NC}"
echo "========================================="
echo ""
echo "请访问服务器验证:"
echo "  HTTP: http://${SERVER_IP}"
echo "  HTTPS: https://${SERVER_IP}"
echo ""
echo "备份文件位置:"
echo "  服务器: ${SERVER_PATH}/${SERVER_DB}"
echo ""
echo "如需回滚，请执行:"
echo "  ssh ${SERVER_USER}@${SERVER_IP} 'cd ${SERVER_PATH} && source venv/bin/activate && python manage.py loaddata ${SERVER_DB}'"
echo ""
