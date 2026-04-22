from django.shortcuts import render

# 首页核心视图函数 - 纯静态渲染，无任何数据库查询
def dashboard_index(request):
    """
    EIMS工程信息管理系统首页
    纯静态渲染，不查询任何模型，彻底避免字段不存在报错
    """
    return render(request, 'index.html')