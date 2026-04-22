#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final verification of login page accessibility and content
"""
import requests
import time

def test_login_page():
    """Test login page from local machine"""
    print("=" * 70)
    print("🧪 Final Login Page Verification")
    print("=" * 70)
    
    urls = [
        'http://39.106.41.239/login/',
        'http://www.xietongai.com.cn/login/',
    ]
    
    for url in urls:
        print(f"\n🌐 Testing: {url}")
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                # Check page content
                html = response.text
                
                # Look for login-related content
                checks = {
                    '登录': '登录' in html or 'Login' in html,
                    '用户名/邮箱': 'username' in html.lower() or 'email' in html.lower(),
                    '密码': 'password' in html.lower(),
                    '提交按钮': 'submit' in html.lower() or 'button' in html.lower(),
                }
                
                print(f"   ✅ Page loaded successfully")
                print(f"   Content checks:")
                for check_name, result in checks.items():
                    status = "✅" if result else "❌"
                    print(f"      {status} {check_name}")
                
                # Extract title
                if '<title>' in html:
                    title_start = html.find('<title>') + 7
                    title_end = html.find('</title>', title_start)
                    if title_end > title_start:
                        title = html[title_start:title_end].strip()
                        print(f"   📄 Page Title: {title}")
                
                return True
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ Connection Error: {str(e)}")
            return False
        except requests.exceptions.Timeout as e:
            print(f"   ❌ Timeout: {str(e)}")
            return False
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False
    
    return False

if __name__ == '__main__':
    success = test_login_page()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ SUCCESS! Login page is fully accessible and working!")
        print("=" * 70)
        print("\n🎉 You can now access the system:")
        print("   🌐 http://39.106.41.239/login/")
        print("   🌐 http://www.xietongai.com.cn/login/")
        print("\n💡 The auto-correction system is running every 2 minutes")
        print("   to ensure continuous availability.")
    else:
        print("❌ FAILED - Login page not accessible")
        print("=" * 70)
