import paramiko
import time

print("="*70)
print("测试登录页面内容")
print("="*70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 获取登录页面内容
    print("\n获取登录页面内容...")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8000/login/ 2>/dev/null | head -100')
    page_content = stdout.read().decode('utf-8')
    
    # 检查是否包含错误信息
    if 'OperationalError' in page_content:
        print("[X] 页面包含错误信息")
        print(page_content[:1000])
    elif 'login' in page_content.lower() or '用户名' in page_content or 'password' in page_content.lower():
        print("[OK] 登录页面正常显示")
        # 检查是否有 CSRF token
        if 'csrfmiddlewaretoken' in page_content:
            print("[OK] CSRF token 存在")
        else:
            print("[警告] CSRF token 未找到")
    else:
        print("[?] 页面内容异常")
        print(page_content[:500])
    
    # 测试 POST 登录
    print("\n测试 POST 登录请求...")
    test_post = '''curl -s -D - -X POST http://127.0.0.1:8000/login/ \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=admin&password=admin123456" \\
  -o /dev/null -w "HTTP Status: %{http_code}\\n" 2>/dev/null'''
    
    stdin, stdout, stderr = ssh.exec_command(test_post)
    time.sleep(3)
    post_result = stdout.read().decode('utf-8')
    print(post_result)
    
    print("\n" + "="*70)
    print("测试完成")
    print("="*70)
    
    print("\n如果上面显示页面正常，请尝试:")
    print("1. 按 Ctrl+Shift+Delete 清除浏览器缓存")
    print("2. 或使用 Ctrl+Shift+N 打开无痕模式")
    print("3. 访问 http://www.xietongai.com.cn/login/")
    
finally:
    ssh.close()
