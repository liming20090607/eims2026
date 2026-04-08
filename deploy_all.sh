#!/bin/bash
# EIMS 一键部署脚本 - 全自动执行
# 使用方法: bash deploy_all.sh

set -e

echo "========================================="
echo "EIMS 云服务器一键部署"
echo "========================================="
echo ""

# 配置变量
SERVER_USER="root"
SERVER_IP="39.106.41.239"
SERVER_PATH="/var/www/eims"
GIT_REPO="https://gitee.com/liming20090607/eims2026.git"
MYSQL_PASSWORD="root123"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}=== 第一步：设置 MySQL 密码 ===${NC}"
echo ""
echo "正在上传并执行 MySQL 密码设置脚本..."

# 上传自动脚本
scp setup_mysql_auto.sh ${SERVER_USER}@${SERVER_IP}:/root/setup_mysql_auto.sh

# SSH 执行脚本
ssh -t ${SERVER_USER}@${SERVER_IP} "bash /root/setup_mysql_auto.sh"

echo ""
echo -e "${GREEN}✓ MySQL 密码设置完成！${NC}"
echo ""

echo -e "${YELLOW}=== 第二步：推送代码到 Gitee ===${NC}"
echo ""
echo "请确认本地代码已提交..."
git status
echo ""
read -p "是否现在提交并推送到 Gitee？(y/n): " confirm_git

if [ "$confirm_git" = "y" ] || [ "$confirm_git" = "Y" ]; then
    git add .
    git commit -m "Auto deploy - $(date +%Y-%m-%d-%H%M%S)"
    git push origin main
    echo -e "${GREEN}✓ 代码已推送到 Gitee${NC}"
else
    echo -e "${YELLOW}跳过代码推送（假设已推送）${NC}"
fi
echo ""

echo -e "${YELLOW}=== 第三步：备份服务器数据库 ===${NC}"
echo ""
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
ssh ${SERVER_USER}@${SERVER_IP} "cd ${SERVER_PATH} && MYSQL_PWD=${MYSQL_PASSWORD} mysqldump -u root eims > ${BACKUP_FILE}"
echo -e "${GREEN}✓ 服务器数据库已备份: ${BACKUP_FILE}${NC}"
echo ""

echo -e "${YELLOW}=== 第四步：从 Gitee 拉取代码到服务器 ===${NC}"
echo ""
ssh ${SERVER_USER}@${SERVER_IP} "cd ${SERVER_PATH} && git pull origin main"
echo -e "${GREEN}✓ 代码已从 Gitee 同步${NC}"
echo ""

echo -e "${YELLOW}=== 第五步：导出本地数据 ===${NC}"
echo ""
python manage.py dumpdata --natural-foreign --natural-primary --indent=2 > local_data.json
echo -e "${GREEN}✓ 本地数据已导出${NC}"
echo ""

echo -e "${YELLOW}=== 第六步：传输数据到服务器 ===${NC}"
echo ""
scp local_data.json ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/local_data.json
echo -e "${GREEN}✓ 数据已传输${NC}"
echo ""

echo -e "${YELLOW}=== 第七步：导入数据到 MySQL ===${NC}"
echo ""
ssh ${SERVER_USER}@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && python manage.py loaddata local_data.json"
echo -e "${GREEN}✓ 数据导入完成${NC}"
echo ""

echo -e "${YELLOW}=== 第八步：同步媒体文件 ===${NC}"
echo ""
rsync -avz --progress media/ ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/media/
echo -e "${GREEN}✓ 媒体文件同步完成${NC}"
echo ""

echo -e "${YELLOW}=== 第九步：收集静态文件 ===${NC}"
echo ""
ssh ${SERVER_USER}@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && python manage.py collectstatic --noinput"
echo -e "${GREEN}✓ 静态文件收集完成${NC}"
echo ""

echo -e "${YELLOW}=== 第十步：数据库迁移 ===${NC}"
echo ""
ssh ${SERVER_USER}@${SERVER_IP} "cd ${SERVER_PATH} && source venv/bin/activate && python manage.py migrate --noinput"
echo -e "${GREEN}✓ 数据库迁移完成${NC}"
echo ""

echo -e "${YELLOW}=== 第十一步：重启服务 ===${NC}"
echo ""
ssh ${SERVER_USER}@${SERVER_IP} "supervisorctl restart eims"
echo -e "${GREEN}✓ Gunicorn 已重启${NC}"

ssh ${SERVER_USER}@${SERVER_IP} "systemctl restart nginx"
echo -e "${GREEN}✓ Nginx 已重启${NC}"
echo ""

echo -e "${YELLOW}=== 第十二步：清理临时文件 ===${NC}"
echo ""
rm -f local_data.json
ssh ${SERVER_USER}@${SERVER_IP} "rm -f ${SERVER_PATH}/local_data.json"
echo -e "${GREEN}✓ 临时文件已清理${NC}"
echo ""

echo "========================================="
echo -e "${GREEN}✓ 部署完成！${NC}"
echo "========================================="
echo ""
echo "📊 服务器信息："
echo "  地址: http://${SERVER_IP}"
echo "  数据库: eims (root/${MYSQL_PASSWORD})"
echo "  代码路径: ${SERVER_PATH}"
echo ""
echo "📋 验证步骤："
echo "  1. 浏览器访问: http://${SERVER_IP}"
echo "  2. SSH 检查服务: ssh ${SERVER_USER}@${SERVER_IP}"
echo "  3. 查看日志: tail -f /var/log/eims/error.log"
echo ""
echo "🔄 备份文件："
echo "  服务器: ${SERVER_PATH}/${BACKUP_FILE}"
echo ""
echo "如需回滚数据库："
echo "  ssh ${SERVER_USER}@${SERVER_IP} 'cd ${SERVER_PATH} && MYSQL_PWD=${MYSQL_PASSWORD} mysql -u root eims < ${BACKUP_FILE}'"
echo ""
