#!/bin/bash
# 网页无法访问问题诊断脚本
# 使用方法：sudo bash 诊断网页访问问题.sh

echo "======================================"
echo "EIMS 网页访问问题诊断"
echo "======================================"
echo ""

# 检查项 1：Gunicorn 进程
echo "🔍 检查 1：Gunicorn 进程状态"
echo "-----------------------------------"
if ps aux | grep -E "[g]unicorn" > /dev/null; then
    echo "✅ Gunicorn 正在运行"
    ps aux | grep -E "[g]unicorn" | head -n 5
    gunicorn_count=$(ps aux | grep -E "[g]unicorn" | wc -l)
    echo "   进程数：$gunicorn_count"
else
    echo "❌ Gunicorn 未运行"
    echo "   这是网页打不开的主要原因！"
fi
echo ""

# 检查项 2：端口 8000 监听
echo "🔍 检查 2：端口 8000 监听状态"
echo "-----------------------------------"
if netstat -tln 2>/dev/null | grep -q ":8000"; then
    echo "✅ 端口 8000 正在监听"
    netstat -tln 2>/dev/null | grep ":8000"
else
    echo "❌ 端口 8000 未监听"
    echo "   Gunicorn 可能未启动或绑定失败"
fi
echo ""

# 检查项 3：Supervisor 状态
echo "🔍 检查 3：Supervisor 服务状态"
echo "-----------------------------------"
if systemctl is-active --quiet supervisord; then
    echo "✅ Supervisor 正在运行"
    echo ""
    echo "EIMS 服务状态:"
    supervisorctl status eims 2>/dev/null || echo "⚠️  未找到 EIMS 服务配置"
else
    echo "❌ Supervisor 未运行"
    echo "   需要启动 Supervisor"
fi
echo ""

# 检查项 4：防火墙状态
echo "🔍 检查 4：防火墙状态"
echo "-----------------------------------"
if command -v firewall-cmd &> /dev/null; then
    firewall_state=$(sudo firewall-cmd --state 2>/dev/null)
    if [ "$firewall_state" = "running" ]; then
        echo "⚠️  防火墙已开启"
        echo ""
        echo "检查 8000 端口:"
        if sudo firewall-cmd --query-port=8000/tcp 2>/dev/null; then
            echo "✅ 8000 端口已开放"
        else
            echo "❌ 8000 端口未开放"
            echo "   需要添加防火墙规则"
        fi
    else
        echo "ℹ️  防火墙未运行"
    fi
else
    echo "ℹ️  未安装 firewalld"
fi
echo ""

# 检查项 5：Django 配置
echo "🔍 检查 5：Django 配置"
echo "-----------------------------------"
cd /var/www/eims
if [ -f "settings.py" ]; then
    echo "✅ settings.py 存在"
    
    # 检查 ALLOWED_HOSTS
    if grep -q "ALLOWED_HOSTS" settings.py; then
        echo "✅ ALLOWED_HOSTS 配置存在"
        
        # 检查是否包含服务器 IP
        if grep -q "39.106.41.239" settings.py || grep -q "'\*'" settings.py; then
            echo "✅ IP 地址已配置"
        else
            echo "⚠️  可能缺少服务器 IP 配置"
        fi
    else
        echo "⚠️  未找到 ALLOWED_HOSTS 配置"
    fi
else
    echo "❌ settings.py 不存在"
fi
echo ""

# 检查项 6：虚拟环境
echo "🔍 检查 6：虚拟环境"
echo "-----------------------------------"
if [ -d "venv" ]; then
    echo "✅ 虚拟环境存在"
    
    # 检查 Gunicorn 是否安装
    source venv/bin/activate
    if python -c "import gunicorn" 2>/dev/null; then
        echo "✅ Gunicorn 已安装"
    else
        echo "❌ Gunicorn 未安装"
        echo "   需要安装：pip install gunicorn"
    fi
    deactivate
else
    echo "❌ 虚拟环境不存在"
fi
echo ""

# 检查项 7：日志文件
echo "🔍 检查 7：最近的错误日志"
echo "-----------------------------------"
if [ -f "/var/log/eims/error.log" ]; then
    echo "📄 最后 10 行错误日志:"
    echo ""
    tail -n 10 /var/log/eims/error.log
    echo ""
    
    # 检查是否有严重错误
    if tail -n 50 /var/log/eims/error.log | grep -qi "error\|exception\|traceback"; then
        echo "⚠️  发现错误信息"
    else
        echo "✅ 未发现明显错误"
    fi
else
    echo "ℹ️  未找到 Gunicorn 日志文件"
fi
echo ""

# 检查项 8：磁盘空间
echo "🔍 检查 8：磁盘空间"
echo "-----------------------------------"
df -h / | tail -n 1
disk_usage=$(df / | tail -n 1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -gt 90 ]; then
    echo "⚠️  磁盘空间不足（使用率：${disk_usage}%）"
else
    echo "✅ 磁盘空间充足（使用率：${disk_usage}%）"
fi
echo ""

# 检查项 9：内存使用
echo "🔍 检查 9：内存使用"
echo "-----------------------------------"
free -h | grep Mem
mem_available=$(free -h | awk '/Mem:/ {print $7}')
echo "可用内存：$mem_available"
echo ""

# 检查项 10：本地访问测试
echo "🔍 检查 10：本地访问测试"
echo "-----------------------------------"
if command -v curl &> /dev/null; then
    echo "正在测试访问 http://localhost:8000/admin/ ..."
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://localhost:8000/admin/)
    
    if [ "$response" = "200" ] || [ "$response" = "302" ]; then
        echo "✅ 本地访问成功 (HTTP $response)"
    else
        echo "❌ 本地访问失败 (HTTP $response)"
        echo "   Django 服务可能异常"
    fi
else
    echo "ℹ️  未安装 curl，跳过测试"
fi
echo ""

# 总结
echo "======================================"
echo "诊断完成！"
echo "======================================"
echo ""

# 统计检查结果
critical_issues=0
warnings=0

if ! ps aux | grep -E "[g]unicorn" > /dev/null; then
    ((critical_issues++))
    echo "❌ 严重问题：Gunicorn 未运行"
fi

if ! netstat -tln 2>/dev/null | grep -q ":8000"; then
    ((critical_issues++))
    echo "❌ 严重问题：端口 8000 未监听"
fi

if ! systemctl is-active --quiet supervisord; then
    ((warnings++))
    echo "⚠️  警告：Supervisor 未运行"
fi

if command -v firewall-cmd &> /dev/null; then
    if sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
        if ! sudo firewall-cmd --query-port=8000/tcp 2>/dev/null; then
            ((warnings++))
            echo "⚠️  警告：防火墙未开放 8000 端口"
        fi
    fi
fi

echo ""
if [ $critical_issues -gt 0 ]; then
    echo "🚨 发现 $critical_issues 个严重问题"
    echo ""
    echo "建议立即执行:"
    echo "  1. 启动 Supervisor: systemctl start supervisord"
    echo "  2. 启动 Gunicorn: supervisorctl start eims"
    echo "  3. 检查配置：查看 /var/log/eims/error.log"
elif [ $warnings -gt 0 ]; then
    echo "⚠️  发现 $warnings 个警告"
    echo ""
    echo "建议操作:"
    echo "  - 检查防火墙配置"
    echo "  - 检查阿里云安全组"
else
    echo "✅ 未发现明显问题"
    echo ""
    echo "如果仍无法访问，请检查:"
    echo "  1. 阿里云安全组配置"
    echo "  2. 本地网络连接"
    echo "  3. 浏览器缓存（Ctrl+F5 刷新）"
fi
echo ""
echo "======================================"
