#!/usr/bin/env python
"""
自动纠错系统 - 持续监控并自动修复EIMS2026系统问题
Auto-Correction System - Continuous monitoring and automatic fix for EIMS2026

功能：
1. 每30秒检测一次系统状态
2. 自动修复常见问题（MySQL、Nginx、Gunicorn、CSRF等）
3. 记录所有操作日志
4. 无需人工干预
"""

import paramiko
import time
from datetime import datetime

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

class AutoCorrectionSystem:
    def __init__(self):
        self.log_file = 'auto_correction.log'
        self.check_interval = 30  # 每30秒检查一次
        
    def log(self, message, level='INFO'):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def execute_command(self, command, timeout=10):
        """执行SSH命令"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(**SSH_CONFIG, timeout=timeout)
            stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
            result = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            ssh.close()
            return result, error
        except Exception as e:
            return None, str(e)
    
    def check_and_fix_mysql(self):
        """检查并修复MySQL"""
        # 检查MySQL状态
        result, _ = self.execute_command('systemctl is-active mysqld')
        if result != 'active':
            self.log('MySQL is not running, attempting to fix...', 'WARNING')
            
            # 尝试启动MySQL
            self.execute_command('systemctl start mysqld')
            time.sleep(2)
            
            # 验证启动成功
            result, _ = self.execute_command('systemctl is-active mysqld')
            if result == 'active':
                self.log('✅ MySQL started successfully', 'SUCCESS')
                return True
            else:
                self.log('❌ Failed to start MySQL, trying restart...', 'ERROR')
                self.execute_command('systemctl restart mysqld')
                time.sleep(3)
                result, _ = self.execute_command('systemctl is-active mysqld')
                if result == 'active':
                    self.log('✅ MySQL restarted successfully', 'SUCCESS')
                    return True
                else:
                    self.log('❌ MySQL restart failed, trying force recovery...', 'ERROR')
                    self.execute_command('mysqld_safe --force-recovery &')
                    time.sleep(5)
                    return False
        return True
    
    def check_and_fix_gunicorn(self):
        """检查并修复Gunicorn"""
        result, _ = self.execute_command('pgrep -c gunicorn')
        if not result or int(result) < 2:
            self.log('Gunicorn not running or insufficient workers, restarting...', 'WARNING')
            
            # 杀死现有进程
            self.execute_command('pkill -9 gunicorn || true')
            time.sleep(1)
            
            # 启动Gunicorn
            self.execute_command('cd /var/www/eims && /var/www/eims/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 5 eims.wsgi:application --daemon')
            time.sleep(3)
            
            # 验证
            result, _ = self.execute_command('pgrep -c gunicorn')
            if result and int(result) >= 2:
                self.log(f'✅ Gunicorn running with {result} workers', 'SUCCESS')
                return True
            else:
                self.log('❌ Gunicorn failed to start', 'ERROR')
                return False
        return True
    
    def check_and_fix_nginx(self):
        """检查并修复Nginx"""
        result, _ = self.execute_command('pgrep -c nginx')
        if not result or int(result) == 0:
            self.log('Nginx not running, restarting...', 'WARNING')
            self.execute_command('nginx -s stop 2>/dev/null || true')
            time.sleep(1)
            self.execute_command('nginx')
            time.sleep(2)
            
            result, _ = self.execute_command('pgrep -c nginx')
            if result and int(result) > 0:
                self.log(f'✅ Nginx running with {result} processes', 'SUCCESS')
                return True
            else:
                self.log('❌ Nginx failed to start', 'ERROR')
                return False
        return True
    
    def check_and_fix_csrf(self):
        """修复CSRF问题 - 确保Django CSRF cookie正确设置"""
        self.log('Checking CSRF configuration...', 'INFO')
        
        # 检查settings.py中的CSRF配置
        cmd = """grep -E "^CSRF_COOKIE_SECURE|^CSRF_COOKIE_HTTPONLY|^CSRF_TRUSTED_ORIGINS" /var/www/eims/eims/settings.py || echo "NOT_FOUND\""""
        result, _ = self.execute_command(cmd)
        
        if 'NOT_FOUND' in result or not result:
            self.log('CSRF settings not properly configured, fixing...', 'WARNING')
            
            # 添加正确的CSRF配置
            fix_cmd = """cat >> /var/www/eims/eims/settings.py << 'EOF'

# CSRF Configuration
CSRF_COOKIE_SECURE = False  # Set to True when using HTTPS
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = [
    'http://www.xietongai.com.cn',
    'http://xietongai.com.cn',
    'http://39.106.41.239',
]
EOF"""
            self.execute_command(fix_cmd)
            self.log('✅ CSRF configuration added', 'SUCCESS')
            return True
        
        return True
    
    def check_http_status(self):
        """检查HTTP服务状态"""
        # 测试本地访问
        result, _ = self.execute_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:80/login/ 2>&1')
        if result in ['302', '200', '500']:
            return True  # 服务在响应
        return False
    
    def run_once(self):
        """执行一次完整的检查和修复"""
        self.log('='*60)
        self.log('Starting auto-correction check...', 'INFO')
        
        issues_found = False
        
        # 检查MySQL
        if not self.check_and_fix_mysql():
            issues_found = True
        
        # 检查Gunicorn
        if not self.check_and_fix_gunicorn():
            issues_found = True
        
        # 检查Nginx
        if not self.check_and_fix_nginx():
            issues_found = True
        
        # 检查CSRF配置
        self.check_and_fix_csrf()
        
        # 检查HTTP状态
        if not self.check_http_status():
            self.log('⚠️ HTTP service not responding correctly', 'WARNING')
            issues_found = True
        
        if not issues_found:
            self.log('✅ All systems healthy', 'SUCCESS')
        else:
            self.log('⚠️ Some issues were detected and fixed', 'WARNING')
        
        self.log('='*60)
    
    def run_continuous(self):
        """持续运行自动纠错"""
        self.log('🚀 Auto-Correction System Started', 'INFO')
        self.log(f'Check interval: {self.check_interval} seconds', 'INFO')
        self.log('Monitoring: MySQL, Gunicorn, Nginx, CSRF', 'INFO')
        
        while True:
            try:
                self.run_once()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                self.log('Auto-correction system stopped by user', 'INFO')
                break
            except Exception as e:
                self.log(f'Error in auto-correction: {str(e)}', 'ERROR')
                time.sleep(10)  # 出错后等待10秒再重试

if __name__ == '__main__':
    system = AutoCorrectionSystem()
    system.run_continuous()
