#!/bin/bash
# Server diagnosis and repair script - admin user
# Usage: Login as admin and run this script

echo "======================================"
echo "EIMS Server Diagnosis & Repair"
echo "======================================"
echo ""

# Check sudo permission
if ! sudo -v &>/dev/null; then
    echo "Error: admin user needs sudo permission"
    exit 1
fi

echo "Admin sudo permission: OK"
echo ""

# Check 1: System status
echo "Checking system status..."
echo "-----------------------------------"
echo "Uptime:"
sudo uptime
echo ""
echo "Memory:"
sudo free -h
echo ""
echo "Disk:"
sudo df -h /
echo ""

# Check 2: Network
echo "Checking network..."
echo "-----------------------------------"
echo "IP Address:"
ip addr show eth0 2>/dev/null | grep "inet " || echo "eth0 not found"
echo ""
echo "Internet:"
ping -c 2 -W 1 www.baidu.com > /dev/null 2>&1 && echo "OK" || echo "Failed"
echo ""

# Check 3: Gunicorn
echo "Checking Gunicorn..."
echo "-----------------------------------"
if ps aux | grep -E "[g]unicorn" > /dev/null; then
    echo "OK - Gunicorn is running"
    ps aux | grep -E "[g]unicorn" | head -n 5
else
    echo "ERROR - Gunicorn not running"
fi
echo ""

# Check 4: Supervisor
echo "Checking Supervisor..."
echo "-----------------------------------"
if sudo systemctl is-active --quiet supervisord; then
    echo "OK - Supervisor is running"
    echo ""
    echo "Services:"
    sudo supervisorctl status 2>/dev/null
else
    echo "ERROR - Supervisor not running"
fi
echo ""

# Check 5: Ports
echo "Checking ports..."
echo "-----------------------------------"
echo "Port 8000:"
sudo netstat -tln 2>/dev/null | grep ":8000" || echo "NOT listening"
echo ""
echo "Port 22:"
sudo netstat -tln 2>/dev/null | grep ":22" || echo "NOT listening"
echo ""

# Check 6: Firewall
echo "Checking firewall..."
echo "-----------------------------------"
if command -v firewall-cmd &> /dev/null; then
    fw_state=$(sudo firewall-cmd --state 2>/dev/null)
    if [ "$fw_state" = "running" ]; then
        echo "Firewall is running"
        echo "Open ports:"
        sudo firewall-cmd --list-ports 2>/dev/null
        
        if sudo firewall-cmd --query-port=8000/tcp 2>/dev/null; then
            echo "Port 8000: OPEN"
        else
            echo "Port 8000: BLOCKED"
        fi
    else
        echo "Firewall not running"
    fi
else
    echo "firewalld not installed"
fi
echo ""

# Auto repair menu
echo "======================================"
echo "Repair Options"
echo "======================================"
echo ""
echo "Select option:"
echo "1. Start Supervisor and Gunicorn (Recommended)"
echo "2. Restart all services"
echo "3. View error logs"
echo "4. Test local access"
echo "5. Open firewall port 8000"
echo "6. Exit"
echo ""
read -p "Enter choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "Starting Supervisor..."
        sudo systemctl start supervisord
        sleep 2
        
        echo "Starting Gunicorn..."
        sudo supervisorctl start eims
        sleep 2
        
        echo ""
        echo "Service status:"
        sudo supervisorctl status eims
        ;;
    
    2)
        echo ""
        echo "Restarting all services..."
        sudo systemctl restart supervisord
        sleep 2
        sudo supervisorctl restart all
        sleep 2
        
        echo ""
        echo "Service status:"
        sudo supervisorctl status
        ;;
    
    3)
        echo ""
        echo "=== Last 20 lines of error log ==="
        if [ -f "/var/log/eims/error.log" ]; then
            sudo tail -n 20 /var/log/eims/error.log
        else
            echo "Log file not found"
        fi
        ;;
    
    4)
        echo ""
        echo "Testing local access..."
        if command -v curl &> /dev/null; then
            response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://localhost:8000/admin/)
            echo "HTTP Response: $response"
            
            if [ "$response" = "200" ] || [ "$response" = "302" ]; then
                echo "Local access: OK"
            else
                echo "Local access: Failed (HTTP $response)"
            fi
        else
            echo "curl not installed"
        fi
        ;;
    
    5)
        echo ""
        echo "Opening port 8000..."
        if command -v firewall-cmd &> /dev/null; then
            if sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
                sudo firewall-cmd --permanent --add-port=8000/tcp
                sudo firewall-cmd --reload
                echo "Port 8000 opened"
            else
                echo "Firewall not running"
            fi
        else
            echo "firewalld not installed"
        fi
        ;;
    
    6)
        echo "Exit"
        exit 0
        ;;
    
    *)
        echo "Invalid option"
        ;;
esac

echo ""
echo "======================================"
echo "Done"
echo "======================================"
echo ""

# Final status
echo "Final Status:"
echo ""
echo "Gunicorn processes:"
ps aux | grep -E "[g]unicorn" | head -n 3 || echo "Not running"
echo ""

echo "Port 8000:"
sudo netstat -tln 2>/dev/null | grep ":8000" || echo "Not listening"
echo ""

echo "Supervisor status:"
sudo supervisorctl status eims 2>/dev/null || echo "Not configured"
echo ""

echo "======================================"
echo "Tips:"
echo "  - Visit: http://39.106.41.239:8000/"
echo "  - Check Alibaba Cloud Security Group"
echo "  - Press Ctrl+F5 to hard refresh browser"
echo "======================================"
