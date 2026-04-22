import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')

print('Upgrading pip...')
ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/pip install --upgrade pip', timeout=120)
time.sleep(20)

stdin, stdout, stderr = ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/pip --version')
print('Pip version:', stdout.read().decode().strip())

print('\nInstalling dependencies (this will take 5-10 minutes)...')
req_path = '/www/wwwroot/EIMS2026/requirements.txt'
ssh.exec_command(f'/www/wwwroot/EIMS2026/venv/bin/pip install -r {req_path}', timeout=600)
time.sleep(60)

stdin, stdout, stderr = ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/python -c "import django; print(django.get_version())"')
django_ver = stdout.read().decode().strip()
print('Django version:', django_ver)

if django_ver:
    print('\nSUCCESS! Dependencies installed.')
else:
    print('\nStill installing... waiting more...')
    time.sleep(60)
    stdin, stdout, stderr = ssh.exec_command('/www/wwwroot/EIMS2026/venv/bin/python -c "import django; print(django.get_version())"')
    print('Django version:', stdout.read().decode().strip())

ssh.close()
print('Done!')
