"""
同步云服务器用户账号数据到本地
从云服务器导出用户数据并导入到本地数据库
"""
import os
import sys
import json
import subprocess
import django

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from eims_app.models import UserProfile

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
EXPORT_FILE = '/tmp/users_export.json'
LOCAL_FILE = 'eims_app/fixtures/users_export.json'

def export_users_from_server():
    """从云服务器导出用户数据"""
    print('='*60)
    print('步骤 1: 从云服务器导出用户数据')
    print('='*60)
    
    # SSH 命令导出用户数据
    export_command = f"""ssh {SERVER_USER}@{SERVER_IP} << 'SSHEOF'
cd /var/www/eims
source venv/bin/activate
python manage.py dumpdata auth.User eims_app.UserProfile --indent 2 > {EXPORT_FILE}
echo "Export completed: {EXPORT_FILE}"
wc -l {EXPORT_FILE}
SSHEOF
"""
    
    print(f'正在从服务器 {SERVER_IP} 导出用户数据...')
    result = subprocess.run(export_command, shell=True, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode == 0:
        print('✅ 服务器导出成功')
        print(result.stdout)
    else:
        print('❌ 服务器导出失败')
        print('错误信息:', result.stderr)
        return False
    
    return True

def download_exported_data():
    """下载导出的用户数据到本地"""
    print('='*60)
    print('步骤 2: 下载用户数据到本地')
    print('='*60)
    
    # 创建本地目录
    os.makedirs('eims_app/fixtures', exist_ok=True)
    
    # SCP 命令下载文件
    scp_command = f'scp {SERVER_USER}@{SERVER_IP}:{EXPORT_FILE} {LOCAL_FILE}'
    
    print(f'正在下载文件到 {LOCAL_FILE}...')
    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode == 0:
        print('✅ 文件下载成功')
    else:
        print('❌ 文件下载失败')
        print('错误信息:', result.stderr)
        return False
    
    return True

def import_users_to_local():
    """导入用户数据到本地数据库"""
    print('='*60)
    print('步骤 3: 导入用户数据到本地数据库')
    print('='*60)
    
    # 检查文件是否存在
    if not os.path.exists(LOCAL_FILE):
        print(f'❌ 文件不存在: {LOCAL_FILE}')
        return False
    
    # 读取文件内容检查
    try:
        with open(LOCAL_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f'✅ 数据文件有效，共 {len(data)} 个对象')
    except Exception as e:
        print(f'❌ 数据文件无效: {e}')
        return False
    
    # 导入数据
    import_command = f'python manage.py loaddata {LOCAL_FILE}'
    print(f'正在导入数据...')
    result = subprocess.run(import_command, shell=True, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode == 0:
        print('✅ 数据导入成功')
        print(result.stdout)
    else:
        print('❌ 数据导入失败')
        print('错误信息:', result.stderr)
        return False
    
    return True

def verify_imported_data():
    """验证导入的数据"""
    print('='*60)
    print('步骤 4: 验证导入的用户数据')
    print('='*60)
    
    # 统计用户数量
    user_count = User.objects.count()
    profile_count = UserProfile.objects.count()
    
    print(f'\n导入结果:')
    print(f'  用户账号 (User): {user_count} 个')
    print(f'  用户资料 (UserProfile): {profile_count} 个')
    
    # 显示部分用户信息
    print('\n最新用户列表:')
    users = User.objects.order_by('-id')[:10]
    for user in users:
        try:
            profile = user.userprofile
            real_name = profile.real_name or '-'
        except UserProfile.DoesNotExist:
            real_name = '-'
        
        print(f'  • {user.username} | 姓名: {real_name} | 邮箱: {user.email or "-"} | 超级管理员: {user.is_superuser}')
    
    print('\n✅ 数据验证完成')
    return True

def main():
    """主函数"""
    print('\n')
    print('*' * 60)
    print('   同步云服务器用户账号数据到本地')
    print('*' * 60)
    print(f'  服务器: {SERVER_IP}')
    print(f'  用户: {SERVER_USER}')
    print(f'  本地数据库: db.sqlite3')
    print('*' * 60)
    print('\n')
    
    # 确认操作
    confirm = input('是否继续？(y/n): ')
    if confirm.lower() != 'y':
        print('操作已取消')
        return
    
    # 执行同步步骤
    steps = [
        ('导出服务器数据', export_users_from_server),
        ('下载数据到本地', download_exported_data),
        ('导入到本地数据库', import_users_to_local),
        ('验证导入数据', verify_imported_data),
    ]
    
    for step_name, step_func in steps:
        print(f'\n[{step_name}]')
        try:
            success = step_func()
            if not success:
                print(f'\n❌ 步骤失败: {step_name}')
                print('请检查错误信息并手动修复')
                return
        except Exception as e:
            print(f'\n❌ 步骤异常: {step_name}')
            print(f'错误信息: {e}')
            import traceback
            traceback.print_exc()
            return
    
    print('\n')
    print('*' * 60)
    print('   ✅ 用户数据同步完成！')
    print('*' * 60)
    print('\n现在您可以在本地系统查看所有用户账号了')
    print('访问: http://127.0.0.1:8000/admin/')
    print('访问: http://127.0.0.1:8000/user-management/')
    print('\n')

if __name__ == '__main__':
    main()
