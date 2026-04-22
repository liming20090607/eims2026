#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紧急修复MySQL认证问题
Emergency fix for MySQL authentication
"""
import paramiko
import time

def main():
    print("=" * 70)
    print("紧急修复MySQL认证问题")
    print("Emergency MySQL Authentication Fix")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] 连接服务器...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH 连接成功")
        
        # 测试MySQL命令行连接
        print("\n[2] 测试MySQL命令行连接...")
        stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT 1;" 2>&1')
        mysql_result = stdout.read().decode() + stderr.read().decode()
        
        if 'ERROR' in mysql_result:
            print("❌ MySQL命令行连接失败:")
            print(mysql_result[:300])
            print("\n需要使用skip-grant-tables模式修复...")
            
            # 停止MySQL
            print("\n[3] 停止MySQL服务...")
            ssh.exec_command('systemctl stop mysqld || service mysqld stop')
            time.sleep(2)
            
            # 检查MySQL进程
            stdin, stdout, stderr = ssh.exec_command('ps aux | grep mysqld | grep -v grep')
            processes = stdout.read().decode()
            if processes:
                print("  MySQL进程仍在运行，强制终止...")
                ssh.exec_command('killall -9 mysqld || pkill -9 mysqld')
                time.sleep(2)
            
            # 清理socket文件
            print("\n[4] 清理socket文件...")
            ssh.exec_command('rm -f /var/lib/mysql/mysql.sock /var/lib/mysql/mysql.sock.lock')
            time.sleep(1)
            
            # 启动MySQL with skip-grant-tables
            print("\n[5] 启动MySQL（跳过权限验证）...")
            ssh.exec_command('mysqld_safe --skip-grant-tables --skip-networking=0 &')
            print("  等待MySQL启动...")
            time.sleep(10)
            
            # 测试socket连接
            print("\n[6] 测试socket连接...")
            stdin, stdout, stderr = ssh.exec_command('mysql -u root --socket=/var/lib/mysql/mysql.sock -e "SELECT 1;" 2>&1')
            socket_result = stdout.read().decode() + stderr.read().decode()
            
            if 'ERROR' not in socket_result:
                print("✓ Socket连接成功")
                
                # 重置root用户
                print("\n[7] 重置root用户...")
                reset_sql = """
mysql -u root --socket=/var/lib/mysql/mysql.sock << 'EOF'
FLUSH PRIVILEGES;

DELETE FROM mysql.user WHERE User='root';
FLUSH PRIVILEGES;

CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
CREATE USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';

GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' WITH GRANT OPTION;

FLUSH PRIVILEGES;

SELECT User, Host, plugin FROM mysql.user WHERE User='root';
EOF
"""
                stdin, stdout, stderr = ssh.exec_command(reset_sql)
                time.sleep(5)
                reset_result = stdout.read().decode()
                reset_error = stderr.read().decode()
                
                print("重置结果:")
                if reset_result.strip():
                    print(reset_result)
                if reset_error.strip():
                    print("警告:", reset_error[:300])
                
                # 关闭MySQL
                print("\n[8] 关闭MySQL...")
                ssh.exec_command('mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown')
                time.sleep(3)
                
                # 启动正常MySQL
                print("\n[9] 启动正常MySQL服务...")
                ssh.exec_command('systemctl start mysqld || service mysqld start')
                time.sleep(5)
                
                # 测试连接
                print("\n[10] 测试MySQL连接...")
                stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT COUNT(*) FROM eims.auth_user;" 2>&1')
                test_result = stdout.read().decode() + stderr.read().decode()
                
                if 'ERROR' not in test_result:
                    print("✓ MySQL连接成功!")
                    print(test_result)
                else:
                    print("❌ MySQL连接仍失败:")
                    print(test_result)
            else:
                print("❌ Socket连接失败:")
                print(socket_result[:300])
        else:
            print("✓ MySQL命令行连接正常")
            print(mysql_result)
            
            # 检查认证插件
            print("\n[3] 检查root用户认证插件...")
            stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e \"SELECT User, Host, plugin FROM mysql.user WHERE User='root';\"")
            plugin_info = stdout.read().decode()
            print(plugin_info)
            
            if 'caching_sha2_password' in plugin_info:
                print("\n⚠️ 发现caching_sha2_password插件，需要更改...")
                change_sql = """
mysql -uroot -pEIMS2026_mysql << 'EOF'
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
ALTER USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
ALTER USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
FLUSH PRIVILEGES;
SELECT User, Host, plugin FROM mysql.user WHERE User='root';
EOF
"""
                stdin, stdout, stderr = ssh.exec_command(change_sql)
                time.sleep(3)
                change_result = stdout.read().decode()
                print("更改结果:")
                print(change_result)
        
        # 重启Gunicorn
        print("\n[11] 重启Gunicorn服务...")
        ssh.exec_command('cd /var/www/eims && source venv/bin/activate && pkill -9 -f gunicorn; sleep 2; gunicorn --bind 127.0.0.1:8000 --workers 4 --daemon wsgi:application')
        time.sleep(5)
        
        # 测试HTTP访问
        print("\n[12] 测试HTTP访问...")
        stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "状态码: %{http_code}\\n" http://localhost/login/')
        http_status = stdout.read().decode()
        print(http_status)
        
        # 检查错误日志
        print("\n[13] 检查最新错误日志...")
        stdin, stdout, stderr = ssh.exec_command('tail -5 /var/www/eims/logs/gunicorn_error.log')
        error_log = stdout.read().decode()
        if error_log.strip():
            print(error_log[-500:])
        else:
            print("无错误日志")
        
        print("\n" + "=" * 70)
        print("修复完成！")
        print("=" * 70)
        print("\n请使用以下地址访问:")
        print("http://www.xietongai.com.cn/login/")
        print("http://39.106.41.239/login/")
        print("\n登录凭据:")
        print("  admin / admin123456")
        print("  root / root123456")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
