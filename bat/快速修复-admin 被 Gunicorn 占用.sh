#!/bin/bash

echo "======================================"
echo "快速修复：admin 被 Gunicorn 占用"
echo "======================================"
echo ""

USERNAME="admin"

# 显示当前进程
echo "📋 当前 admin 用户的进程："
ps aux | grep -E "^(USER|${USERNAME})" | grep -v grep
echo ""

# 停止 supervisor
read -p "是否停止 Supervisor 服务？(y/n): " stop_sup
if [ "$stop_sup" = "y" ]; then
    echo "正在停止 Supervisor..."
    systemctl stop supervisord 2>/dev/null || supervisorctl stop all 2>/dev/null
    sleep 2
    echo "✅ Supervisor 已停止"
fi

# 杀死所有 gunicorn 进程
echo ""
echo "🔪 正在杀死所有 Gunicorn 进程..."
pkill -9 gunicorn
sleep 2

# 检查是否还有进程
if pgrep -u "$USERNAME" &>/dev/null; then
    echo "⚠️  仍有进程，强制终止..."
    pkill -KILL -u "$USERNAME"
    sleep 2
fi
echo "✅ 所有进程已终止"

# 验证
echo ""
echo "🔍 验证进程状态..."
if ps -u "$USERNAME" &>/dev/null; then
    echo "⚠️  仍有进程在运行："
    ps -u "$USERNAME"
    read -p "是否强制杀死这些进程？(y/n): " force_kill
    if [ "$force_kill" = "y" ]; then
        pkill -KILL -u "$USERNAME"
        sleep 2
    fi
else
    echo "✅ 没有发现进程"
fi

# 删除用户
echo ""
echo "🗑️  正在删除用户..."
userdel -f "$USERNAME" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️  userdel 失败，尝试手动清理..."
    rm -rf /home/"$USERNAME"
    sed -i "/^${USERNAME}:/d" /etc/passwd
    sed -i "/^${USERNAME}:/d" /etc/shadow
    sed -i "/^${USERNAME}:/d" /etc/group
    sed -i "/^${USERNAME}:/d" /etc/gshadow
    echo "✅ 手动清理完成"
else
    echo "✅ 用户已删除"
fi

# 重新创建
echo ""
echo "🆕 正在创建新用户..."
useradd -m -s /bin/bash "$USERNAME"

if [ $? -eq 0 ]; then
    echo "✅ 用户创建成功"
else
    echo "❌ 用户创建失败"
    exit 1
fi

# 设置密码
echo ""
echo "🔐 请设置密码（输入两次）："
passwd "$USERNAME"

if [ $? -eq 0 ]; then
    echo "✅ 密码设置成功"
else
    echo "❌ 密码设置失败"
    exit 1
fi

# 添加 sudo 权限
usermod -aG wheel "$USERNAME"
echo "✅ sudo 权限已配置"

# 配置 SSH
su - "$USERNAME" -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
echo "✅ SSH 目录已配置"

# 启动 supervisor
echo ""
echo "🚀 正在启动 Supervisor..."
systemctl start supervisord
sleep 2
echo "✅ Supervisor 已启动"

# 显示结果
echo ""
echo "======================================"
echo "✅ admin 用户修复成功！"
echo "======================================"
echo ""
echo "📋 登录信息："
echo "━━━━━━━━━━━━━━━━━━━━"
echo "用户名：$USERNAME"
echo "密  码：(您刚才设置的密码)"
echo "━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔧 SSH 登录命令："
echo "ssh admin@39.106.41.239"
echo ""
echo "切换 root 命令："
echo "sudo su -"
echo ""

echo "📊 用户信息："
id "$USERNAME"
echo ""

echo "🏠 家目录："
ls -la /home/$USERNAME/
echo ""

echo "⚠️  重要提示："
echo "━━━━━━━━━━━━━━━━━━━━"
echo "1. 请在本地测试 SSH 登录（不要关闭此窗口）"
echo "2. 如果 Gunicorn 未自动启动，执行："
echo "   sudo supervisorctl start eims"
echo ""

# 保存凭据
echo "用户名：$USERNAME" > /root/admin_cred.txt
echo "修复时间：$(date '+%Y-%m-%d %H:%M:%S')" >> /root/admin_cred.txt
chmod 600 /root/admin_cred.txt
echo "💾 凭据已保存到：/root/admin_cred.txt"
echo ""
