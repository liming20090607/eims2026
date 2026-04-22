import paramiko
import time

print("Quick login test...")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # Test login with Django test client
    test = r'''/var/www/eims/venv/bin/python3 << 'PYEOF'
import os, sys
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.test import Client
client = Client()

# GET login page
r = client.get('/login/')
print("GET:", r.status_code)

if r.status_code == 200:
    import re
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode('utf-8'))
    if match:
        csrf = match.group(1)
        r = client.post('/login/', {
            'username': 'admin',
            'password': 'admin123456',
            'csrfmiddlewaretoken': csrf
        }, follow=True)
        print("POST:", r.status_code)
        print("URL:", r.request.get('PATH_INFO', '?'))
        if r.status_code in [200, 302]:
            print("SUCCESS")
        else:
            print("FAIL")
    else:
        print("No CSRF token")
else:
    print("GET failed")
PYEOF
'''
    stdin, stdout, stderr = ssh.exec_command(test)
    time.sleep(10)
    result = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print("Result:", result)
    if error:
        print("Error:", error[:300])
finally:
    ssh.close()
