#!/bin/bash
# 服务器诊断与修复脚本 - admin 用户专用
# 使用方法：以 admin 身份登录后执行此脚本

echo "======================================"
echo "EIMS 服务器诊断与修复 (admin 用户)"
echo "======================================"
echo ""

# 检查 sudo 权限
if ! sudo -v &>/dev/null; then
    echo "❌ 错误：admin 用户需要 sudo 权限"
    echo "   请确认 admin 用户已添加到 wheel 组"
    exit 1
fi

echo "✅ admin 用户 sudo 权限正常"
echo ""

# 检查 1：系统状态
echo "📊 检查 1：系统基本状态"
echo "-----------------------------------"
echo "系统运行时间："
sudo uptime
echo ""
echo "内存使用："
sudo free -h
echo ""
echo "磁盘空间："
sudo df -h /
echo ""

# 检查 2：网络状态
echo " 检查 2：网络状态"
echo "-----------------------------------"
echo "IP 地址："
ip addr show eth0 2>/dev/null | grep "inet " || echo "未找到 eth0"
echo ""
echo "外网连通性："
ping -c 2 -W 1 www.baidu.com > /dev/null 2>&1 && echo "✅ 网络正常" || echo "❌ 网络异常"
echo ""

# 检查 3：SSH 服务
echo "🔐 检查 3：SSH 服务"
echo "-----------------------------------"
sudo systemctl status sshd --no-pager | head -n 5
echo ""

# 检查 4：Gunicorn 进程
echo "🔍 检查 4：Gunicorn 进程"
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

# 检查 5：Supervisor 状态
echo "🔍 检查 5：Supervisor 状态"
echo "-----------------------------------"
if sudo systemctl is-active --quiet supervisord; then
    echo "✅ Supervisor 正在运行"
    echo ""
    echo "服务列表:"
    sudo supervisorctl status 2>/dev/null
else
    echo "❌ Supervisor 未运行"
    echo "   需要启动 Supervisor"
fi
echo ""

# 检查 6：端口监听
echo "📡 检查 6：端口监听状态"
echo "-----------------------------------"
echo "端口 8000:"
sudo netstat -tln 2>/dev/null | grep ":8000" || echo "❌ 未监听"
echo ""
echo "端口 22:"
sudo netstat -tln 2>/dev/null | grep ":22" || echo "❌ 未监听"
echo ""

# 检查 7：防火墙
echo "🛡️  检查 7：防火墙状态"
echo "-----------------------------------"
if command -v firewall-cmd &> /dev/null; then
    fw_state=$(sudo firewall-cmd --state 2>/dev/null)
    if [ "$fw_state" = "running" ]; then
        echo "🔥 防火墙已开启"
        echo "开放端口:"
        sudo firewall-cmd --list-ports 2>/dev/null
        echo ""
        
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

# 检查 8：Django 项目
echo "🔍 检查 8：Django 项目"
echo "-----------------------------------"
cd /var/www/eims
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

if [ -f "settings.py" ]; then
    echo "✅ settings.py 存在"
    
    # 检查 ALLOWED_HOSTS
    if grep -q "ALLOWED_HOSTS" settings.py; then
        echo "✅ ALLOWED_HOSTS 配置存在"
    else
        echo "⚠️  未找到 ALLOWED_HOSTS 配置"
    fi
else
    echo "❌ settings.py 不存在"
fi
echo ""

# 检查 9：错误日志
echo "📄 检查 9：最近的错误日志"
echo "-----------------------------------"
if [ -f "/var/log/eims/error.log" ]; then
    echo "最后 10 行错误日志:"
    sudo tail -n 10 /var/log/eims/error.log
    echo ""
    
    # 检查是否有严重错误
    if sudo tail -n 50 /var/log/eims/error.log | grep -qi "error\|exception\|traceback"; then
        echo "⚠️  发现错误信息"
    else
        echo "✅ 未发现明显错误"
    fi
else
    echo "ℹ️  未找到 Gunicorn 日志文件"
fi
echo ""

# 自动修复选项
echo "======================================"
echo "自动修复选项"
echo "======================================"
echo ""
echo "选择要执行的操作:"
echo "1. 启动 Supervisor 和 Gunicorn (推荐)"
echo "2. 重启所有服务"
echo "3. 查看错误日志"
echo "4. 测试本地访问"
echo "5. 开放防火墙 8000 端口"
echo "6. 退出"
echo ""
read -p "请输入选项 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "正在启动 Supervisor..."
        sudo systemctl start supervisord
        sleep 2
        
        echo "正在启动 Gunicorn..."
        sudo supervisorctl start eims
        sleep 2
        
        echo ""
        echo "服务状态:"
        sudo supervisorctl status eims
        ;;
    
    2)
        echo ""
        echo "正在重启所有服务..."
        sudo systemctl restart supervisord
        sleep 2
        sudo supervisorctl restart all
        sleep 2
        
        echo ""
        echo "服务状态:"
        sudo supervisorctl status
        ;;
    
    3)
        echo ""
        echo "=== Gunicorn 错误日志 (最后 20 行) ==="
        if [ -f "/var/log/eims/error.log" ]; then
            sudo tail -n 20 /var/log/eims/error.log
        else
            echo "未找到日志文件"
        fi
        echo ""
        echo "=== Supervisor 错误日志 (最后 20 行) ==="
        if [ -f "/var/log/supervisor/supervisord.log" ]; then
            sudo tail -n 20 /var/log/supervisor/supervisord.log
        else
            echo "未找到日志文件"
        fi
        ;;
    
    4)
        echo ""
        echo "正在测试本地访问..."
        if command -v curl &> /dev/null; then
            response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://localhost:8000/admin/)
            echo "HTTP 响应码：$response"
            
            if [ "$response" = "200" ] || [ "$response" = "302" ]; then
                echo "✅ 本地访问成功"
            else
                echo "⚠️  本地访问异常 (HTTP $response)"
            fi
        else
            echo "ℹ️  未安装 curl"
        fi
        ;;
    
    5)
        echo ""
        echo "正在开放 8000 端口..."
        if command -v firewall-cmd &> /dev/null; then
            if sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
                sudo firewall-cmd --permanent --add-port=8000/tcp
                sudo firewall-cmd --reload
                echo "✅ 8000 端口已开放"
            else
                echo "ℹ️  防火墙未运行"
            fi
        else
            echo "ℹ️  未安装 firewalld"
        fi
        ;;
    
    6)
        echo "退出"
        exit 0
        ;;
    
    *)
        echo "无效的选项"
        ;;
esac

echo ""
echo "======================================"
echo "诊断完成"
echo "======================================"
echo ""

# 最终状态检查
echo "最终状态:"
echo ""
echo "Gunicorn 进程:"
ps aux | grep -E "[g]unicorn" | head -n 3 || echo "未运行"
echo ""

echo "端口 8000 监听:"
sudo netstat -tln 2>/dev/null | grep ":8000" || echo "未监听"
echo ""

echo "Supervisor 状态:"
sudo supervisorctl status eims 2>/dev/null || echo "未配置"
echo ""

echo "======================================"
echo "提示："
echo "  - 如果服务已启动，请访问：http://39.106.41.239:8000/"
echo "  - 如果仍无法访问，检查阿里云安全组配置"
echo "  - 按 Ctrl+F5 强制刷新浏览器"
echo "======================================"
