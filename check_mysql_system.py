import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("=== MySQL Installation Check ===\n")

# Check mysqld location
stdin, stdout, stderr = ssh.exec_command('ls -la /usr/sbin/mysqld*')
print("MySQL binaries:")
print(stdout.read().decode())

# Check systemctl
stdin, stdout, stderr = ssh.exec_command('systemctl list-unit-files | grep mysql')
print("\nSystemd services:")
print(stdout.read().decode())

# Check if mysqld_safe exists anywhere
stdin, stdout, stderr = ssh.exec_command('find /usr -name "*mysqld_safe*" 2>/dev/null')
print("\nmysqld_safe locations:")
result = stdout.read().decode().strip()
print(result if result else "NOT FOUND")

# Check MySQL version and type
stdin, stdout, stderr = ssh.exec_command('mysql --version')
print("\nMySQL version:")
print(stdout.read().decode())

ssh.close()
