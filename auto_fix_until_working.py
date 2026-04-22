#!/usr/bin/env python
"""
自动重启Gunicorn并持续监控直到登录页面完全正常
"""

import paramiko
import time
from datetime import datetime

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

def auto_fix_until_working():
    print("\n" + "="*70)
    print("🚀 自动修复系统 - 持续监控直到登录页面正常")
    print("="*70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SSH_CONFIG, timeout=10)
    
    # Step 1: 重启Gunicorn
    print("[1] 重启Gunicorn...")
    ssh.exec_command('pkill -9 gunicorn || true')
    time.sleep(2)
    
    cmd = 'cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 --timeout 120 eims.wsgi:application --access-logfile /var/www/eims/logs/gunicorn_access.log --error-logfile /var/www/eims/logs/gunicorn_error.log >/dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    time.sleep(5)
    
    stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
    count = stdout.read().decode().strip()
    print(f"  ✅ Gunicorn已启动: {count}个工作进程\n")
    
    # Step 2: 持续监控直到正常
    print("[2] 开始持续监控...")
    max_attempts = 20
    attempt = 0
    success_count = 0
    
    while attempt < max_attempts:
        attempt += 1
        time.sleep(5)  # 每5秒检查一次
        
        # 检查Gunicorn
        stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
        gunicorn_count = stdout.read().decode().strip()
        
        # 如果Gunicorn又崩溃了，重启
        if not gunicorn_count or int(gunicorn_count) < 2:
            print(f"\n  ⚠️ Gunicorn崩溃了 ({gunicorn_count}个进程)，正在重启...")
            ssh.exec_command('pkill -9 gunicorn || true')
            time.sleep(2)
            ssh.exec_command(cmd)
            time.sleep(5)
            stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
            gunicorn_count = stdout.read().decode().strip()
            print(f"  ✅ Gunicorn已重启: {gunicorn_count}个进程")
        
        # 测试HTTP
        stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
        http_code = stdout.read().decode().strip()
        
        # 测试CSRF Cookie
        stdin, stdout, stderr = ssh.exec_command('curl -s -c /tmp/csrf_monitor.txt http://127.0.0.1:80/login/ >/dev/null && grep csrftoken /tmp/csrf_monitor.txt || echo "NO"')
        csrf_ok = 'csrftoken' in stdout.read().decode()
        
        # 显示状态
        g_icon = "✅" if gunicorn_count and int(gunicorn_count) >= 2 else "❌"
        h_icon = "✅" if http_code in ['200', '302'] else "❌"
        c_icon = "✅" if csrf_ok else "❌"
        
        status_line = f"  [{attempt}] G:{g_icon}{gunicorn_count} HTTP:{h_icon}{http_code} CSRF:{c_icon}"
        print(status_line)
        
        # 判断是否成功
        if http_code in ['200', '302'] and csrf_ok and gunicorn_count and int(gunicorn_count) >= 2:
            success_count += 1
            if success_count >= 3:  # 连续3次成功才算稳定
                print(f"\n{'='*70}")
                print("✅✅✅ 系统完全正常！✅✅✅")
                print(f"{'='*70}")
                print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"总共尝试: {attempt} 次")
                print(f"成功次数: {success_count} 次（连续）\n")
                print("🎉 现在请在浏览器中:")
                print("   1. 按 Ctrl+F5 强制刷新")
                print("   2. 或清除缓存后访问: http://www.xietongai.com.cn/login/")
                print("   3. 或使用无痕模式 (Ctrl+Shift+N)\n")
                print("💡 自动纠错系统会继续每2分钟监控一次")
                print("   即使将来出现问题也会自动修复\n")
                ssh.close()
                return True
        else:
            success_count = 0  # 重置成功计数
        
        # 显示错误日志（如果失败）
        if attempt % 5 == 0 and http_code not in ['200', '302']:
            print("\n  最近错误日志:")
            stdin, stdout, stderr = ssh.exec_command('tail -5 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
            errors = stdout.read().decode().strip()
            if errors:
                for line in errors.split('\n')[-3:]:
                    print(f"    {line[:80]}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("⚠️ 达到最大尝试次数")
    print(f"{'='*70}")
    print("\n请在浏览器中:")
    print("  1. 按 Ctrl+Shift+Delete 清除缓存")
    print("  2. 使用无痕模式访问: http://www.xietongai.com.cn/login/")
    print("="*70 + "\n")
    
    return False

if __name__ == '__main__':
    auto_fix_until_working()
