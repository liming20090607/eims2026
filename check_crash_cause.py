import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("="*80)
print("MYSQL CRASH DIAGNOSIS")
print("="*80)

# Check MySQL error log
print("\n[1] MySQL Error Log (last 30 lines):")
stdin, stdout, stderr = ssh.exec_command('tail -30 /var/log/mysqld.log 2>/dev/null || journalctl -u mysqld -n 30 --no-pager 2>/dev/null || echo "No log available"')
error_log = stdout.read().decode()
if error_log.strip():
    # Filter to show only important lines
    for line in error_log.split('\n'):
        if any(keyword in line.lower() for keyword in ['error', 'warning', 'crash', 'shutdown', 'start', 'abort', 'failed']):
            print(f"  {line}")
else:
    print("  No error log found")

# Check system memory
print("\n[2] System Memory:")
stdin, stdout, stderr = ssh.exec_command('free -h | grep Mem')
memory = stdout.read().decode().strip()
print(f"  {memory}")

# Check disk space
print("\n[3] Disk Space:")
stdin, stdout, stderr = ssh.exec_command('df -h / | tail -1')
disk = stdout.read().decode().strip()
print(f"  {disk}")

# Check MySQL configuration
print("\n[4] MySQL Configuration:")
stdin, stdout, stderr = ssh.exec_command('grep -E "^innodb_buffer_pool|^max_connections|^key_buffer" /etc/my.cnf 2>/dev/null || echo "Using defaults"')
config = stdout.read().decode().strip()
print(f"  {config if config else '  Using default configuration'}")

# Check if MySQL is running in recovery mode
print("\n[5] MySQL Process Details:")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep mysqld | grep -v grep')
procs = stdout.read().decode()
if procs.strip():
    for line in procs.split('\n'):
        if line.strip():
            print(f"  {line}")
            if 'skip-grant-tables' in line:
                print("  [WARN] MySQL is running in recovery mode!")

# Count crashes
print("\n[6] Crash Frequency:")
stdin, stdout, stderr = ssh.exec_command('grep -c "MySQL.*repair" /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null || echo "0"')
crash_count = stdout.read().decode().strip()
print(f"  Auto-fix triggered: {crash_count} times")

stdin, stdout, stderr = ssh.exec_command('grep "MySQL" /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null | grep "==========" | wc -l')
total_repairs = stdout.read().decode().strip()
print(f"  Total repair attempts: {total_repairs}")

print("\n" + "="*80)
print("RECOMMENDATIONS")
print("="*80)

if int(crash_count) > 5:
    print("\n[CRITICAL] MySQL is crashing too frequently!")
    print("\nPossible causes:")
    print("  1. Insufficient memory (MySQL needs more RAM)")
    print("  2. Corrupted database files")
    print("  3. MySQL configuration issues")
    print("  4. Disk space problems")
    print("\nSuggested fixes:")
    print("  Option A: Increase server memory")
    print("  Option B: Optimize MySQL configuration")
    print("  Option C: Check and repair database tables")
    print("  Option D: Restart server completely")
else:
    print("\n[INFO] MySQL crash frequency is acceptable")
    print("The auto-fix system is handling it properly.")

print("\n" + "="*80 + "\n")

ssh.close()
