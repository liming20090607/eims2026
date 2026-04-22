#!/usr/bin/env python3
"""
Quick MySQL Emergency Fix - Direct approach
"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("=" * 80)
print("🚨 Emergency MySQL Fix")
print("=" * 80)

# Step 1: Kill all MySQL processes
print("\n[1/5] Killing all MySQL processes...")
ssh.exec_command("killall -9 mysqld mysqld_safe 2>/dev/null; sleep 2")
time.sleep(3)

# Step 2: Clean up
print("[2/5] Cleaning socket and lock files...")
ssh.exec_command("rm -f /var/lib/mysql/mysql.sock /var/run/mysqld/mysqld.sock /var/lock/subsys/mysql")
ssh.exec_command("mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld")
time.sleep(1)

# Step 3: Start MySQL with skip-grant-tables using mysqld directly
print("[3/5] Starting MySQL in recovery mode...")
ssh.exec_command("mysqld --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock &")
print("   Waiting 15 seconds for MySQL to start...")
for i in range(15):
    print(f"   {i+1}/15", end='\r')
    time.sleep(1)
print("   ✓ Wait complete")

# Check if socket exists
stdin, stdout, stderr = ssh.exec_command("ls -la /var/lib/mysql/mysql.sock 2>&1")
socket_check = stdout.read().decode()
if 'mysql.sock' in socket_check:
    print("   ✅ Socket file created successfully!")
else:
    print("   ❌ Socket file not found")
    print(f"   Debug: {socket_check}")
    
    # Try alternative location
    stdin, stdout, stderr = ssh.exec_command("find /var -name mysql.sock 2>/dev/null")
    alt_socket = stdout.read().decode().strip()
    if alt_socket:
        print(f"   ℹ️  Found socket at: {alt_socket}")
    else:
        print("   ❌ No socket file found anywhere")

# Step 4: Reset password via socket
print("\n[4/5] Resetting root password...")
reset_cmd = """mysql -u root --socket=/var/lib/mysql/mysql.sock <<EOF
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
DROP USER IF EXISTS 'root'@'127.0.0.1';
DROP USER IF EXISTS 'root'@'::1';
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

stdin, stdout, stderr = ssh.exec_command(reset_cmd, timeout=10)
output = stdout.read().decode()
error = stderr.read().decode()

if output:
    print("   MySQL output:")
    print(output)
if error and 'ERROR' in error:
    print(f"   ⚠️  Error: {error[:300]}")
else:
    print("   ✅ Password reset commands executed")

# Step 5: Shutdown and restart normally
print("\n[5/5] Restarting MySQL normally...")
ssh.exec_command("mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall mysqld")
time.sleep(3)

ssh.exec_command("systemctl start mysqld 2>/dev/null || service mysql start 2>/dev/null || mysqld_safe --user=mysql &")
time.sleep(5)

# Verify
print("\n🔍 Verifying MySQL connection...")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 AS test;' 2>&1")
result = stdout.read().decode()
error = stderr.read().decode()

if 'test' in result.lower() or '1' in result:
    print("✅ SUCCESS! MySQL is working!")
    print(f"\n{result}")
else:
    print("❌ Still having issues")
    if error:
        print(f"Error: {error[:200]}")
    
    # Try one more thing - check if MySQL is running
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep mysql | grep -v grep")
    ps_output = stdout.read().decode()
    if ps_output:
        print("\nMySQL processes found:")
        print(ps_output[:500])
    else:
        print("\nNo MySQL processes running")

# Restart Gunicorn
print("\n🔄 Restarting Gunicorn...")
ssh.exec_command("pkill -9 -f gunicorn; sleep 2")
ssh.exec_command("cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &")
time.sleep(3)

# Test HTTP
print("\n🌐 Testing HTTP access...")
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/")
http_code = stdout.read().decode().strip()
print(f"   Login page status: {http_code}")

if http_code == '200':
    print("   ✅ Website is accessible!")
else:
    print(f"   ⚠️  Unexpected status code: {http_code}")

print("\n" + "=" * 80)
print("Fix complete!")
print("=" * 80)

ssh.close()
