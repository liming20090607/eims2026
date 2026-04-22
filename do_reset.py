import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', key_filename='C:/Users/Administrator/.ssh/id_rsa')

# Execute password reset
cmd = """mysql -u root <<'EOSQL'
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'mysql2026!';
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'mysql2026!';
FLUSH PRIVILEGES;
SELECT 'Password updated!' AS status;
EOSQL"""

print("Resetting MySQL password...")
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("Errors:", err)

time.sleep(2)

# Kill safe mode and restart normally
print("\nRestarting MySQL normally...")
ssh.exec_command("pkill mysqld")
time.sleep(3)
ssh.exec_command("systemctl start mysqld")
time.sleep(4)

# Test new password
print("\nTesting new password...")
stdin, stdout, stderr = ssh.exec_command('mysql -u root -pmysql2026! -e "SELECT 1" 2>&1')
output = stdout.read().decode()
error = stderr.read().decode()

if 'Access denied' not in error:
    print("✅ Password reset successful!")
    
    # Update .env
    print("\nUpdating .env file...")
    ssh.exec_command('sed -i \'s/DB_PASSWORD=.*/DB_PASSWORD="mysql2026!"/\' /var/www/eims/.env')
    
    # Restart Gunicorn
    print("Restarting Gunicorn...")
    ssh.exec_command("pkill -9 -f gunicorn || true")
    time.sleep(2)
    ssh.exec_command("cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 --daemon wsgi:application")
    time.sleep(3)
    
    # Test website
    print("\nTesting website...")
    stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
    print(f"HTTP Status: {stdout.read().decode()}")
    
    print("\n✅ ALL DONE! Visit http://www.xietongai.com.cn/login/")
else:
    print("❌ Password reset failed")
    print("Error:", error)

ssh.close()
