import os
import shutil
import sys

BACKUP_DIR = r'e:\EIMS2026\backup'
DB_FILE = r'e:\EIMS2026\db.sqlite3'

def list_backups():
    if not os.path.exists(BACKUP_DIR):
        print('[ERROR] 备份目录不存在')
        return []

    backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith('eims_backup_') and f.endswith('.sqlite3')]
    backups.sort(reverse=True)
    return backups

def restore_backup(backup_filename):
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    if not os.path.exists(backup_path):
        print(f'[ERROR] 备份文件不存在: {backup_filename}')
        return False

    confirm = input(f'警告: 此操作将用备份文件替换当前数据库! 确认恢复? (Y/N): ')
    if confirm.lower() != 'y':
        print('已取消恢复')
        return False

    try:
        shutil.copy2(backup_path, DB_FILE)
        print(f'[SUCCESS] 数据库恢复成功')
        print(f'已恢复到: {backup_filename}')
        return True
    except Exception as e:
        print(f'[ERROR] 数据库恢复失败: {e}')
        return False

if __name__ == '__main__':
    print('=' * 50)
    print('EIMS数据库恢复工具')
    print('=' * 50)
    print()

    backups = list_backups()
    if not backups:
        print('没有找到备份文件')
        sys.exit(1)

    print('可用的备份文件:')
    print()
    for i, backup in enumerate(backups[:20], 1):
        print(f'  {i}. {backup}')
    print()

    if len(backups) > 20:
        print(f'  ... 共 {len(backups)} 个备份文件')

    print()
    choice = input('请输入要恢复的备份编号(直接回车取消): ')

    if not choice:
        print('已取消')
        sys.exit(0)

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(backups):
            restore_backup(backups[idx])
        else:
            print('[ERROR] 无效的选择')
    except ValueError:
        print('[ERROR] 请输入有效的数字')
