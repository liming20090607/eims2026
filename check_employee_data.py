"""检查 Employee 和 Personnel 模型数据分布"""
import pymysql

# 连接各数据库
databases = {
    'eims_root': 'root_admin',
    'eims_dingce': '鼎策',
    'eims_shengchang': '晟昌', 
    'eims_jiachengda': '嘉诚达',
}

print("=" * 70)
print("Employee（员工信息）数据分布")
print("=" * 70)

total_employees = 0
for db_name, label in databases.items():
    try:
        conn = pymysql.connect(host='localhost', user='root', password='root123', database=db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM eims_app_employee")
        count = cursor.fetchone()[0]
        total_employees += count
        
        # 按 tenant_id 分组统计
        cursor.execute("SELECT tenant_id, COUNT(*) FROM eims_app_employee GROUP BY tenant_id")
        by_tenant = cursor.fetchall()
        
        print(f"\n{label} ({db_name}): {count} 条")
        if by_tenant:
            for t_id, t_count in by_tenant:
                print(f"  tenant_id={t_id}: {t_count} 条")
        
        conn.close()
    except Exception as e:
        print(f"\n{label} ({db_name}): 错误 - {e}")

print(f"\n总计: {total_employees} 条")

print("\n" + "=" * 70)
print("Personnel（人员去向/项目分配）数据分布")
print("=" * 70)

total_personnel = 0
for db_name, label in databases.items():
    try:
        conn = pymysql.connect(host='localhost', user='root', password='root123', database=db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM eims_app_personnel")
        count = cursor.fetchone()[0]
        total_personnel += count
        
        # 按 tenant_id 分组统计
        cursor.execute("SELECT tenant_id, COUNT(*) FROM eims_app_personnel GROUP BY tenant_id")
        by_tenant = cursor.fetchall()
        
        print(f"\n{label} ({db_name}): {count} 条")
        if by_tenant:
            for t_id, t_count in by_tenant:
                print(f"  tenant_id={t_id}: {t_count} 条")
        
        conn.close()
    except Exception as e:
        print(f"\n{label} ({db_name}): 错误 - {e}")

print(f"\n总计: {total_personnel} 条")

print("\n" + "=" * 70)
print("结论")
print("=" * 70)
print("""
Employee 模型：
- 数据按 tenant_id 分布在各公司数据库
- 路由器将 Employee 强制路由到 root_admin → 只能看到 root_admin 的数据
- 应该按请求上下文路由到正确的公司数据库

Personnel 模型：
- 数据按 tenant_id 分布在各公司数据库
- 已修复：不再强制路由到 root_admin

需要修复 Employee 模型的路由配置！
""")
