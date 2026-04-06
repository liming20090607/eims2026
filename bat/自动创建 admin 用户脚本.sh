#!/bin/bash

echo "======================================"
echo "强制创建/重置 admin 用户"
echo "适用于：CentOS / Alibaba Cloud Linux"
echo "======================================"
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 错误：请使用 root 用户运行此脚本"
    exit 1
fi

USERNAME="admin"

echo "📋 本脚本将执行以下操作："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 终止占用 admin 用户的所有进程"
echo "2. 删除现有 admin 用户（如果存在）"
echo "3. 创建新的 admin 用户"
echo "4. 设置随机强密码"
echo "5. 配置 sudo 权限"
echo "6. 显示登录凭据"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "是否继续？(y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ 已取消"
    exit 1
fi

# 步骤 1：查找并终止所有 admin 用户的进程
echo ""
echo "🔍 正在检查 admin 用户的进程..."
ps aux | grep -E "^(USER|${USERNAME})" | grep -v grep

if ps -u "$USERNAME" &>/dev/null; then
    echo "⚠️  发现 admin 用户的进程，正在终止..."
    pkill -9 -u "$USERNAME" 2>/dev/null
    sleep 2
    
    # 再次检查
    if ps -u "$USERNAME" &>/dev/null; then
        echo "⚠️  仍有进程在运行，尝试强制终止..."
        pkill -KILL -u "$USERNAME" 2>/dev/null
        sleep 1
    fi
    echo "✅ 已终止所有 admin 用户的进程"
else
    echo "✅ 没有发现运行中的进程"
fi

# 步骤 2：删除现有用户
echo ""
echo "🗑️  正在删除旧用户（如果存在）..."
if id "$USERNAME" &>/dev/null; then
    userdel -r "$USERNAME" 2>/dev/null || userdel -f "$USERNAME" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ 已删除旧用户 $USERNAME"
    else
        echo "⚠️  用户删除失败，但将继续创建新用户..."
    fi
else
    echo "ℹ️  用户不存在，跳过删除步骤"
fi

# 步骤 3：创建新用户
echo ""
echo "🆕 正在创建新用户 $USERNAME..."
useradd -m -s /bin/bash "$USERNAME"

if [ $? -eq 0 ]; then
    echo "✅ 用户创建成功"
else
    echo "❌ 用户创建失败"
    echo ""
    echo "可能的原因："
    echo "1. 用户仍然存在（有进程占用）"
    echo "2. 文件系统只读"
    echo "3. 磁盘空间不足"
    exit 1
fi

# 步骤 4：生成并设置密码
RANDOM_PASS=$(openssl rand -base64 12)

echo "正在设置密码..."
echo "$RANDOM_PASS" | passwd --stdin "$USERNAME" &>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 密码设置成功"
else
    echo "❌ 密码设置失败"
    exit 1
fi

# 步骤 5：添加 sudo 权限
echo "正在添加 sudo 权限..."
usermod -aG wheel "$USERNAME"

if [ $? -eq 0 ]; then
    echo "✅ sudo 权限配置成功"
else
    echo "❌ sudo 权限配置失败"
    exit 1
fi

# 步骤 6：验证配置
echo "验证 sudoers 配置..."
if grep -q "%wheel.*ALL=(ALL).*ALL" /etc/sudoers; then
    echo "✅ sudoers 配置正确"
else
    echo "⚠️  sudoers 可能需要手动配置"
fi

# 步骤 7：创建 SSH 目录
echo "配置 SSH 目录..."
su - "$USERNAME" -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

# 步骤 8：显示结果
echo ""
echo "======================================"
echo "✅ admin 用户强制创建/重置成功！"
echo "======================================"
echo ""
echo "📋 登录信息："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "用户名：$USERNAME"
echo "密  码：$RANDOM_PASS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  重要提示："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 请立即复制上面的密码（只显示一次）"
echo "2. 建议首次登录后修改密码"
echo "3. 使用 'sudo su -' 切换到 root"
echo "4. 密码已保存到：/root/admin_credentials.txt"
echo ""
echo "🔧 SSH 登录命令："
echo "ssh admin@39.106.41.239"
echo ""
echo "📊 用户信息："
id "$USERNAME"
echo ""
echo "🏠 家目录："
ls -la /home/$USERNAME/
echo ""

# 保存凭据到文件
cat > /root/admin_credentials.txt << CRED_EOF
========================================
阿里云 ECS 服务器登录凭据
========================================
服务器 IP: 39.106.41.239
实例 ID: iZ2ze74hagmo3egfxeffrcZ
========================================
用户名：$USERNAME
密  码：$RANDOM_PASS
========================================
创建时间：$(date '+%Y-%m-%d %H:%M:%S')
========================================

SSH 登录命令:
ssh admin@39.106.41.239

切换 root 命令:
sudo su -

注意事项:
1. 请妥善保管此文件
2. 建议定期更换密码
3. 不要将此文件分享给他人
4. 文件权限已设置为仅 root 可读
========================================
CRED_EOF

chmod 600 /root/admin_credentials.txt
echo "💾 凭据已保存到：/root/admin_credentials.txt"
echo ""

# 安全建议
echo "======================================"
echo "🔒 安全加固建议"
echo "======================================"
echo ""
echo "可选的安全措施："
echo "1. 禁用 root SSH 直接登录"
echo "   编辑：/etc/ssh/sshd_config"
echo "   设置：PermitRootLogin no"
echo ""
echo "2. 修改 SSH 端口（避免使用 22）"
echo "   编辑：/etc/ssh/sshd_config"
echo "   设置：Port 2222"
echo ""
echo "3. 安装 fail2ban 防暴力破解"
echo "   yum install epel-release -y"
echo "   yum install fail2ban -y"
echo ""
echo "4. 配置防火墙"
echo "   firewall-cmd --permanent --add-service=ssh"
echo "   firewall-cmd --reload"
echo ""

echo "======================================"
echo "✅ 所有操作已完成！"
echo "======================================"
echo ""
echo "下一步："
echo "1. 复制上面的密码"
echo "2. 在本地测试 SSH 登录（不要关闭此窗口）"
echo "3. 验证 sudo 权限"
echo ""

# 测试提示
echo "📝 测试命令（在本地 PowerShell 执行）："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ssh admin@39.106.41.239"
echo "# 输入上面的密码"
echo ""
echo "# 成功后测试 sudo:"
echo "sudo su -"
echo "# 输入 admin 密码"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
