#!/bin/bash
# 服务器诊断与修复脚本
# 使用方法：以 root 身份登录后执行此脚本

echo "======================================"
echo "EIMS 服务器诊断与修复"
echo "======================================"
echo ""

# 检查 1：系统状态
echo "📊 检查 1：系统基本状态"
echo "-----------------------------------"
echo "系统运行时间："
uptime
echo ""
echo "内存使用："
free -h
echo ""
echo "磁盘空间："
df -h /
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
systemctl status sshd --no-pager | head -n 5
echo ""

# 检查 4：Gunicorn 进程
echo "🔍 检查 4：Gunicorn 进程"
echo "-----------------------------------"
if ps aux | grep -E "[g]unicorn" > /dev/null; then
    echo "✅ Gunicorn 正在运行"
    ps aux | grep -E "[g]unicorn" | head -n 5
else
    echo "❌ Gunicorn 未运行"
fi
echo ""

# 检查 5：Supervisor 状态
echo "🔍 检查 5：Supervisor 状态"
echo "-----------------------------------"
if systemctl is-active --quiet supervisord; then
    echo "✅ Supervisor 正在运行"
    echo ""
    echo "服务列表:"
    supervisorctl status 2>/dev/null
else
    echo "❌ Supervisor 未运行"
fi
echo ""

# 检查 6：端口监听
echo "📡 检查 6：端口监听状态"
echo "-----------------------------------"
echo "端口 8000:"
netstat -tln 2>/dev/null | grep ":8000" || echo "❌ 未监听"
echo ""
echo "端口 22:"
netstat -tln 2>/dev/null | grep ":22" || echo "❌ 未监听"
echo ""

# 检查 7：防火墙
echo "🛡️  检查 7：防火墙状态"
echo "-----------------------------------"
if command -v firewall-cmd &> /dev/null; then
    fw_state=$(firewall-cmd --state 2>/dev/null)
    if [ "$fw_state" = "running" ]; then
        echo "🔥 防火墙已开启"
        echo "开放端口:"
        firewall-cmd --list-ports 2>/dev/null
        echo ""
        
        if firewall-cmd --query-port=8000/tcp 2>/dev/null; then
            echo "✅ 8000 端口已开放"
        else
            echo "❌ 8000 端口未开放"
            read -p "是否现在开放？(y/n): " answer
            if [ "$answer" = "y" ]; then
                firewall-cmd --permanent --add-port=8000/tcp
                firewall-cmd --reload
                echo "✅ 已开放 8000 端口"
            fi
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
    source venv/bin/activate
    
    if python -c "import gunicorn" 2>/dev/null; then
        echo "✅ Gunicorn 已安装"
    else
        echo "❌ Gunicorn 未安装"
    fi
    deactivate
else
    echo "❌ 虚拟环境不存在"
fi

if [ -f "settings.py" ]; then
    echo "✅ settings.py 存在"
else
    echo "❌ settings.py 不存在"
fi
echo ""

# 自动修复选项
echo "======================================"
echo "自动修复选项"
echo "======================================"
echo ""
echo "选择要执行的操作:"
echo "1. 启动 Supervisor 和 Gunicorn"
echo "2. 重启所有服务"
echo "3. 查看错误日志"
echo "4. 测试本地访问"
echo "5. 退出"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "正在启动 Supervisor..."
        systemctl start supervisord
        sleep 2
        
        echo "正在启动 Gunicorn..."
        supervisorctl start eims
        sleep 2
        
        echo ""
        echo "服务状态:"
        supervisorctl status eims
        ;;
    
    2)
        echo ""
        echo "正在重启所有服务..."
        systemctl restart supervisord
        sleep 2
        supervisorctl restart all
        sleep 2
        
        echo ""
        echo "服务状态:"
        supervisorctl status
        ;;
    
    3)
        echo ""
        echo "=== Gunicorn 错误日志 (最后 20 行) ==="
        if [ -f "/var/log/eims/error.log" ]; then
            tail -n 20 /var/log/eims/error.log
        else
            echo "未找到日志文件"
        fi
        echo ""
        echo "=== Supervisor 错误日志 (最后 20 行) ==="
        if [ -f "/var/log/supervisor/supervisord.log" ]; then
            tail -n 20 /var/log/supervisor/supervisord.log
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
                echo "⚠️  本地访问异常"
            fi
        else
            echo "ℹ️  未安装 curl"
        fi
        ;;
    
    5)
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
netstat -tln 2>/dev/null | grep ":8000" || echo "未监听"
echo ""

echo "Supervisor 状态:"
supervisorctl status eims 2>/dev/null || echo "未配置"
echo ""

echo "======================================"
echo "提示："
echo "  - 如果服务已启动，请访问：http://39.106.41.239:8000/"
echo "  - 如果仍无法访问，检查阿里云安全组配置"
echo "======================================"
