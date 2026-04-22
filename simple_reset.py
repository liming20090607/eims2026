import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', key_filename='C:/Users/Administrator/.ssh/id_rsa', timeout=15)

print("Step 1: Stopping MySQL...")
ssh.exec_command("systemctl stop mysqld")

import time
time.sleep(2)

print("Step 2: Starting MySQL in safe mode...")
ssh.exec_command("mysqld_safe --skip-grant-tables &")
time.sleep(4)

print("Step 3: Resetting password...")
stdin, stdout, stderr = ssh.exec_command("""mysql -u root <<'EOF'
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'mysql2026!';
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'mysql2026!';
FLUSH PRIVILEGES;
EOF
""")
print(stdout.read().decode())
print(stderr.read().decode())

time.sleep(2)

print("Step 4: Restarting MySQL normally...")
ssh.exec_command("kill $(cat /var/run/mysqld/mysqld.pid 2>/dev/null) 2>/dev/null || pkill -9 mysqld_safe")
time.sleep(2)
ssh.exec_command("systemctl start mysqld")
time.sleep(4)

print("Step 5: Testing new password...")
stdin, stdout, stderr = ssh.exec_command('mysql -u root -pmysql2026! -e "SELECT 1;" 2>&1')
output = stdout.read().decode()
error = stderr.read().decode()
print("Output:", output)
print("Error:", error)

if 'Access denied' not in error:
    print("\n✅ SUCCESS! Password reset to: mysql2026!")
    
    print("\nStep 6: Updating .env file...")
    ssh.exec_command('sed -i \'s/DB_PASSWORD=.*/DB_PASSWORD="mysql2026!"/\' /var/www/eims/.env')
    
    print("Step 7: Restarting Gunicorn...")
    ssh.exec_command("pkill -9 -f gunicorn || true")
    time.sleep(2)
    ssh.exec_command("cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 --daemon wsgi:application")
    time.sleep(3)
    
    print("Step 8: Testing website...")
    stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w 'HTTP %{http_code}\\n' http://127.0.0.1:8000/login/")
    print(stdout.read().decode())
    
    print("\n✅ ALL DONE! Please test at http://www.xietongai.com.cn/login/")
else:
    print("\n❌ FAILED! Please check MySQL logs")

ssh.close()
