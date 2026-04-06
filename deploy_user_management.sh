#!/bin/bash
# 部署用户账号管理功能到生产服务器

echo "======================================"
echo "部署用户账号管理功能"
echo "======================================"

# 服务器信息
SERVER_IP="39.106.41.239"
SERVER_USER="admin"
PROJECT_PATH="/var/www/eims"

echo ""
echo "📦 开始部署到生产服务器..."
echo ""

# 1. 收集需要部署的文件
echo "1️⃣  准备部署文件..."

FILES_TO_DEPLOY=(
    "eims_app/forms/form_user_management.py"
    "eims_app/views/views_user_management.py"
    "eims_app/templates/eims_app/user_management.html"
    "eims_app/templatetags/custom_filters.py"
    "eims_app/urls.py"
    "eims_app/templates/base/base.html"
)

# 2. 创建临时部署包
echo "2️⃣  创建部署包..."
DEPLOY_DIR="/tmp/eims_user_mgmt_deploy"
mkdir -p "$DEPLOY_DIR"

for file in "${FILES_TO_DEPLOY[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ 添加：$file"
        cp --parents "$file" "$DEPLOY_DIR/"
    else
        echo "  ✗ 文件不存在：$file"
    fi
done

# 3. 上传到服务器
echo ""
echo "3️⃣  上传文件到服务器..."
cd "$DEPLOY_DIR"
scp -r * ${SERVER_USER}@${SERVER_IP}:${PROJECT_PATH}/

if [ $? -eq 0 ]; then
    echo "  ✓ 文件上传成功"
else
    echo "  ✗ 文件上传失败"
    exit 1
fi

# 4. 在服务器上执行部署
echo ""
echo "4️⃣  在服务器上执行部署命令..."
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /var/www/eims

echo "  • 收集静态文件..."
source venv/bin/activate
python manage.py collectstatic --noinput

echo "  • 检查配置..."
python manage.py check

echo "  • 重启 Gunicorn 服务..."
sudo supervisorctl restart eims

echo "  • 检查服务状态..."
sudo supervisorctl status eims

echo "  • 部署完成！"
ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ 部署成功！"
    echo "======================================"
    echo ""
    echo " 访问地址："
    echo "   http://xietongai.com.cn/user-management/"
    echo ""
    echo "🔐 登录信息："
    echo "   用户名：admin"
    echo "   密码：Admin2026!"
    echo ""
else
    echo ""
    echo "======================================"
    echo "❌ 部署失败！"
    echo "======================================"
    exit 1
fi

# 清理临时文件
rm -rf "$DEPLOY_DIR"

echo "📝 详细说明请查看：用户账号管理功能使用指南.md"
