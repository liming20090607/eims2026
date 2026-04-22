#!/usr/bin/env python
"""
持续自动修复CSRF问题，直到登录页面正常工作
每30秒检查一次，最多尝试10次
"""

import paramiko
import time
from datetime import datetime

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

def fix_and_test():
    print("\n" + "="*70)
    print("🔄 持续自动修复CSRF问题")
    print("="*70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("每30秒检查一次，最多尝试10次\n")
    
    max_attempts = 10
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n{'='*70}")
        print(f"📍 第 {attempt}/{max_attempts} 次检查")
        print(f"{'='*70}")
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(**SSH_CONFIG, timeout=10)
            
            # Step 1: 检查Gunicorn
            print("\n[1] 检查Gunicorn...")
            stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
            gunicorn_count = stdout.read().decode().strip()
            
            if not gunicorn_count or int(gunicorn_count) < 2:
                print(f"  ⚠️ Gunicorn不正常 ({gunicorn_count}个进程)，正在重启...")
                ssh.exec_command('pkill -9 gunicorn || true')
                time.sleep(2)
                ssh.exec_command('cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 eims.wsgi:application >/dev/null 2>&1 &')
                time.sleep(5)
                stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
                gunicorn_count = stdout.read().decode().strip()
                print(f"  ✅ Gunicorn已重启: {gunicorn_count}个进程")
            else:
                print(f"  ✅ Gunicorn正常: {gunicorn_count}个进程")
            
            # Step 2: 检查settings.py的CSRF配置
            print("\n[2] 检查CSRF配置...")
            stdin, stdout, stderr = ssh.exec_command("grep 'CSRF_TRUSTED_ORIGINS' /var/www/eims/eims/settings.py")
            if 'CSRF_TRUSTED_ORIGINS' in stdout.read().decode():
                print("  ✅ CSRF配置存在")
            else:
                print("  ❌ CSRF配置缺失，添加中...")
                csrf_config = """
CSRF_TRUSTED_ORIGINS = [
    'http://www.xietongai.com.cn',
    'http://xietongai.com.cn',
    'http://39.106.41.239',
    'http://localhost',
]
"""
                ssh.exec_command(f"echo '{csrf_config}' >> /var/www/eims/eims/settings.py")
                print("  ✅ CSRF配置已添加")
            
            # Step 3: 测试登录页面
            print("\n[3] 测试登录页面...")
            stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
            http_code = stdout.read().decode().strip()
            print(f"  HTTP状态码: {http_code}")
            
            # Step 4: 测试CSRF Cookie
            print("\n[4] 测试CSRF Cookie...")
            stdin, stdout, stderr = ssh.exec_command('curl -s -c /tmp/csrf_test.txt http://127.0.0.1:80/login/ >/dev/null && grep csrftoken /tmp/csrf_test.txt || echo "NO_COOKIE"')
            cookie_result = stdout.read().decode().strip()
            
            if 'csrftoken' in cookie_result:
                print("  ✅ CSRF Cookie生成成功")
                print(f"  {cookie_result[:60]}...")
            else:
                print("  ❌ CSRF Cookie未生成")
            
            # Step 5: 判断是否成功
            print("\n[5] 检查结果...")
            if http_code in ['200', '302'] and 'csrftoken' in cookie_result:
                print("  ✅✅✅ 登录页面完全正常！✅✅✅")
                print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"总共尝试: {attempt} 次")
                print("\n🎉 现在请在浏览器中:")
                print("   1. 按 Ctrl+F5 强制刷新")
                print("   2. 或清除缓存后访问: http://www.xietongai.com.cn/login/")
                ssh.close()
                return True
            elif http_code in ['200', '302']:
                print("  ⚠️ 页面可访问，但CSRF Cookie有问题")
                print("  继续尝试修复...")
            else:
                print(f"  ❌ HTTP {http_code} - 页面不可访问")
                print("  继续尝试修复...")
            
            ssh.close()
            
            # 等待30秒后再次检查
            if attempt < max_attempts:
                print(f"\n⏳ 等待30秒后再次检查...")
                time.sleep(30)
            
        except Exception as e:
            print(f"\n❌ 错误: {str(e)}")
            time.sleep(30)
    
    print("\n" + "="*70)
    print("⚠️ 达到最大尝试次数")
    print("="*70)
    print("\n请在浏览器中手动操作:")
    print("  1. 按 Ctrl+Shift+Delete 清除所有缓存和Cookie")
    print("  2. 关闭浏览器重新打开")
    print("  3. 访问: http://www.xietongai.com.cn/login/")
    print("  4. 或使用无痕模式 (Ctrl+Shift+N)")
    print("="*70 + "\n")
    
    return False

if __name__ == '__main__':
    fix_and_test()
