import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("=" * 60)
print("验证root用户信息")
print("=" * 60)

cursor.execute("SELECT id, username, email, is_staff, is_superuser FROM auth_user WHERE username='root'")
user = cursor.fetchone()

if user:
    print("\n✅ 用户信息:")
    print(f"  ID: {user[0]}")
    print(f"  用户名: {user[1]}")
    print(f"  邮箱: {user[2]}")
    print(f"  管理员: {'是' if user[3] else '否'}")
    print(f"  超级管理员: {'是' if user[4] else '否'}")
    
    print("\n" + "=" * 60)
    print("租户信息")
    print("=" * 60)
    
    cursor.execute("SELECT id, name, code FROM eims_app_tenant WHERE code='jiachengda'")
    tenant = cursor.fetchone()
    if tenant:
        print(f"\n✅ 租户信息:")
        print(f"  ID: {tenant[0]}")
        print(f"  名称: {tenant[1]}")
        print(f"  代码: {tenant[2]}")
    
    print("\n" + "=" * 60)
    print("人员信息")
    print("=" * 60)
    
    cursor.execute("SELECT personnel_code, name, tenant_id FROM eims_app_personnel WHERE personnel_code='JDRY022'")
    personnel = cursor.fetchone()
    if personnel:
        print(f"\n✅ 人员信息:")
        print(f"  编号: {personnel[0]}")
        print(f"  姓名: {personnel[1]}")
        print(f"  租户ID: {personnel[2]}")
    
    print("\n" + "=" * 60)
    print("登录信息")
    print("=" * 60)
    print("\n  用户名: root")
    print("  密码: root2026!")
    print("  登录地址: http://127.0.0.1:8000/login/")
    print("\n" + "=" * 60)
else:
    print("\n❌ 未找到root用户")

conn.close()
