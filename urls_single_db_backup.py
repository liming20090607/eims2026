from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from eims_app.views.views_custom_login import custom_login

def profile_redirect(request):
    return HttpResponseRedirect('/')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect('/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', logout_view, name='logout'),
    path('login/', custom_login, name='user_login'),
    path('accounts/login/', custom_login, name='login'),
    path('accounts/profile/', profile_redirect, name='user_profile'),
    
    # ✅ 包含eims_app的URL并设置命名空间
    path('', include('eims_app.urls', namespace='eims_app')),
    
    # 如有其他应用，继续添加...
    # path('other_app/', include('other_app.urls', namespace='other_app')),
]

# 媒体文件配置（开发环境）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
