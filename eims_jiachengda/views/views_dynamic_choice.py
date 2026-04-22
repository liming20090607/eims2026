from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
import json
from eims_app.models.model_dynamic_choice import DynamicChoice


@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def add_dynamic_choice(request):
    """
    通用动态选项添加 API
    
    请求体 JSON:
    {
        "category": "project.project_status",  // 选项类别
        "code": "custom_status",              // 选项代码
        "name": "自定义状态"                   // 选项名称
    }
    
    返回 JSON:
    {
        "success": true/false,
        "message": "成功/失败原因",
        "data": {
            "code": "custom_status",
            "name": "自定义状态"
        }
    }
    """
    try:
        data = json.loads(request.body)
        category = data.get('category', '').strip()
        code = data.get('code', '').strip().lower()
        name = data.get('name', '').strip()
        
        # 验证必填字段
        if not category or not code or not name:
            return JsonResponse({
                'success': False,
                'message': '选项类别、代码和名称都不能为空'
            }, status=400)
        
        # 验证类别是否合法
        valid_categories = [choice[0] for choice in DynamicChoice.CATEGORY_CHOICES]
        if category not in valid_categories:
            return JsonResponse({
                'success': False,
                'message': f'无效的选项类别：{category}'
            }, status=400)
        
        # 验证代码格式（只能包含字母、数字和下划线）
        import re
        if not re.match(r'^[a-z][a-z0-9_]*$', code):
            return JsonResponse({
                'success': False,
                'message': '选项代码必须以字母开头，只能包含小写字母、数字和下划线'
            }, status=400)
        
        # 检查是否已存在
        if DynamicChoice.objects.filter(category=category, code=code).exists():
            return JsonResponse({
                'success': False,
                'message': f'选项代码 "{code}" 在该类别下已存在'
            }, status=400)
        
        # 创建新选项
        choice = DynamicChoice.add_choice(
            category=category,
            code=code,
            name=name,
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': '添加成功',
            'data': {
                'code': choice.code,
                'name': choice.name
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '无效的 JSON 数据'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'服务器错误：{str(e)}'
        }, status=500)


@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["GET"])
def get_dynamic_choices(request, category):
    """
    获取某个类别的所有动态选项
    
    URL 参数:
        category: 选项类别，如 "project.project_status"
    
    返回 JSON:
    [
        {"code": "not_started", "name": "未开工"},
        {"code": "custom_status", "name": "自定义状态"}
    ]
    """
    try:
        # 验证类别是否合法
        valid_categories = [choice[0] for choice in DynamicChoice.CATEGORY_CHOICES]
        if category not in valid_categories:
            return JsonResponse({
                'error': f'无效的选项类别：{category}'
            }, status=400)
        
        # 获取所有选项（包括默认的和动态添加的）
        choices = DynamicChoice.get_choices_for_category(category)
        
        # 转换为 JSON 格式
        result = [{'code': code, 'name': name} for code, name in choices]
        
        return JsonResponse(result, safe=False)
    
    except Exception as e:
        return JsonResponse({
            'error': f'服务器错误：{str(e)}'
        }, status=500)


@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["PUT", "DELETE"])
def manage_dynamic_choice(request, pk):
    """
    管理单个动态选项（更新或删除）
    
    PUT - 更新选项:
    {
        "code": "new_code",
        "name": "新名称",
        "order": 10,
        "is_active": true
    }
    
    DELETE - 删除选项（软删除，设置为 is_active=False）
    """
    choice = get_object_or_404(DynamicChoice, pk=pk)
    
    if request.method == 'DELETE':
        # 软删除
        choice.is_active = False
        choice.save()
        return JsonResponse({
            'success': True,
            'message': '已禁用该选项'
        })
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            # 更新字段
            if 'code' in data:
                new_code = data['code'].strip().lower()
                # 检查代码是否已被其他选项使用
                if DynamicChoice.objects.filter(category=choice.category, code=new_code).exclude(pk=choice.pk).exists():
                    return JsonResponse({
                        'success': False,
                        'message': f'选项代码 "{new_code}" 已被使用'
                    }, status=400)
                choice.code = new_code
            
            if 'name' in data:
                choice.name = data['name'].strip()
            
            if 'order' in data:
                choice.order = data['order']
            
            if 'is_active' in data:
                choice.is_active = data['is_active']
            
            choice.save()
            
            return JsonResponse({
                'success': True,
                'message': '更新成功',
                'data': {
                    'code': choice.code,
                    'name': choice.name,
                    'order': choice.order,
                    'is_active': choice.is_active
                }
            })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的 JSON 数据'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'服务器错误：{str(e)}'
            }, status=500)
