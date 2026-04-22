import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Checking database configuration on server...")
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # Check .env file
    print("\n[1] Checking .env file...")
    stdin, stdout, stderr = ssh.exec_command('cat /www/wwwroot/EIMS2026/.env')
    env_content = stdout.read().decode('utf-8')
    print(env_content)
    
    # Check settings.py database config
    print("\n[2] Checking settings.py database configuration...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 20 "DATABASES" /www/wwwroot/EIMS2026/settings.py | head -30')
    db_config = stdout.read().decode('utf-8')
    print(db_config)
    
    # Test MySQL connection with current password
    print("\n[3] Testing MySQL connection...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT 1 AS test;" 2>&1')
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if output and '1' in output:
        print("[OK] MySQL connection successful with password 'EIMS2026_mysql'")
    else:
        print("[ERROR] MySQL connection failed")
        print("Error:", error)
    
    # List databases
    print("\n[4] Available databases...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SHOW DATABASES;" 2>&1')
    output = stdout.read().decode('utf-8')
    print(output)
    
finally:
    ssh.close()
    print("\nDone!")
