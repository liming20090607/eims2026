#!/bin/bash
# ========================================
# EIMS 自动部署脚本 - 服务器端
# ========================================

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 配置
PROJECT_DIR="/var/www/eims"
VENV_DIR="$PROJECT_DIR/venv"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  EIMS 自动部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查是否在正确的目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}错误：项目目录不存在：$PROJECT_DIR${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# 1. 拉取最新代码
echo -e "${YELLOW}[1/5] 拉取最新代码...${NC}"
git pull origin main
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 代码拉取失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 代码拉取成功${NC}"
echo ""

# 2. 激活虚拟环境
echo -e "${YELLOW}[2/5] 激活虚拟环境...${NC}"
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 虚拟环境激活失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
echo ""

# 3. 安装依赖
echo -e "${YELLOW}[3/5] 安装依赖...${NC}"
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠ 依赖安装可能有警告（通常可以忽略）${NC}"
fi
echo -e "${GREEN}✓ 依赖安装完成${NC}"
echo ""

# 4. 数据库迁移和静态文件
echo -e "${YELLOW}[4/5] 数据库迁移和静态文件收集...${NC}"
python manage.py migrate --noinput
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 数据库迁移或静态文件收集失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 数据库迁移和静态文件收集完成${NC}"
echo ""

# 5. 重启服务
echo -e "${YELLOW}[5/5] 重启服务...${NC}"
systemctl restart eims
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 服务重启失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 服务重启成功${NC}"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "服务状态查看："
echo "  systemctl status eims"
echo ""
echo "日志查看："
echo "  tail -f /var/log/gunicorn/error.log"
echo ""
echo "访问地址："
echo "  http://$(hostname -I | awk '{print $1}')"
echo ""
