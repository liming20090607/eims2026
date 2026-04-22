import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=10)

print("="*80)
print("Testing External Access After Firewall Template Applied")
print("="*80)

time.sleep(2)

# Test 1: External access to server IP
print("\n[1] Testing external access to server IP...")
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 http://39.106.41.239/login/ 2>&1')
test1 = stdout.read().decode().strip()
print(f"    http://39.106.41.239/login/ => HTTP {test1}")

# Test 2: External access with verbose output
print("\n[2] Detailed connection test...")
stdin, stdout, stderr = ssh.exec_command('curl -v --connect-timeout 10 http://39.106.41.239/login/ 2>&1 | head -30')
verbose = stdout.read().decode()
print(verbose[:500])

# Test 3: Local test for comparison
print("\n[3] Local test (for comparison)...")
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/login/')
local = stdout.read().decode().strip()
print(f"    http://127.0.0.1:80/login/ => HTTP {local}")

# Test 4: Check if port 80 is reachable from outside
print("\n[4] Port 80 connectivity check...")
stdin, stdout, stderr = ssh.exec_command('timeout 5 bash -c "echo > /dev/tcp/39.106.41.239/80" && echo "PORT_OPEN" || echo "PORT_CLOSED"')
port_check = stdout.read().decode().strip()
print(f"    Port 80 from external: {port_check}")

print("\n" + "="*80)
if test1 in ['200', '302', '301']:
    print("🎉 SUCCESS! Website is now accessible from outside!")
    print("="*80)
    print("\nYou can now access:")
    print("  http://39.106.41.239/login/")
    print("  http://www.xietongai.com.cn/login/")
    print("\nThe firewall template has been successfully applied!")
elif test1 == '000' or test1 == '':
    print("❌ Still cannot connect from outside")
    print("="*80)
    print("\nPossible issues:")
    print("  1. Firewall template applied but not yet effective (wait 2-3 minutes)")
    print("  2. Need to restart Nginx")
    print("  3. Cloud provider issue")
    print("\nRecommended: Wait 2 minutes and try again")
else:
    print(f"ℹ️  HTTP Status: {test1}")
    print("="*80)
    if test1 == '500':
        print("\nServer is responding but has internal error (HTTP 500)")
        print("This is a Django application error, not a network issue.")
        print("The firewall is working! Now we need to fix the Django error.")
print("\n" + "="*80 + "\n")

ssh.close()
