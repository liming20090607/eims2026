#!/bin/bash
# 服务器问题排查与一键修复脚本
# 使用方法：sudo bash 修复服务器访问.sh

echo "======================================"
echo "EIMS 服务器问题排查与修复"
echo "======================================"
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 错误：请使用 root 用户或 sudo 运行此脚本"
    exit 1
fi

echo "📋 开始检查..."
echo ""

# Step 1: 检查 Gunicorn
echo "🔍 检查 Gunicorn 进程..."
if ps aux | grep -E "[g]unicorn" > /dev/null; then
    echo "✅ Gunicorn 正在运行"
    ps aux | grep -E "[g]unicorn" | head -n 5
else
    echo "❌ Gunicorn 未运行"
    echo "🔧 正在启动 Supervisor..."
    
    if systemctl start supervisord 2>/dev/null; then
        echo "✅ Supervisor 已启动"
        sleep 2
    else
        echo "⚠️  Supervisor 启动失败，尝试直接启动 Gunicorn..."
        cd /var/www/eims
        source venv/bin/activate
        nohup gunicorn --bind 0.0.0.0:8000 eims.wsgi:application > /tmp/gunicorn.log 2>&1 &
        sleep 2
    fi
fi
echo ""

# Step 2: 检查 Supervisor 状态
echo "🔍 检查 Supervisor 状态..."
if systemctl is-active --quiet supervisord; then
    echo "✅ Supervisor 服务正常"
    echo ""
    echo "EIMS 服务状态:"
    supervisorctl status eims 2>/dev/null || echo "⚠️  未找到 EIMS 服务配置"
else
    echo "❌ Supervisor 未运行"
    echo "🔧 正在启动..."
    systemctl start supervisord
    sleep 2
    if systemctl is-active --quiet supervisord; then
        echo "✅ Supervisor 已启动"
    else
        echo "❌ Supervisor 启动失败"
    fi
fi
echo ""

# Step 3: 检查端口 8000
echo "📡 检查端口 8000..."
if netstat -tln 2>/dev/null | grep -q ":8000"; then
    echo "✅ 端口 8000 正在监听"
    netstat -tln 2>/dev/null | grep ":8000"
else
    echo "❌ 端口 8000 未监听"
    echo "⚠️  可能原因:"
    echo "   1. Gunicorn 未启动"
    echo "   2. 端口被占用"
    echo "   3. 防火墙阻止"
fi
echo ""

# Step 4: 检查防火墙
echo "🛡️  检查防火墙..."
if command -v firewall-cmd &> /dev/null; then
    if sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
        echo "⚠️  防火墙已开启"
        echo "🔧 检查是否开放 8000 端口..."
        if sudo firewall-cmd --query-port=8000/tcp 2>/dev/null; then
            echo "✅ 8000 端口已开放"
        else
            echo "❌ 8000 端口未开放"
            echo "🔧 正在开放端口..."
            sudo firewall-cmd --permanent --add-port=8000/tcp
            sudo firewall-cmd --reload
            echo "✅ 8000 端口已开放"
        fi
    else
        echo "ℹ️  防火墙未运行"
    fi
else
    echo "ℹ️  未安装 firewalld"
fi
echo ""

# Step 5: 检查安全组提示
echo "🛡️  阿里云安全组检查:"
echo "   请登录阿里云控制台检查:"
echo "   1. 访问：https://ecs.console.aliyun.com/"
echo "   2. 找到实例：39.106.41.239"
echo "   3. 安全组 → 配置规则"
echo "   4. 确认入方向规则:"
echo "      - 端口 8000/TCP, 授权对象 0.0.0.0/0"
echo ""

# Step 6: 测试本地访问
echo "🧪 测试本地访问..."
if command -v curl &> /dev/null; then
    if curl -s --connect-timeout 3 http://localhost:8000/admin/ > /dev/null; then
        echo "✅ 本地访问测试成功"
    else
        echo "❌ 本地访问测试失败"
        echo "⚠️  Django 可能配置有误或服务异常"
    fi
else
    echo "ℹ️  未安装 curl，跳过测试"
fi
echo ""

# Step 7: 查看最近的日志
echo "📄 最近的错误日志:"
if [ -f /var/log/eims/error.log ]; then
    echo "--- 最后 10 行错误日志 ---"
    tail -n 10 /var/log/eims/error.log
    echo "--- 日志结束 ---"
else
    echo "ℹ️  未找到 Gunicorn 日志文件"
fi
echo ""

# Step 8: 检查磁盘空间
echo "💾 检查磁盘空间..."
df -h / | tail -n 1
if df / | tail -n 1 | awk '{print $5}' | sed 's/%//' | grep -q '^100$\|^9[0-9]$'; then
    echo "⚠️  磁盘空间不足！"
else
    echo "✅ 磁盘空间充足"
fi
echo ""

# Step 9: 检查内存
echo "🧠 检查内存使用..."
free -h | grep Mem
if free -h | awk '/Mem:/ {print $7/$2 * 100.0}' | awk '{if ($1 < 10) print "low"}' | grep -q "low"; then
    echo "⚠️  内存不足！"
else
    echo "✅ 内存充足"
fi
echo ""

# 总结
echo "======================================"
echo "排查完成！"
echo "======================================"
echo ""

# 检查服务状态
if ps aux | grep -E "[g]unicorn" > /dev/null && netstat -tln 2>/dev/null | grep -q ":8000"; then
    echo "✅ Gunicorn 服务正常"
    echo ""
    echo "现在可以通过浏览器访问:"
    echo "  http://39.106.41.239:8000/admin/"
    echo ""
    echo "如果仍然无法访问，请检查:"
    echo "  1. 阿里云安全组配置"
    echo "  2. 本地网络连接"
    echo "  3. 浏览器缓存（尝试 Ctrl+F5 刷新）"
else
    echo "❌ Gunicorn 服务异常"
    echo ""
    echo "建议操作:"
    echo "  1. 查看日志：tail -f /var/log/eims/error.log"
    echo "  2. 手动启动：cd /var/www/eims && source venv/bin/activate && gunicorn --bind 0.0.0.0:8000 eims.wsgi:application"
    echo "  3. 重启 Supervisor: systemctl restart supervisord"
fi
echo ""
echo "======================================"
