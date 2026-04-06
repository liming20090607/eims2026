#!/bin/bash
# 网页无法访问一键修复脚本
# 使用方法：sudo bash 修复网页访问.sh

echo "======================================"
echo "EIMS 网页访问问题一键修复"
echo "======================================"
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 错误：请使用 root 用户或 sudo 运行此脚本"
    exit 1
fi

echo "📋 开始自动修复..."
echo ""

# Step 1: 启动 Supervisor
echo "🔧 步骤 1：检查 Supervisor 服务"
echo "-----------------------------------"
if systemctl is-active --quiet supervisord; then
    echo "✅ Supervisor 已在运行"
else
    echo "⚠️  Supervisor 未运行，正在启动..."
    systemctl start supervisord
    sleep 2
    
    if systemctl is-active --quiet supervisord; then
        echo "✅ Supervisor 启动成功"
    else
        echo "❌ Supervisor 启动失败"
        echo "   请检查：systemctl status supervisord"
        exit 1
    fi
fi
echo ""

# Step 2: 启动 Gunicorn
echo "🔧 步骤 2：启动 Gunicorn 服务"
echo "-----------------------------------"
cd /var/www/eims
source venv/bin/activate

# 检查 Supervisor 中的 EIMS 配置
if supervisorctl status eims 2>/dev/null | grep -q "RUNNING"; then
    echo "✅ EIMS 服务已在运行"
    echo "   正在重启服务..."
    supervisorctl restart eims
else
    echo "⚠️  EIMS 服务未运行，正在启动..."
    supervisorctl start eims
fi

sleep 3

# 检查启动结果
if supervisorctl status eims 2>/dev/null | grep -q "RUNNING"; then
    echo "✅ EIMS 服务启动成功"
else
    echo "❌ EIMS 服务启动失败"
    echo "   查看日志：tail -f /var/log/eims/error.log"
    echo "   尝试手动启动..."
    
    # 尝试手动启动
    nohup gunicorn --bind 0.0.0.0:8000 eims.wsgi:application > /tmp/gunicorn.log 2>&1 &
    sleep 2
    
    if ps aux | grep -E "[g]unicorn" > /dev/null; then
        echo "✅ Gunicorn 手动启动成功"
    else
        echo "❌ 手动启动也失败了"
        echo "   日志：cat /tmp/gunicorn.log"
        exit 1
    fi
fi
echo ""

# Step 3: 检查端口
echo "🔧 步骤 3：检查端口 8000"
echo "-----------------------------------"
if netstat -tln 2>/dev/null | grep -q ":8000"; then
    echo "✅ 端口 8000 正在监听"
    netstat -tln 2>/dev/null | grep ":8000"
else
    echo "❌ 端口 8000 未监听"
    echo "   Gunicorn 可能绑定失败"
    echo "   检查是否有其他进程占用:"
    netstat -tlnp 2>/dev/null | grep ":8000" || echo "   无占用"
fi
echo ""

# Step 4: 配置防火墙
echo "🔧 步骤 4：配置防火墙"
echo "-----------------------------------"
if command -v firewall-cmd &> /dev/null; then
    if sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
        echo "🔥 防火墙已开启"
        
        if sudo firewall-cmd --query-port=8000/tcp 2>/dev/null; then
            echo "✅ 8000 端口已开放"
        else
            echo "⚠️  8000 端口未开放，正在添加..."
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

# Step 5: 测试本地访问
echo "🔧 步骤 5：测试本地访问"
echo "-----------------------------------"
if command -v curl &> /dev/null; then
    echo "正在测试：http://localhost:8000/admin/"
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://localhost:8000/admin/)
    
    if [ "$response" = "200" ] || [ "$response" = "302" ]; then
        echo "✅ 本地访问成功 (HTTP $response)"
    else
        echo "⚠️  本地访问返回 HTTP $response"
        echo "   可能是 Django 配置问题"
    fi
else
    echo "ℹ️  未安装 curl，跳过测试"
fi
echo ""

# Step 6: 检查阿里云安全组（提示）
echo "🔧 步骤 6：阿里云安全组检查"
echo "-----------------------------------"
echo "请登录阿里云控制台检查:"
echo "  1. 访问：https://ecs.console.aliyun.com/"
echo "  2. 找到实例：39.106.41.239"
echo "  3. 安全组 → 配置规则"
echo "  4. 确认入方向规则:"
echo "     - 端口 8000/TCP, 授权对象 0.0.0.0/0"
echo ""

# Step 7: 查看服务状态
echo "🔧 步骤 7：最终状态检查"
echo "-----------------------------------"
echo "Gunicorn 进程:"
ps aux | grep -E "[g]unicorn" | head -n 3

echo ""
echo "端口监听:"
netstat -tln 2>/dev/null | grep ":8000" || echo "未监听"

echo ""
echo "Supervisor 状态:"
supervisorctl status eims 2>/dev/null || echo "未配置"

echo ""

# 总结
echo "======================================"
echo "修复完成！"
echo "======================================"
echo ""

# 最终验证
if ps aux | grep -E "[g]unicorn" > /dev/null && netstat -tln 2>/dev/null | grep -q ":8000"; then
    echo "✅ Gunicorn 服务运行正常"
    echo ""
    echo "现在可以访问:"
    echo "  http://39.106.41.239:8000/admin/"
    echo ""
    echo "如果仍然无法访问，请检查:"
    echo "  1. ✅ 阿里云安全组配置（最重要！）"
    echo "  2. ✅ 本地网络连接"
    echo "  3. ✅ 浏览器缓存（Ctrl+F5 刷新）"
    echo "  4. ✅ 查看错误日志：tail -f /var/log/eims/error.log"
else
    echo "❌ 服务仍有问题"
    echo ""
    echo "建议操作:"
    echo "  1. 查看详细日志：tail -f /var/log/eims/error.log"
    echo "  2. 手动测试：curl http://localhost:8000/"
    echo "  3. 重启服务器：reboot"
fi
echo ""
echo "======================================"
