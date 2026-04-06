#!/bin/bash
# 检查 Django 管理员账号
# 使用方法：sudo bash 检查 admin 账号.sh

echo "======================================"
echo "检查 Django 管理员账号"
echo "======================================"
echo ""

cd /var/www/eims
source venv/bin/activate

echo "📋 当前 Django 用户列表："
echo ""

python manage.py shell << EOF
from django.contrib.auth.models import User
users = User.objects.all()
if users.exists():
    print(f"✅ 发现 {users.count()} 个用户:")
    for user in users:
        print(f"  - {user.username} (邮箱：{user.email}, 超级管理员：{user.is_superuser}, 活跃：{user.is_active})")
else
    print("❌ 未发现任何用户")
EOF

echo ""
echo "======================================"
echo "提示："
echo "  - 这是 Django 系统的账号（用于登录 Web 后台）"
echo "  - 不是 Linux 的 admin 账号（用于 SSH 登录）"
echo "======================================"
