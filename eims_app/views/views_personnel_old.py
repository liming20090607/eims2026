from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from eims_app.models import Personnel
from eims_app.forms import PersonnelForm

# 人员列表
@login_required
def personnel_list(request):
    search_key = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    personnels = Personnel.objects.filter(is_deleted=False)
    if search_key:
        personnels = personnels.filter(
            Q(emp_name__icontains=search_key) | 
            Q(emp_id__icontains=search_key) | 
            Q(department__icontains=search_key) | 
            Q(position__icontains=search_key)
        )
    if status:
        personnels = personnels.filter(emp_status=status)
    
    # 分页
    page = request.GET.get('page', 1)
    from django.core.paginator import Paginator
    paginator = Paginator(personnels, 10)
    personnels = paginator.get_page(page)
    
    back_url = request.META.get('HTTP_REFERER', '/')
    context = {
        'personnels': personnels,
        'search_key': search_key,
        'status': status,
        'back_url': back_url,
        'active_menu': 'personnel'
    }
    return render(request, 'eims_app/personnel/list.html', context)

# 人员详情
@login_required
def personnel_detail(request, pk):
    personnel = get_object_or_404(PersonnelInfo, pk=pk, is_deleted=False)
    back_url = request.GET.get('back_url', '/personnel/list/')
    context = {
        'personnel': personnel,
        'back_url': back_url,
        'active_menu': 'personnel'
    }
    return render(request, 'eims_app/personnel/detail.html', context)

# 添加人员
@login_required
def personnel_add(request):
    if request.method == 'POST':
        form = PersonnelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '人员信息添加成功！')
            return redirect('eims_app:personnel_list')
        messages.error(request, '添加失败，请检查输入内容！')
    else:
        form = PersonnelForm()
    
    back_url = '/personnel/list/'
    context = {
        'form': form,
        'back_url': back_url,
        'active_menu': 'personnel',
        'title': '添加人员信息'
    }
    return render(request, 'eims_app/personnel/add.html', context)

# 编辑人员
@login_required
def personnel_edit(request, pk):
    personnel = get_object_or_404(PersonnelInfo, pk=pk, is_deleted=False)
    if request.method == 'POST':
        form = PersonnelForm(request.POST, instance=personnel)
        if form.is_valid():
            form.save()
            messages.success(request, '人员信息修改成功！')
            return redirect('eims_app:personnel_detail', pk=pk)
        messages.error(request, '修改失败，请检查输入内容！')
    else:
        form = PersonnelForm(instance=personnel)
    
    back_url = request.GET.get('back_url', f'/personnel/detail/{pk}/')
    context = {
        'form': form,
        'personnel': personnel,
        'back_url': back_url,
        'active_menu': 'personnel',
        'title': '编辑人员信息'
    }
    return render(request, 'eims_app/personnel/edit.html', context)

# 删除人员（软删除）
@login_required
def personnel_delete(request, pk):
    personnel = get_object_or_404(PersonnelInfo, pk=pk, is_deleted=False)
    if request.method == 'POST':
        personnel.is_deleted = True
        personnel.save()
        messages.success(request, '人员信息删除成功！')
        return redirect('eims_app:personnel_list')
    
    back_url = f'/personnel/detail/{pk}/'
    context = {
        'personnel': personnel,
        'back_url': back_url,
        'active_menu': 'personnel'
    }
    return render(request, 'eims_app/personnel/delete.html', context) 
