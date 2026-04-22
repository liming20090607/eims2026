import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Checking server database setup...")
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # Check what databases exist
    print("\n[1] All MySQL databases:")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SHOW DATABASES;" 2>&1')
    output = stdout.read().decode('utf-8')
    print(output)
    
    # Check if eims_dingce database exists
    print("\n[2] Checking for eims_dingce database:")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = \'eims_dingce\';" 2>&1')
    output = stdout.read().decode('utf-8')
    print(output)
    
    # Check project directory structure
    print("\n[3] Project directory structure:")
    stdin, stdout, stderr = ssh.exec_command('ls -la /www/wwwroot/EIMS2026/ | head -20')
    output = stdout.read().decode('utf-8')
    print(output)
    
    # Check if there are multiple system directories
    print("\n[4] All directories in /www/wwwroot/:")
    stdin, stdout, stderr = ssh.exec_command('ls -la /www/wwwroot/')
    output = stdout.read().decode('utf-8')
    print(output)
    
    # Check current .env file content
    print("\n[5] Current .env file:")
    stdin, stdout, stderr = ssh.exec_command('cat /www/wwwroot/EIMS2026/.env 2>&1')
    env_content = stdout.read().decode('utf-8')
    if env_content.strip():
        print(env_content)
    else:
        print("[EMPTY or NOT FOUND]")
    
    # Check settings.py location
    print("\n[6] Settings.py location:")
    stdin, stdout, stderr = ssh.exec_command('find /www/wwwroot/EIMS2026 -name "settings.py" -type f 2>&1')
    output = stdout.read().decode('utf-8')
    print(output)
    
finally:
    ssh.close()
    print("\nDone!")
