"""
部署相关视图
"""
import os
import subprocess
import json
import time
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache


def is_superuser(user):
    """检查是否为超级管理员"""
    return user.is_superuser


# 全局变量存储部署进度
deploy_progress = {}


@login_required
@user_passes_test(is_superuser)
@require_POST
def deploy_to_server(request):
    """
    部署到云服务器API
    仅限超级管理员使用
    返回实时进度信息
    """
    try:
        # 生成唯一的任务ID
        task_id = f"deploy_{request.user.id}_{int(time.time())}"
        
        # 初始化进度
        deploy_progress[task_id] = {
            'status': 'running',
            'progress': 0,
            'current_step': '',
            'logs': [],
            'error': None
        }
        
        def add_log(message):
            """添加日志并更新进度"""
            deploy_progress[task_id]['logs'].append(message)
            # 保存到缓存，5分钟过期
            cache.set(f'deploy_{task_id}', deploy_progress[task_id], 300)
        
        def update_progress(percent, step):
            """更新进度百分比和当前步骤"""
            deploy_progress[task_id]['progress'] = percent
            deploy_progress[task_id]['current_step'] = step
            cache.set(f'deploy_{task_id}', deploy_progress[task_id], 300)
        
        # 在后台线程中执行部署
        def run_deployment():
            try:
                add_log("📦 开始部署流程...")
                update_progress(5, "初始化")
                
                # 步骤1: 检查本地代码是否已提交
                add_log("\n[1/5] 检查本地代码状态...")
                update_progress(10, "检查代码状态")
                try:
                    result = subprocess.run(
                        ['git', 'status', '--porcelain'],
                        capture_output=True,
                        text=True,
                        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    )
                    
                    if result.stdout.strip():
                        add_log("⚠️  检测到未提交的更改")
                        add_log("请先提交代码再部署")
                        deploy_progress[task_id]['status'] = 'failed'
                        deploy_progress[task_id]['error'] = '本地有未提交的更改，请先 git add 和 git commit'
                        cache.set(f'deploy_{task_id}', deploy_progress[task_id], 300)
                        return
                    else:
                        add_log("✅ 本地代码干净")
                except Exception as e:
                    add_log(f"❌ Git检查失败: {str(e)}")
                    deploy_progress[task_id]['status'] = 'failed'
                    deploy_progress[task_id]['error'] = f'Git检查失败: {str(e)}'
                    cache.set(f'deploy_{task_id}', deploy_progress[task_id], 300)
                    return
                
                # 步骤2: 推送到Gitee仓库
                add_log("\n[2/5] 推送代码到Gitee仓库...")
                update_progress(25, "推送代码")
                try:
                    result = subprocess.run(
                        ['git', 'push', 'gitee', 'master'],
                        capture_output=True,
                        text=True,
                        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        add_log("✅ 代码推送成功")
                        if result.stdout:
                            for line in result.stdout.strip().split('\n'):
                                add_log(line)
                    else:
                        add_log(f"❌ 推送失败: {result.stderr}")
                        deploy_progress[task_id]['status'] = 'failed'
                        deploy_progress[task_id]['error'] = f'推送到Gitee失败: {result.stderr}'
                        cache.set(f'deploy_{task_id}', deploy_progress[task_id], 300)
                        return
                except subprocess.TimeoutExpired:
                    add_log("❌ 推送超时")
                    deploy_progress[task_id]['status'] = 'failed'
                    deploy_progress[task_id]['error'] = '推送到Gitee超时'
                    cache.set(f'deploy_{task_id}', deploy_progress[task_id], 300)
                    return
                except Exception as e:
                    add_log(f"❌ 推送失败: {str(e)}")
                    deploy_progress[task_id]['status'] = 'failed'
                    deploy_progress[task_id]['error'] = f'推送失败: {str(e)}'
                    cache.set(f'deploy_{task_id}', deploy_progress[task_id], 300)
                    return
                
                # 步骤3: SSH连接到服务器并执行部署
                add_log("\n[3/5] 连接服务器执行部署...")
                update_progress(40, "连接服务器")
                try:
                    import paramiko
                    
                    SERVER_IP = '39.106.41.239'
                    SERVER_USER = 'root'
                    PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
                    SERVER_PATH = '/var/www/eims'
                    
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
                    
                    add_log("✅ 服务器连接成功")
                    update_progress(50, "拉取代码")
                    
                    # 3.1 Git pull
                    add_log("\n[3.1/5] 拉取最新代码...")
                    stdin, stdout, stderr = ssh.exec_command(f"cd {SERVER_PATH} && git pull", timeout=30)
                    git_output = stdout.read().decode().strip()
                    git_error = stderr.read().decode().strip()
                    
                    if git_output:
                        for line in git_output.split('\n'):
                            add_log(line)
                    if git_error and 'Already up to date' not in git_error:
                        add_log(f"警告: {git_error}")
                    
                    # 3.2 安装依赖
                    add_log("\n[3.2/5] 安装依赖包...")
                    update_progress(60, "安装依赖")
                    stdin, stdout, stderr = ssh.exec_command(
                        f"cd {SERVER_PATH} && source venv/bin/activate && pip install -r requirements.txt 2>&1 | tail -10",
                        timeout=180
                    )
                    pip_output = stdout.read().decode().strip()
                    if pip_output:
                        for line in pip_output.split('\n'):
                            add_log(line)
                    
                    # 3.3 数据库迁移
                    add_log("\n[3.3/5] 应用数据库迁移...")
                    update_progress(75, "数据库迁移")
                    stdin, stdout, stderr = ssh.exec_command(
                        f"cd {SERVER_PATH} && source venv/bin/activate && python manage.py migrate 2>&1 | tail -10",
                        timeout=60
                    )
                    migrate_output = stdout.read().decode().strip()
                    if migrate_output:
                        for line in migrate_output.split('\n'):
                            add_log(line)
                    
                    # 3.4 重启Gunicorn
                    add_log("\n[3.4/5] 重启Gunicorn服务...")
                    update_progress(85, "重启服务")
                    ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null; sleep 2", timeout=5)
                    
                    start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
nohup gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --daemon \
    wsgi:application && \
echo "Gunicorn started" """
                    
                    stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=15)
                    gunicorn_output = stdout.read().decode().strip()
                    if gunicorn_output:
                        add_log(gunicorn_output)
                    
                    time.sleep(3)
                    
                    # 3.5 验证服务
                    add_log("\n[3.5/5] 验证服务状态...")
                    update_progress(95, "验证服务")
                    stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
                    http_code = stdout.read().decode().strip()
                    
                    if http_code == '200':
                        add_log("✅ 服务验证成功 (HTTP 200)")
                    else:
                        add_log(f"⚠️  HTTP状态码: {http_code}")
                    
                    ssh.close()
                    
                except ImportError:
                    add_log("❌ paramiko未安装，无法连接服务器")
                    deploy_progress[task_id]['status'] = 'failed'
                    deploy_progress[task_id]['error'] = '缺少paramiko库，请先安装: pip install paramiko'
                    cache.set(f'deploy_{task_id}', deploy_progress[task_id], 300)
                    return
                except Exception as e:
                    add_log(f"❌ 服务器部署失败: {str(e)}")
                    deploy_progress[task_id]['status'] = 'failed'
                    deploy_progress[task_id]['error'] = f'服务器部署失败: {str(e)}'
                    cache.set(f'deploy_{task_id}', deploy_progress[task_id], 300)
                    return
                
                # 步骤4: 完成
                add_log("\n[4/5] 部署完成！")
                add_log("\n🌐 访问地址: http://39.106.41.239/login/")
                update_progress(100, "部署完成")
                deploy_progress[task_id]['status'] = 'completed'
                cache.set(f'deploy_{task_id}', deploy_progress[task_id], 300)
                
            except Exception as e:
                add_log(f"\n❌ 部署过程出错: {str(e)}")
                deploy_progress[task_id]['status'] = 'failed'
                deploy_progress[task_id]['error'] = f'部署过程出错: {str(e)}'
                cache.set(f'deploy_{task_id}', deploy_progress[task_id], 300)
        
        # 启动后台线程
        thread = threading.Thread(target=run_deployment)
        thread.daemon = True
        thread.start()
        
        # 立即返回任务ID
        return JsonResponse({
            'success': True,
            'task_id': task_id,
            'message': '部署任务已启动，请等待完成'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'部署过程出错: {str(e)}'
        })


@login_required
@user_passes_test(is_superuser)
def get_deploy_progress(request, task_id):
    """
    获取部署进度（用于前端轮询）
    """
    progress = cache.get(f'deploy_{task_id}')
    
    if not progress:
        return JsonResponse({
            'success': False,
            'error': '任务不存在或已过期'
        })
    
    return JsonResponse({
        'success': True,
        'status': progress['status'],
        'progress': progress['progress'],
        'current_step': progress['current_step'],
        'logs': progress['logs'],
        'error': progress.get('error')
    })
