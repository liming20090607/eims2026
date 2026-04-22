"""
测试部门角色列表视图是否可以正常访问
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_department import DepartmentRole

print("="*80)
print("测试部门角色查询")
print("="*80)

# 测试查询 - 不使用select_related('user')
print("\n1. 测试 DepartmentRole 查询（不含 user 的 select_related）:")
try:
    roles = DepartmentRole.objects.filter(is_deleted=False).select_related('department')[:3]
    print(f"   ✓ 查询成功，返回 {len(roles)} 条记录")
    for role in roles:
        print(f"   - {role.role_name}: {role.department.department_name}")
        # 单独访问 user 字段（会从 root_admin 数据库获取）
        print(f"     用户: {role.user.username}")
except Exception as e:
    print(f"   ✗ 查询失败: {e}")

# 测试模板渲染中会访问的字段
print("\n2. 测试模板中会访问的所有字段:")
try:
    role = DepartmentRole.objects.filter(is_deleted=False).first()
    if role:
        print(f"   ✓ 角色对象获取成功")
        print(f"   - 部门名称: {role.department.department_name}")
        print(f"   - 用户名: {role.user.username}")
        print(f"   - 角色类型: {role.get_role_type_display()}")
        print(f"   - 角色名称: {role.role_name}")
        if role.supervisor:
            print(f"   - 上级: {role.supervisor.username}")
        else:
            print(f"   - 上级: 无")
except Exception as e:
    print(f"   ✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("✅ 测试完成！")
print("="*80)
