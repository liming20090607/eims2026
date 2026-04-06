#!/bin/bash
# 重置 Linux admin 账号密码脚本
# 使用方法：sudo bash 重置 admin 密码.sh

echo "======================================"
echo "重置 Linux admin 账号密码"
echo "======================================"
echo ""

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 错误：请使用 root 用户运行此脚本"
    exit 1
fi

echo "⚠️  密码格式要求："
echo "  - 长度：8-30 个字符"
echo "  - 必须包含：大写字母、小写字母、数字、特殊字符"
echo "  - 允许的特殊字符：()~!@#\$%^&*-_+=\|;:.:/?"
echo "  - 不能包含：admin（用户名）"
echo ""
echo "✅ 示例密码：Admin@2026、Eims#1234、Server\$2026"
echo ""
echo "======================================"
echo ""

# 提示输入新密码
read -s -p "请输入新密码：" password
echo ""
read -s -p "确认密码：" password2
echo ""

# 验证密码一致性
if [ "$password" != "$password2" ]; then
    echo "❌ 两次输入的密码不一致！"
    exit 1
fi

# 验证密码长度
if [ ${#password} -lt 8 ]; then
    echo "❌ 密码长度至少 8 位！"
    exit 1
fi

if [ ${#password} -gt 30 ]; then
    echo "❌ 密码长度不能超过 30 位！"
    exit 1
fi

# 验证密码复杂度
if ! [[ "$password" =~ [A-Z] ]]; then
    echo "❌ 密码必须包含大写字母（A-Z）！"
    exit 1
fi

if ! [[ "$password" =~ [a-z] ]]; then
    echo "❌ 密码必须包含小写字母（a-z）！"
    exit 1
fi

if ! [[ "$password" =~ [0-9] ]]; then
    echo "❌ 密码必须包含数字（0-9）！"
    exit 1
fi

if ! [[ "$password" =~ [[:punct:]] ]]; then
    echo "❌ 密码必须包含特殊字符！"
    exit 1
fi

# 检查是否包含 admin
if [[ "$password" =~ [Aa][Dd][Mm][Ii][Nn] ]]; then
    echo "❌ 密码不能包含 'admin' 字样！"
    exit 1
fi

echo ""
echo "✅ 密码格式验证通过"
echo ""

# 显示密码摘要（脱敏）
masked_pass="${password:0:2}****${password: -2}"
echo "设置的密码：$masked_pass"
echo ""

# 重置密码
echo ""
echo "正在重置密码..."
echo "$password" | passwd --stdin admin

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ admin 账号密码重置成功！"
    echo "======================================"
    echo ""
    echo "登录信息："
    echo "  服务器：39.106.41.239"
    echo "  用户名：admin"
    echo "  密码：$password"
    echo ""
    echo "测试登录："
    echo "  ssh admin@39.106.41.239"
    echo ""
    echo "提示："
    echo "  - 请立即测试登录"
    echo "  - 妥善保管密码"
    echo "  - 建议定期更换密码"
    echo ""
    echo "======================================"
else
    echo ""
    echo "❌ 密码重置失败！"
    echo "可能原因："
    echo "  1. 密码不符合系统策略"
    echo "  2. 账号被锁定"
    echo "  3. 系统权限问题"
    echo ""
    echo "建议尝试："
    echo "  1. 使用更复杂的密码"
    echo "  2. 检查账号状态：passwd -S admin"
    echo "  3. 手动设置：passwd admin"
    echo ""
fi
