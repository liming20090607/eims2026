"""
部署相关视图
"""
import os
import subprocess
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test


def is_superuser(user):
    """检查是否为超级管理员"""
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
@require_POST
def deploy_to_server(request):
    """
    部署到云服务器API
    仅限超级管理员使用
    """
    try:
        # 记录日志
        log_messages = []
        
        def add_log(message):
            log_messages.append(message)
        
        add_log("📦 开始部署流程...")
        
        # 步骤1: 检查本地代码是否已提交
        add_log("\n[1/4] 检查本地代码状态...")
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
                return JsonResponse({
                    'success': False,
                    'error': '本地有未提交的更改，请先 git add 和 git commit'
                })
            else:
                add_log("✅ 本地代码干净")
        except Exception as e:
            add_log(f"❌ Git检查失败: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Git检查失败: {str(e)}'
            })
        
        # 步骤2: 推送到Gitee仓库
        add_log("\n[2/4] 推送代码到Gitee仓库...")
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
                    add_log(result.stdout.strip())
            else:
                add_log(f"❌ 推送失败: {result.stderr}")
                return JsonResponse({
                    'success': False,
                    'error': f'推送到Gitee失败: {result.stderr}'
                })
        except subprocess.TimeoutExpired:
            add_log("❌ 推送超时")
            return JsonResponse({
                'success': False,
                'error': '推送到Gitee超时'
            })
        except Exception as e:
            add_log(f"❌ 推送失败: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'推送失败: {str(e)}'
            })
        
        # 步骤3: SSH连接到服务器并执行部署
        add_log("\n[3/4] 连接服务器执行部署...")
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
            
            # 3.1 Git pull
            add_log("\n[3.1] 拉取最新代码...")
            stdin, stdout, stderr = ssh.exec_command(f"cd {SERVER_PATH} && git pull", timeout=30)
            git_output = stdout.read().decode().strip()
            git_error = stderr.read().decode().strip()
            
            if git_output:
                add_log(git_output)
            if git_error and 'Already up to date' not in git_error:
                add_log(f"警告: {git_error}")
            
            # 3.2 安装依赖
            add_log("\n[3.2] 安装依赖包...")
            stdin, stdout, stderr = ssh.exec_command(
                f"cd {SERVER_PATH} && source venv/bin/activate && pip install -r requirements.txt 2>&1 | tail -5",
                timeout=180
            )
            pip_output = stdout.read().decode().strip()
            if pip_output:
                add_log(pip_output)
            
            # 3.3 数据库迁移
            add_log("\n[3.3] 应用数据库迁移...")
            stdin, stdout, stderr = ssh.exec_command(
                f"cd {SERVER_PATH} && source venv/bin/activate && python manage.py migrate 2>&1 | tail -5",
                timeout=60
            )
            migrate_output = stdout.read().decode().strip()
            if migrate_output:
                add_log(migrate_output)
            
            # 3.4 重启Gunicorn
            add_log("\n[3.4] 重启Gunicorn服务...")
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
            
            import time
            time.sleep(3)
            
            # 3.5 验证服务
            add_log("\n[3.5] 验证服务状态...")
            stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
            http_code = stdout.read().decode().strip()
            
            if http_code == '200':
                add_log("✅ 服务验证成功 (HTTP 200)")
            else:
                add_log(f"⚠️  HTTP状态码: {http_code}")
            
            ssh.close()
            
        except ImportError:
            add_log("❌ paramiko未安装，无法连接服务器")
            return JsonResponse({
                'success': False,
                'error': '缺少paramiko库，请先安装: pip install paramiko'
            })
        except Exception as e:
            add_log(f"❌ 服务器部署失败: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'服务器部署失败: {str(e)}'
            })
        
        # 步骤4: 完成
        add_log("\n[4/4] 部署完成！")
        add_log("\n🌐 访问地址: http://39.106.41.239/login/")
        
        return JsonResponse({
            'success': True,
            'message': '同步成功！代码已部署到云服务器',
            'log': '\n'.join(log_messages)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'部署过程出错: {str(e)}'
        })
