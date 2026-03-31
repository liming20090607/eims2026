from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models.model_user import UserProfile

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
    list_display = BaseUserAdmin.list_display + ('get_real_name',)
    
    # 添加搜索字段
    search_fields = BaseUserAdmin.search_fields + ('profile__real_name',)
    
    def get_real_name(self, obj):
        """获取用户的中文姓名"""
        try:
            return obj.profile.real_name
        except UserProfile.DoesNotExist:
            return '-'
    
    get_real_name.short_description = '姓名'


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
    
    list_display = ('user', 'real_name', 'gender', 'phone', 'wechat')
    search_fields = ('user__username', 'real_name', 'phone')
    list_filter = ('gender',)
    
    # 定义表单字段及其顺序
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'real_name', 'gender', 'birthday'),
            'description': '填写用户的基本信息，包括中文姓名'
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
            'fields': ('user', 'real_name', 'phone'),
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
        writer.writerow(['用户名', '姓名', '性别', '生日', '手机号', '微信号'])
        
        for profile in queryset:
            writer.writerow([
                profile.user.username,
                profile.real_name or '-',
                profile.get_gender_display() if profile.gender else '-',
                profile.birthday or '-',
                profile.phone or '-',
                profile.wechat or '-'
            ])
        
        self.message_user(request, f'已导出 {queryset.count()} 条用户资料')
        return response
    
    export_selected_profiles.short_description = '导出选中的用户资料'
