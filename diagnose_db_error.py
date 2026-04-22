import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("诊断服务器数据库配置问题...")
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查 settings.py 中的数据库配置
    print("\n[1] 检查 settings.py 数据库配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 15 "DATABASES" /www/wwwroot/EIMS2026/settings.py | head -25')
    db_config = stdout.read().decode('utf-8')
    print(db_config)
    
    # 2. 检查 .env 文件
    print("\n[2] 检查 .env 文件...")
    stdin, stdout, stderr = ssh.exec_command('cat /www/wwwroot/EIMS2026/.env 2>&1')
    env_content = stdout.read().decode('utf-8')
    if env_content.strip():
        print(env_content)
    else:
        print("[.env 文件不存在或为空]")
    
    # 3. 测试 MySQL 连接
    print("\n[3] 测试 MySQL 连接...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT 1 AS test;" 2>&1')
    mysql_output = stdout.read().decode('utf-8')
    mysql_error = stderr.read().decode('utf-8')
    
    if '1' in mysql_output:
        print("[✓] MySQL 连接成功（使用密码 EIMS2026_mysql）")
    else:
        print("[✗] MySQL 连接失败")
        print("错误信息:", mysql_error)
        
        # 尝试不用密码连接
        print("\n尝试不用密码连接...")
        stdin, stdout, stderr = ssh.exec_command('mysql -uroot -e "SELECT 1 AS test;" 2>&1')
        no_pass_output = stdout.read().decode('utf-8')
        no_pass_error = stderr.read().decode('utf-8')
        
        if '1' in no_pass_output:
            print("[✓] MySQL 可以无密码连接")
        else:
            print("[✗] 无密码连接也失败")
            print("错误:", no_pass_error)
    
    # 4. 查看当前运行的是哪个 Django 项目
    print("\n[4] 检查运行的项目路径...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep -E "python.*manage.py|gunicorn|uwsgi" | grep -v grep')
    process_info = stdout.read().decode('utf-8')
    if process_info.strip():
        print(process_info)
    else:
        print("[未找到运行的 Django 进程]")
    
    # 5. 检查是否有其他 EIMS 项目
    print("\n[5] 检查 /var/www/ 目录...")
    stdin, stdout, stderr = ssh.exec_command('ls -la /var/www/ 2>&1')
    var_www = stdout.read().decode('utf-8')
    print(var_www)
    
    # 错误中显示的路径是 /var/www/eims/，检查这个目录
    print("\n[6] 检查 /var/www/eims/ 目录...")
    stdin, stdout, stderr = ssh.exec_command('ls -la /var/www/eims/ 2>&1')
    eims_dir = stdout.read().decode('utf-8')
    if 'No such file' not in eims_dir:
        print(eims_dir)
        
        # 检查这个项目的 settings.py
        print("\n检查 /var/www/eims/ 的数据库配置...")
        stdin, stdout, stderr = ssh.exec_command('grep -A 15 "DATABASES" /var/www/eims/settings.py 2>&1 | head -25')
        other_db_config = stdout.read().decode('utf-8')
        print(other_db_config)
    else:
        print("[/var/www/eims/ 目录不存在]")
    
    # 6. 检查 Baota 站点配置
    print("\n[7] 检查 Baota 站点配置...")
    stdin, stdout, stderr = ssh.exec_command('cat /www/server/panel/vhost/nginx/*.conf 2>/dev/null | grep -A 10 "xietongai.com.cn" | head -20')
    nginx_config = stdout.read().decode('utf-8')
    if nginx_config.strip():
        print(nginx_config)
    else:
        print("[未找到 xietongai.com.cn 的 Nginx 配置]")
    
    # 7. 查看所有数据库
    print("\n[8] 查看所有 MySQL 数据库...")
    stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SHOW DATABASES;" 2>&1')
    databases = stdout.read().decode('utf-8')
    print(databases)
    
finally:
    ssh.close()
    print("\n诊断完成！")
