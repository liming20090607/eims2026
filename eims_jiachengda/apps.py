from django.apps import AppConfig

class EimsJiachengdaConfig(AppConfig):
    # 应用名称（必须与 INSTALLED_APPS 中的'eims_jiachengda'一致）
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eims_jiachengda'
    # 应用 verbose 名称（Admin 后台显示，可修改）
    verbose_name = 'EIMS 核心业务模块'
    
    def ready(self):
        """应用启动时自动加载信号处理程序"""
        import eims_jiachengda.signals  # 导入信号模块以注册所有信号处理程序
