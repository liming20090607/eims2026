import os
import subprocess
import sys

TASK_NAME = 'EIMS_Auto_Backup'
BACKUP_SCRIPT = r'e:\EIMS2026\backup_auto.py'
INTERVAL_MINUTES = 10

def create_scheduled_task():
    try:
        result = subprocess.run(
            ['schtasks', '/query', '/tn', TASK_NAME],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f'检测到已存在定时任务: {TASK_NAME}')
            choice = input('是否重新创建? (Y/N): ')
            if choice.lower() != 'y':
                print('已取消')
                return

            subprocess.run(['schtasks', '/delete', '/tn', TASK_NAME, '/f'], capture_output=True)
            print('已删除旧任务')

        result = subprocess.run([
            'schtasks', '/create',
            '/tn', TASK_NAME,
            '/tr', f'python "{BACKUP_SCRIPT}"',
            '/sc', 'minute',
            '/mo', str(INTERVAL_MINUTES),
            '/f'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print()
            print('=' * 50)
            print('[SUCCESS] 自动备份任务创建成功!')
            print('=' * 50)
            print(f'任务名称: {TASK_NAME}')
            print(f'执行间隔: 每 {INTERVAL_MINUTES} 分钟')
            print(f'备份脚本: {BACKUP_SCRIPT}')
            print(f'备份目录: e:\\EIMS2026\\backup\\')
            print()
            print('现在运行一次备份测试...')
            os.system(f'python "{BACKUP_SCRIPT}"')
        else:
            print(f'[ERROR] 创建定时任务失败')
            print(result.stderr)
            print('请以管理员身份运行此脚本')

    except Exception as e:
        print(f'[ERROR] {e}')

if __name__ == '__main__':
    print('=' * 50)
    print('EIMS自动备份设置')
    print('=' * 50)
    print()
    create_scheduled_task()
    print()
    print('=' * 50)
    print('备份设置完成!')
    print()
    print('可用操作:')
    print('  1. 立即备份: python backup_auto.py')
    print('  2. 恢复数据: python restore_db.py')
    print('  3. 停止自动: schtasks /delete /tn "EIMS_Auto_Backup" /f')
    print('=' * 50)
    input()
