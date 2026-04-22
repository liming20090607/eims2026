import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("="*80)
print("COMPLETE MYSQL RESET - Fix File Lock Issue")
print("="*80)

# Step 1: Kill ALL MySQL processes
print("\n[1/6] Killing all MySQL processes...")
stdin, stdout, stderr = ssh.exec_command('killall -9 mysqld mysqld_safe 2>/dev/null; echo "Killed"')
print(f"    {stdout.read().decode().strip()}")
time.sleep(3)

# Verify all killed
stdin, stdout, stderr = ssh.exec_command('pgrep -c mysqld 2>/dev/null || echo "0"')
remaining = stdout.read().decode().strip()
print(f"    Remaining processes: {remaining}")

# Step 2: Clean up lock files
print("\n[2/6] Cleaning up lock and socket files...")
stdin, stdout, stderr = ssh.exec_command('rm -f /var/lib/mysql/mysql.sock /var/lib/mysql/mysqld.pid /var/lib/mysql/ibdata1.lock 2>/dev/null; echo "Cleaned"')
print(f"    {stdout.read().decode().strip()}")

# Step 3: Ensure proper permissions
print("\n[3/6] Setting correct permissions...")
stdin, stdout, stderr = ssh.exec_command('chown -R mysql:mysql /var/lib/mysql /var/run/mysqld 2>/dev/null; echo "Permissions set"')
print(f"    {stdout.read().decode().strip()}")

# Step 4: Start MySQL normally via systemctl
print("\n[4/6] Starting MySQL normally...")
stdin, stdout, stderr = ssh.exec_command('systemctl start mysqld')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("    [OK] MySQL service started")
else:
    error = stderr.read().decode().strip()
    print(f"    [WARN] Exit code: {exit_code}")
    if error:
        print(f"    Error: {error[:200]}")

time.sleep(5)

# Step 5: Verify MySQL is running properly
print("\n[5/6] Verifying MySQL status...")
for attempt in range(3):
    stdin, stdout, stderr = ssh.exec_command('systemctl is-active mysqld')
    status = stdout.read().decode().strip()
    
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep "mysqld" | grep -v grep | grep -v "skip-grant" | wc -l')
    normal_procs = stdout.read().decode().strip()
    
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep "skip-grant" | grep -v grep | wc -l')
    recovery_procs = stdout.read().decode().strip()
    
    print(f"    Attempt {attempt+1}: Service={status}, Normal={normal_procs}, Recovery={recovery_procs}")
    
    if status == "active" and int(normal_procs) > 0 and int(recovery_procs) == 0:
        print("    [OK] MySQL is running normally!")
        break
    
    time.sleep(3)

# Step 6: Test database connection
print("\n[6/6] Testing database connection...")
stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null && echo "CONNECTED" || echo "FAILED"')
db_status = stdout.read().decode().strip()
print(f"    {db_status}")

if "CONNECTED" in db_status:
    # Restart Gunicorn
    print("\n[EXTRA] Restarting Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn 2>/dev/null; sleep 2')
    time.sleep(2)
    
    gunicorn_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(gunicorn_cmd)
    time.sleep(4)
    
    stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
    gunicorn_count = stdout.read().decode().strip()
    print(f"    Gunicorn workers: {gunicorn_count}")
    
    # Test HTTP
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/')
    http_code = stdout.read().decode().strip()
    print(f"    HTTP Status: {http_code}")

print("\n" + "="*80)
print("RESET COMPLETE")
print("="*80)

if "CONNECTED" in db_status and http_code == "200":
    print("\n[SUCCESS] MySQL is fixed and website should work now!")
    print("\nTry accessing: http://www.xietongai.com.cn/login/")
else:
    print("\n[WARNING] Issues remain. Check the output above for details.")

print("\n" + "="*80 + "\n")

ssh.close()
