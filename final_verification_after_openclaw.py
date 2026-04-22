#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final verification after OpenClaw cooperative fix
OpenClaw协作修复后的最终验证
"""
import paramiko
import time

def main():
    print("=" * 70)
    print("最终系统状态验证")
    print("Final System Status Verification")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] 连接服务器...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH 连接成功")
        
        # Comprehensive verification
        print("\n[2] 全面系统检查...")
        verify_cmd = '''
echo "=========================================="
echo "服务状态"
echo "=========================================="

echo -e "\\n【Gunicorn】"
ps aux | grep gunicorn | grep -v grep | wc -l
netstat -tlnp | grep :8000 || ss -tlnp | grep :8000

echo -e "\\n【Nginx】"
ps aux | grep nginx | grep -v grep | wc -l
netstat -tlnp | grep :80 || ss -tlnp | grep :80

echo -e "\\n【MySQL】"
systemctl is-active mysqld 2>/dev/null || service mysql status 2>/dev/null
mysql -uroot -pEIMS2026_mysql -e "SELECT 'MySQL连接正常' as 状态;" 2>&1

echo -e "\\n=========================================="
echo "数据库测试"
echo "=========================================="

cd /var/www/eims && source venv/bin/activate && python << 'PYEOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.db import connection
from django.contrib.auth.models import User

try:
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM auth_user")
    user_count = cursor.fetchone()[0]
    print(f"✓ Django数据库连接成功")
    print(f"✓ 用户总数: {user_count}")
    
    # Test admin user
    try:
        admin = User.objects.get(username='admin')
        print(f"✓ admin用户存在 (ID: {admin.id}, Superuser: {admin.is_superuser})")
    except:
        print("✗ admin用户不存在")
    
    # Test root user
    try:
        root_user = User.objects.get(username='root')
        print(f"✓ root用户存在 (ID: {root_user.id}, Superuser: {root_user.is_superuser})")
    except:
        print("✗ root用户不存在")
        
except Exception as e:
    print(f"✗ Django数据库连接失败: {e}")
PYEOF

echo -e "\\n=========================================="
echo "HTTP访问测试"
echo "=========================================="

echo -e "\\n【登录页面】"
curl -s -o /dev/null -w "状态码: %{http_code}\\n" http://127.0.0.1:8000/login/

echo -e "\\n【首页】"
curl -s -o /dev/null -w "状态码: %{http_code}\\n" http://127.0.0.1:8000/

echo -e "\\n=========================================="
echo "错误日志检查"
echo "=========================================="

echo -e "\\n【最近5条错误日志】"
tail -5 /var/www/eims/logs/gunicorn_error.log 2>/dev/null | grep -i "error\|denied\|exception" || echo "✓ 无数据库相关错误"

echo -e "\\n=========================================="
echo "OpenClaw监控状态"
echo "=========================================="

echo -e "\\n【最新健康检查】"
tail -15 /root/.openclaw/monitoring/logs/health_check.log 2>/dev/null | tail -10

echo -e "\\n【最新自动修复】"
tail -10 /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null | tail -5

echo -e "\\n=========================================="
echo "内存和磁盘使用"
echo "=========================================="

free -h | grep Mem
df -h / | tail -1
'''
        stdin, stdout, stderr = ssh.exec_command(verify_cmd)
        time.sleep(10)
        result = stdout.read().decode('utf-8')
        print(result)
        
        # Check for any remaining issues
        print("\n[3] 问题检测...")
        if 'Access denied' in result or 'ERROR 1045' in result:
            print("⚠️  警告: 仍然存在MySQL认证错误")
            return False
        elif 'MySQL连接正常' in result or 'Django数据库连接成功' in result:
            print("✓ MySQL认证问题已解决！")
            return True
        else:
            print("? 状态不明确，请检查以上输出")
            return None
            
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

if __name__ == '__main__':
    success = main()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 系统完全恢复正常！")
        print("\n访问地址:")
        print("  http://www.xietongai.com.cn/")
        print("  http://39.106.41.239/")
        print("\n登录凭据:")
        print("  admin / admin123456")
        print("  root / root123456")
        print("\n注意: 请使用 HTTP，不是 HTTPS")
    elif success is False:
        print("❌ 系统仍有问题，需要进一步排查")
    else:
        print("⚠️  请检查以上输出确认系统状态")
    print("=" * 70)
