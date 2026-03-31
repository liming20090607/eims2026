import os
import shutil
from datetime import datetime

BACKUP_DIR = r'e:\EIMS2026\backup'
DB_FILE = r'e:\EIMS2026\db.sqlite3'

if __name__ == '__main__':
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f'[INFO] 创建备份目录: {BACKUP_DIR}')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'eims_backup_{timestamp}.sqlite3'
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        shutil.copy2(DB_FILE, backup_path)
        print(f'[SUCCESS] 数据库备份成功: {backup_filename}')
    except Exception as e:
        print(f'[ERROR] 数据库备份失败: {e}')
