#!/usr/bin/env python
"""
快速检查服务器端登录页面状态
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
print("🔍 服务器端状态检查")
print("="*70 + "\n")

# 1. 检查服务
print("[1] 服务状态:")
checks = {
    'Gunicorn': 'pgrep -c gunicorn || echo 0',
    'Nginx': 'pgrep -c nginx || echo 0',
    'MySQL': 'systemctl is-active mysqld',
}
for name, cmd in checks.items():
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()
    icon = "✅" if result not in ['0', 'inactive', ''] else "❌"
    print(f"  {icon} {name}: {result}")

# 2. 测试GET请求（获取页面）
print("\n[2] GET请求测试（获取登录页面）:")
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "HTTP %{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
get_result = stdout.read().decode().strip()
print(f"  {get_result}")

# 3. 测试CSRF Cookie生成
print("\n[3] CSRF Cookie测试:")
stdin, stdout, stderr = ssh.exec_command('curl -s -c /tmp/test_cookie.txt -D /tmp/test_headers.txt http://127.0.0.1:80/login/ >/dev/null && grep -i "set-cookie" /tmp/test_headers.txt | grep -i csrf || echo "NO_CSRF_COOKIE"')
csrf_cookie = stdout.read().decode().strip()

if 'csrftoken' in csrf_cookie.lower() or 'csrf' in csrf_cookie.lower():
    print("  ✅ CSRF Cookie正常生成")
    print(f"  {csrf_cookie[:80]}")
else:
    print("  ⚠️ CSRF Cookie可能有问题")
    print(f"  结果: {csrf_cookie}")

# 4. 测试POST请求（模拟登录提交）
print("\n[4] POST请求测试（模拟表单提交）:")
post_test = """
# 先获取CSRF token
curl -s -c /tmp/post_test.txt http://127.0.0.1:80/login/ -o /tmp/login_page.html
TOKEN=$(grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' /tmp/login_page.html | sed 's/.*value="//;s/"//')

if [ -z "$TOKEN" ]; then
    echo "❌ 未找到CSRF token"
else
    echo "✅ 找到CSRF token: ${TOKEN:0:20}..."
    # 尝试提交
    RESULT=$(curl -s -o /dev/null -w "HTTP %{http_code}" -b /tmp/post_test.txt -X POST -d "csrfmiddlewaretoken=$TOKEN&username=test&password=test" http://127.0.0.1:80/login/)
    echo "POST结果: $RESULT"
fi
"""
stdin, stdout, stderr = ssh.exec_command(post_test)
post_result = stdout.read().decode().strip()
for line in post_result.split('\n'):
    if line.strip():
        print(f"  {line}")

ssh.close()

print("\n" + "="*70)
print("📋 诊断结果")
print("="*70)
print("\n如果您的浏览器显示'CSRF token from POST incorrect':")
print("\n这是因为浏览器缓存了旧的CSRF token。")
print("\n解决方法（选择其中一个）:")
print("  方法1: 按 Ctrl+Shift+Delete")
print("         → 选择'全部时间'")
print("         → 勾选'Cookie和其他网站数据'")
print("         → 清除后重新访问")
print("\n  方法2: 按 Ctrl+F5 强制刷新页面")
print("\n  方法3: 使用无痕模式 (Ctrl+Shift+N)")
print("         → 直接访问: http://www.xietongai.com.cn/login/")
print("\n  方法4: 清除特定网站Cookie:")
print("         → 地址栏点击🔒图标")
print("         → 选择'Cookie'")
print("         → 删除 xietongai.com.cn 的所有Cookie")
print("         → 刷新页面")
print("="*70 + "\n")
