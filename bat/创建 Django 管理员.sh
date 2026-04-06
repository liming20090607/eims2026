#!/bin/bash
# 创建 Django 超级管理员账号
# 使用方法：sudo bash 创建 Django 管理员.sh

echo "======================================"
echo "创建 Django 超级管理员账号"
echo "======================================"
echo ""
echo "说明："
echo "  - 这是用于登录 Web 后台的账号"
echo "  - 不是 Linux SSH 登录的账号"
echo ""
echo "======================================"
echo ""

cd /var/www/eims
source venv/bin/activate

# 提示输入用户名
read -p "请输入管理员用户名 (默认：admin): " username
username=${username:-admin}

# 提示输入密码
read -s -p "请输入密码: " password
echo ""
read -s -p "确认密码: " password2
echo ""

if [ "$password" != "$password2" ]; then
    echo "❌ 两次输入的密码不一致！"
    exit 1
fi

if [ -z "$password" ]; then
    echo "❌ 密码不能为空！"
    exit 1
fi

# 创建超级用户
echo ""
echo "正在创建超级管理员：$username ..."
echo ""

python manage.py shell << EOF
from django.contrib.auth.models import User

# 检查用户是否已存在
if User.objects.filter(username='$username').exists():
    print(f"⚠️  用户 '$username' 已存在，正在重置密码...")
    user = User.objects.get(username='$username')
    user.set_password('$password')
    user.is_superuser = True
    user.is_staff = True
    user.is_active = True
    user.save()
    print(f"✅ 用户 '$username' 密码已重置")
else
    print(f"正在创建用户 '$username'...")
    user = User.objects.create_superuser('$username', '', '$password')
    print(f"✅ 超级管理员 '$username' 创建成功！")
EOF

echo ""
echo "======================================"
echo "创建完成！"
echo "======================================"
echo ""
echo "登录信息："
echo "  用户名：$username"
echo "  密码：您设置的密码"
echo ""
echo "登录地址："
echo "  http://39.106.41.239:8000/admin/"
echo ""
echo "提示："
echo "  - 使用此账号登录 Django Admin 后台"
echo "  - 使用 Linux admin 账号 SSH 登录服务器"
echo "  - 这是两个不同的账号系统"
echo ""
echo "======================================"
