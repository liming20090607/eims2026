"""
自动同步信号处理程序

功能：确保员工信息(Employee)与用户账号(User)之间的数据自动同步
- 员工创建时，自动创建用户账号
- 员工更新时，自动更新用户账号信息
- 用户创建时，自动查找并关联员工记录
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from ..models import Employee, UserProfile, UserTenantRelation

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=Employee)
def sync_employee_to_user(sender, instance, created, **kwargs):
    """
    员工信息保存时，自动同步到用户系统
    
    触发时机：
    - 新员工创建时（created=True）
    - 员工信息更新时（created=False）
    """
    if instance.is_deleted:
        # 已删除的员工不处理
        return
    
    try:
        # 1. 确定用户名（优先使用手机号，其次使用人员编号，最后使用姓名）
        username = None
        if instance.mobile:
            username = instance.mobile
        elif instance.personnel_code:
            username = instance.personnel_code
        
        if not username:
            logger.warning(f"员工 {instance.name} 缺少手机号和人员编号，无法同步到用户系统")
            return
        
        # 2. 查找或创建用户
        user = User.objects.filter(username=username).first()
        
        if created or not user:
            # 创建新用户
            if not user:
                default_password = 'sc123456#'
                user = User.objects.create_user(
                    username=username,
                    password=default_password,
                    first_name=instance.name,
                )
                logger.info(f"✅ 为员工 {instance.name} 创建用户账号: {username}")
                
                # 创建 UserProfile
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.real_name = instance.name
                profile.phone = instance.mobile or ''
                profile.tenant = instance.tenant
                profile.save()
                
                # 创建用户-公司关联
                if instance.tenant:
                    UserTenantRelation.objects.get_or_create(
                        user=user,
                        tenant=instance.tenant,
                        defaults={'is_primary': True}
                    )
                    logger.info(f"✅ 已关联用户 {username} 到公司: {instance.tenant.name}")
        
        else:
            # 更新现有用户信息
            # 更新基本用户信息
            if user.first_name != instance.name:
                user.first_name = instance.name
                user.save(update_fields=['first_name'])
            
            # 更新 UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile_updated = False
            
            if profile.real_name != instance.name:
                profile.real_name = instance.name
                profile_updated = True
            
            if instance.mobile and profile.phone != instance.mobile:
                profile.phone = instance.mobile
                profile_updated = True
            
            if instance.tenant and profile.tenant_id != instance.tenant_id:
                profile.tenant = instance.tenant
                profile_updated = True
            
            if profile_updated:
                profile.save()
                logger.info(f"✅ 已同步用户 {username} 的个人资料")
            
            # 更新用户-公司关联
            if instance.tenant:
                relation, created_relation = UserTenantRelation.objects.get_or_create(
                    user=user,
                    tenant=instance.tenant,
                    defaults={'is_primary': True}
                )
                if not created_relation and not relation.is_primary:
                    relation.is_primary = True
                    relation.save()
                    logger.info(f"✅ 已更新用户 {username} 的主公司为: {instance.tenant.name}")
        
        logger.debug(f"🔄 员工 {instance.name} ({instance.personnel_code}) 同步到用户 {username} 完成")
        
    except Exception as e:
        logger.error(f"❌ 同步员工 {instance.name} 到用户系统失败: {str(e)}")


@receiver(post_save, sender=User)
def sync_user_to_employee(sender, instance, created, **kwargs):
    """
    用户创建时，自动查找并关联员工记录
    
    触发时机：新用户创建时（created=True）
    """
    if not created:
        return
    
    try:
        username = instance.username
        
        # 1. 尝试通过手机号查找员工
        employee = None
        if username.isdigit() and len(username) >= 11:
            employee = Employee.objects.filter(mobile=username, is_deleted=False).first()
        
        # 2. 如果没找到，尝试通过人员编号查找
        if not employee:
            employee = Employee.objects.filter(personnel_code=username, is_deleted=False).first()
        
        # 3. 如果还是没找到，尝试通过姓名查找
        if not employee:
            employee = Employee.objects.filter(name=instance.first_name, is_deleted=False).first()
        
        if employee:
            logger.info(f"✅ 新用户 {username} 自动关联到员工: {employee.name}")
            
            # 确保 UserProfile 存在并关联
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            if not profile.real_name:
                profile.real_name = employee.name
                profile.save()
            
            # 确保用户-公司关联存在
            if employee.tenant:
                UserTenantRelation.objects.get_or_create(
                    user=instance,
                    tenant=employee.tenant,
                    defaults={'is_primary': True}
                )
        else:
            logger.debug(f"ℹ️ 新用户 {username} 未找到对应的员工记录")
        
    except Exception as e:
        logger.error(f"❌ 同步用户 {instance.username} 到员工系统失败: {str(e)}")
