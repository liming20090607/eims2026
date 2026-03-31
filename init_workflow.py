"""
初始化审批流程系统 - 创建角色和示例人员
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from eims_app.models.model_workflow import Role, ProjectRole
from eims_app.models.model_project import Project

def create_roles():
    """创建系统角色"""
    print("=" * 60)
    print("开始创建系统角色...")
    print("=" * 60)
    
    roles_data = [
        ('super_admin', '超级管理员', '拥有系统所有权限'),
        ('system_admin', '系统管理员', '拥有系统管理权限'),
        ('project_director', '项目总监', '负责项目整体管理和最终审核'),
        ('director_rep', '总监代表', '协助总监工作，可初审'),
        ('supervisor', '监理员', '现场监理，发起填报'),
        ('data_clerk', '资料员', '负责资料管理，发起填报'),
        ('initiator', '发起人', '普通发起人员'),
    ]
    
    for name_key, name_display, desc in roles_data:
        role, created = Role.objects.get_or_create(
            name=name_key,
            defaults={
                'description': desc,
                'permissions': 'view,edit,submit'
            }
        )
        if created:
            print(f"✓ 创建角色：{name_display}")
        else:
            print(f"- 角色已存在：{name_display}")
    
    print()


def create_sample_users():
    """创建示例用户"""
    print("=" * 60)
    print("开始创建示例用户...")
    print("=" * 60)
    
    users_data = [
        # 管理员
        ('admin', 'admin123', '系统管理员', 'male'),
        ('zhangsan', 'password123', '张三', 'male'),
        ('lisi', 'password123', '李四', 'female'),
        ('wangwu', 'password123', '王五', 'male'),
        ('zhaoliu', 'password123', '赵六', 'female'),
        ('sunqi', 'password123', '孙七', 'male'),
        ('zhouba', 'password123', '周八', 'male'),
        ('wujiu', 'password123', '吴九', 'female'),
        ('zhengshi', 'password123', '郑十', 'male'),
    ]
    
    for username, password, real_name, gender in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': real_name,
                'email': f'{username}@example.com',
                'is_active': True
            }
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"✓ 创建用户：{username} ({real_name})")
        else:
            print(f"- 用户已存在：{username} ({real_name})")
    
    print()


def assign_project_roles():
    """为项目分配人员角色"""
    print("=" * 60)
    print("开始为项目分配人员角色...")
    print("=" * 60)
    
    # 获取所有项目
    projects = Project.objects.all()
    
    if not projects.exists():
        print("⚠️  没有找到项目，请先创建项目")
        return
    
    # 获取角色
    try:
        director_role = Role.objects.get(name='project_director')
        rep_role = Role.objects.get(name='director_rep')
        supervisor_role = Role.objects.get(name='supervisor')
        data_clerk_role = Role.objects.get(name='data_clerk')
    except Role.DoesNotExist as e:
        print(f"⚠️  角色不存在：{e}")
        return
    
    # 获取用户
    users = {
        'zhangsan': User.objects.filter(username='zhangsan').first(),
        'lisi': User.objects.filter(username='lisi').first(),
        'wangwu': User.objects.filter(username='wangwu').first(),
        'zhaoliu': User.objects.filter(username='zhaoliu').first(),
        'sunqi': User.objects.filter(username='sunqi').first(),
        'zhouba': User.objects.filter(username='zhouba').first(),
        'wujiu': User.objects.filter(username='wujiu').first(),
        'zhengshi': User.objects.filter(username='zhengshi').first(),
    }
    
    # 为每个项目分配角色
    for i, project in enumerate(projects):
        print(f"\n项目：{project.project_name}")
        
        # 项目总监（张三）
        if users['zhangsan']:
            ProjectRole.objects.get_or_create(
                user=users['zhangsan'],
                project=project,
                role=director_role,
                defaults={'is_active': True}
            )
            print(f"  ✓ 项目总监：张三")
        
        # 总监代表（李四）
        if users['lisi']:
            ProjectRole.objects.get_or_create(
                user=users['lisi'],
                project=project,
                role=rep_role,
                defaults={'is_active': True}
            )
            print(f"  ✓ 总监代表：李四")
        
        # 监理员（王五、赵六）
        for username in ['wangwu', 'zhaoliu']:
            if users[username]:
                ProjectRole.objects.get_or_create(
                    user=users[username],
                    project=project,
                    role=supervisor_role,
                    defaults={'is_active': True}
                )
                print(f"  ✓ 监理员：{users[username].first_name}")
        
        # 资料员（孙七）
        if users['sunqi']:
            ProjectRole.objects.get_or_create(
                user=users['sunqi'],
                project=project,
                role=data_clerk_role,
                defaults={'is_active': True}
            )
            print(f"  ✓ 资料员：孙七")
    
    print("\n✓ 项目角色分配完成！")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("EIMS 审批流程系统初始化")
    print("=" * 60 + "\n")
    
    # 1. 创建角色
    create_roles()
    
    # 2. 创建示例用户
    create_sample_users()
    
    # 3. 分配项目角色
    assign_project_roles()
    
    print("\n" + "=" * 60)
    print("初始化完成！")
    print("=" * 60)
    print("\n示例用户账号：")
    print("  管理员：admin / admin123")
    print("  张三（项目总监）：zhangsan / password123")
    print("  李四（总监代表）：lisi / password123")
    print("  王五（监理员）：wangwu / password123")
    print("  其他人员：用户名拼音 / password123")
    print("\n审批流程：")
    print("  发起人提交 → 项目总监审核 → 系统管理员审批")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
