from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models.model_user import UserProfile, UserTenantRelation

# 取消注册默认的 User Admin
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    增强版用户管理 - 支持在用户管理界面直接设置中文姓名
    
    功能:
    1. 显示用户的中文姓名（来自 UserProfile）
    2. 可快速跳转到 UserProfile 编辑页面
    3. 保留原有所有用户管理功能
    """
    
    # 扩展原有字段列表
    list_display = BaseUserAdmin.list_display + ('get_real_name', 'get_tenant')
    
    # 添加搜索字段
    search_fields = BaseUserAdmin.search_fields + ('profile__real_name', 'profile__tenant__name')
    
    def get_real_name(self, obj):
        """获取用户的中文姓名"""
        try:
            return obj.profile.real_name
        except UserProfile.DoesNotExist:
            return '-'
    
    get_real_name.short_description = '姓名'
    get_real_name.admin_order_field = 'profile__real_name'  # 添加排序支持
    
    def get_tenant(self, obj):
        """获取用户的所属公司（显示所有公司，主公司加粗）"""
        try:
            relations = UserTenantRelation.objects.filter(user=obj)
            if not relations.exists():
                # 如果没有关联表记录，尝试使用旧字段的 tenant
                if obj.profile.tenant:
                    return obj.profile.tenant.name
                return '-'
            
            # 显示所有公司
            companies = []
            for rel in relations:
                if rel.is_primary:
                    companies.append(f"<strong>{rel.tenant.name}</strong>（主）")
                else:
                    companies.append(rel.tenant.name)
            return ' | '.join(companies)
        except UserProfile.DoesNotExist:
            return '-'
    
    get_tenant.short_description = '所属公司'
    get_tenant.admin_order_field = 'profile__tenant__name'  # 添加排序支持
    get_tenant.allow_tags = True  # 允许HTML标签


# 优化 UserProfile 的 Admin 配置
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    用户资料管理 - 可在后台设置用户的中文姓名
    
    使用方法:
    1. 进入 Django admin 后台 (http://localhost:8000/admin/)
    2. 点击"用户资料"或"USER PROFILES"
    3. 选择要编辑的用户
    4. 在"姓名"字段输入中文姓名（如：张三）
    5. 保存后，该用户即可使用中文姓名登录
    
    登录方式:
    - 用户名：zhangsan (英文用户名)
    - 姓名：张三 (中文姓名) ✨
    - 邮箱：zhangsan@example.com
    """
    
    list_display = ('user', 'real_name', 'tenant', 'gender', 'phone', 'wechat')
    search_fields = ('user__username', 'real_name', 'phone', 'tenant__name')
    list_filter = ('gender', 'tenant')
    
    # 定义表单字段及其顺序
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'tenant', 'real_name', 'gender', 'birthday'),
            'description': '填写用户的基本信息，包括所属公司和中文姓名'
        }),
        ('联系方式', {
            'fields': ('phone', 'wechat'),
            'description': '填写用户的联系方式信息'
        }),
    )
    
    # 添加用户时显示简化版表单
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user', 'tenant', 'real_name', 'phone'),
        }),
    )
    
    # 批量操作
    actions = ['export_selected_profiles']
    
    def export_selected_profiles(self, request, queryset):
        """导出选中的用户资料"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="user_profiles.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['用户名', '所属公司', '姓名', '性别', '生日', '手机号', '微信号'])
        
        for profile in queryset:
            writer.writerow([
                profile.user.username,
                profile.tenant.name if profile.tenant else '-',
                profile.real_name or '-',
                profile.get_gender_display() if profile.gender else '-',
                profile.birthday or '-',
                profile.phone or '-',
                profile.wechat or '-'
            ])
        
        self.message_user(request, f'已导出 {queryset.count()} 条用户资料')
        return response
    
    export_selected_profiles.short_description = '导出选中的用户资料'


@admin.register(UserTenantRelation)
class UserTenantRelationAdmin(admin.ModelAdmin):
    """
    用户-公司关联管理 - 支持配置用户在多家公司任职
    
    功能:
    1. 一个用户可以在多家公司任职
    2. 每家公司可以设置是否为主公司
    3. 可以添加备注（如：全职/兼职/顾问）
    """
    
    list_display = ('user', 'get_real_name', 'tenant', 'is_primary', 'remark', 'create_time')
    list_filter = ('is_primary', 'tenant')
    search_fields = ('user__username', 'user__profile__real_name', 'tenant__name')
    list_select_related = ('user', 'tenant', 'user__profile')
    
    fieldsets = (
        ('关联信息', {
            'fields': ('user', 'tenant', 'is_primary', 'remark'),
            'description': '设置用户与公司的关联关系'
        }),
    )
    
    def get_real_name(self, obj):
        """获取用户的真实姓名"""
        try:
            return obj.user.profile.real_name or '-'
        except:
            return '-'
    
    get_real_name.short_description = '姓名'
    
    def get_queryset(self, request):
        """优化查询性能，预加载关联数据以支持排序"""
        qs = super().get_queryset(request)
        return qs.select_related('profile', 'profile__tenant')
