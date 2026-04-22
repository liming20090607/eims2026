from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from eims_app.views.views_custom_login import custom_login
from eims_app.views.views_router import route_selector

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
    
    # ===== 多系统路由 =====
    # 智能路由入口（推荐）
    path('', route_selector, name='route_selector'),
    
    # 各公司系统 - 使用独立命名空间
    path('dingce/', include(('eims_app.urls', 'eims_app'), namespace='dingce')),
    path('shengchang/', include(('eims_app.urls', 'eims_app'), namespace='shengchang')),
    path('jiachengda/', include(('eims_app.urls', 'eims_app'), namespace='jiachengda')),
    
    # Root超级管理员后台
    path('root/', include(('eims_app.urls', 'eims_app'), namespace='root')),
]

# 媒体文件配置（开发环境）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
