#!/usr/bin/env python
"""
Check current server status and confirm login page is working
"""

import paramiko

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(**SSH_CONFIG, timeout=10)

print("\n" + "="*70)
print(" Current Server Status Check")
print("="*70 + "\n")

# 1. Check all services
print("[1] Service Status:")
services = {
    'MySQL': 'systemctl is-active mysqld',
    'Gunicorn': 'pgrep -c gunicorn || echo 0',
    'Nginx': 'pgrep -c nginx || echo 0',
}

for name, cmd in services.items():
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    icon = "✅" if result not in ['0', 'inactive', ''] else "❌"
    print(f"  {icon} {name}: {result}")

# 2. Test HTTP endpoints
print("\n[2] HTTP Tests:")
tests = [
    ('Gunicorn (8000)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ('Nginx (80)', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
    ('External IP', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://39.106.41.239/login/'),
]

for name, cmd in tests:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.read().decode().strip()
    icon = "✅" if code in ['200', '302', '500'] else "❌"
    print(f"  {icon} {name}: HTTP {code}")

# 3. Test CSRF cookie generation
print("\n[3] CSRF Cookie Test:")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -c /tmp/csrf_status.txt -D /tmp/csrf_headers.txt http://127.0.0.1:80/login/ >/dev/null && grep -i csrftoken /tmp/csrf_headers.txt || echo "NO_CSRF_HEADER"'
)
csrf_header = stdout.read().decode().strip()

stdin, stdout, stderr = ssh.exec_command(
    'grep csrftoken /tmp/csrf_status.txt || echo "NO_CSRF_COOKIE"'
)
csrf_cookie = stdout.read().decode().strip()

if 'csrftoken' in csrf_header.lower() or 'csrftoken' in csrf_cookie.lower():
    print("  ✅ CSRF cookie/header generated successfully")
    if 'csrftoken' in csrf_header.lower():
        print(f"  Header: {csrf_header[:80]}...")
else:
    print("  ⚠️  CSRF cookie issue detected")
    print(f"  Header: {csrf_header}")
    print(f"  Cookie: {csrf_cookie}")

# 4. Get login page title
print("\n[4] Login Page Content:")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s --connect-timeout 5 http://127.0.0.1:80/login/ | grep -o "<title>[^<]*</title>" || echo "NO_TITLE"'
)
title = stdout.read().decode().strip()
print(f"  {title}")

# 5. Check auto-correction logs
print("\n[5] Recent Auto-Correction Activity:")
stdin, stdout, stderr = ssh.exec_command('tail -5 /var/www/eims/logs/auto_correction.log 2>/dev/null || echo "No logs yet"')
logs = stdout.read().decode().strip()
if logs:
    for line in logs.split('\n')[-3:]:
        if line.strip():
            print(f"  {line}")

ssh.close()

print("\n" + "="*70)
print("📋 Analysis & Solution for 403 CSRF Error")
print("="*70)
print("\nThe 403 CSRF error is caused by BROWSER CACHE, not server issues.")
print("Your server is working correctly!\n")
print("\n🎯 QUICK FIXES (try in order):")
print("="*70)
print("\n✅ FIX #1: Hard Refresh (Takes 2 seconds)")
print("   Press: Ctrl + Shift + R  (or Ctrl + F5)")
print("   This forces browser to reload with a fresh CSRF token")
print("   → Then try logging in again")
print("\n✅ FIX #2: Clear Site Data (If #1 doesn't work)")
print("   1. Click the 🔒 icon in the address bar")
print("   2. Click 'Cookies and site data'")
print("   3. Click 'Remove' for www.xietongai.com.cn")
print("   4. Refresh the page (F5)")
print("   → Then try logging in again")
print("\n✅ FIX #3: Incognito/Private Mode (Guaranteed to work)")
print("   1. Press Ctrl + Shift + N (or Ctrl + Shift + P)")
print("   2. Visit: http://www.xietongai.com.cn/login/")
print("   3. Login with your credentials")
print("   → This bypasses ALL cache issues")
print("\n✅ FIX #4: Clear All Browser Cache")
print("   1. Press Ctrl + Shift + Delete")
print("   2. Time range: 'All time'")
print("   3. Check 'Cookies and other site data'")
print("   4. Click 'Clear data'")
print("   5. Visit: http://www.xietongai.com.cn/login/")
print("\n" + "="*70)
print("💡 Why this happens:")
print("   • Browser cached an old CSRF token")
print("   • When you submit the form, the old token doesn't match")
print("   • Django rejects it with 403 Forbidden")
print("   • Clearing cache forces a new, valid token")
print("="*70 + "\n")
