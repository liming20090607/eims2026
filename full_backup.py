#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EIMS2026 完整备份脚本
备份内容：
1. 代码打包（排除不必要文件）
2. 所有MySQL数据库备份
3. 媒体文件备份
4. 配置文件备份
"""
import os
import shutil
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
BACKUP_DIR = PROJECT_ROOT / "backup"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_NAME = f"EIMS2026_backup_{TIMESTAMP}"
BACKUP_PATH = BACKUP_DIR / BACKUP_NAME

# MySQL数据库配置（从.env读取或使用默认值）
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': '3306',
    'user': 'root',
    'password': 'qinlin123',  # 请根据实际情况修改
}

# 需要备份的数据库列表
DATABASES = [
    'eims_root',      # Root管理数据库
    'eims_dingce',    # 广西鼎策数据库
    'eims_shengchang', # 广西晟昌数据库
    'eims_jiachengda', # 广西嘉诚达数据库
]

# 排除的文件/目录列表
EXCLUDE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '.git',
    '.vscode',
    '.idea',
    'node_modules',
    'venv',
    'env',
    '*.sqlite3',
    'db.sqlite3',
    '*.log',
    'logs/*',
    'staticfiles/*',
    'backup/*',
]

def create_backup_directory():
    """创建备份目录"""
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        print("[OK] 创建备份目录: {}".format(BACKUP_DIR))
    
    if BACKUP_PATH.exists():
        shutil.rmtree(BACKUP_PATH)
    BACKUP_PATH.mkdir(parents=True, exist_ok=True)
    print("[OK] 准备备份到: {}".format(BACKUP_PATH))

def backup_code():
    """备份项目代码"""
    print("\n" + "="*80)
    print("【1/4】备份项目代码")
    print("="*80)
    
    code_dir = BACKUP_PATH / "code"
    code_dir.mkdir(exist_ok=True)
    
    # 使用shutil.copytree排除不需要的文件
    for item in PROJECT_ROOT.iterdir():
        if item.name in ['backup', 'venv', 'env', '__pycache__']:
            continue
        if item.is_file() and item.suffix in ['.pyc', '.pyo', '.log', '.sqlite3']:
            continue
        if item.is_dir() and item.name in ['node_modules', '.git', '.vscode', '.idea', 'logs', 'staticfiles']:
            continue
        
        dest = code_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*EXCLUDE_PATTERNS))
        else:
            shutil.copy2(item, dest)
    
    print("[OK] 代码备份完成")
    return code_dir

def backup_databases():
    """备份所有MySQL数据库"""
    print("\n" + "="*80)
    print("【2/4】备份MySQL数据库")
    print("="*80)
    
    db_backup_dir = BACKUP_PATH / "databases"
    db_backup_dir.mkdir(exist_ok=True)
    
    # 检查mysqldump是否可用
    try:
        result = subprocess.run(['mysqldump', '--version'], capture_output=True, text=True)
        print("[OK] mysqldump版本: {}".format(result.stdout.strip()))
    except FileNotFoundError:
        print("[ERROR] 找不到mysqldump命令，请确保MySQL已安装并添加到PATH")
        return False
    
    for db_name in DATABASES:
        print(f"\n正在备份数据库: {db_name}...")
        dump_file = db_backup_dir / f"{db_name}_{TIMESTAMP}.sql"
        
        try:
            cmd = [
                'mysqldump',
                '-h', MYSQL_CONFIG['host'],
                '-P', MYSQL_CONFIG['port'],
                '-u', MYSQL_CONFIG['user'],
                f"-p{MYSQL_CONFIG['password']}",
                '--single-transaction',
                '--routines',
                '--triggers',
                '--events',
                db_name
            ]
            
            with open(dump_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                file_size = dump_file.stat().st_size / 1024 / 1024  # MB
                print("  [OK] {} 备份成功 ({:.2f} MB)".format(db_name, file_size))
            else:
                print("  [FAIL] {} 备份失败: {}".format(db_name, result.stderr))
        except Exception as e:
            print("  [ERROR] {} 备份异常: {}".format(db_name, str(e)))
    
    print("[OK] 数据库备份完成")
    return True

def backup_media():
    """备份媒体文件"""
    print("\n" + "="*80)
    print("【3/4】备份媒体文件")
    print("="*80)
    
    media_dir = PROJECT_ROOT / "media"
    media_backup_dir = BACKUP_PATH / "media"
    
    if media_dir.exists():
        shutil.copytree(media_dir, media_backup_dir, dirs_exist_ok=True)
        file_count = sum([len(files) for _, _, files in os.walk(media_backup_dir)])
        print("[OK] 媒体文件备份完成 ({} 个文件)".format(file_count))
    else:
        print("[WARN]  媒体目录不存在，跳过备份")
    
    return True

def backup_env():
    """备份配置文件"""
    print("\n" + "="*80)
    print("【4/4】备份配置文件")
    print("="*80)
    
    config_dir = BACKUP_PATH / "config"
    config_dir.mkdir(exist_ok=True)
    
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        shutil.copy2(env_file, config_dir / ".env")
        print("[OK] .env 文件已备份")
    
    settings_file = PROJECT_ROOT / "settings.py"
    if settings_file.exists():
        shutil.copy2(settings_file, config_dir / "settings.py")
        print("[OK] settings.py 已备份")
    
    requirements_file = PROJECT_ROOT / "requirements.txt"
    if requirements_file.exists():
        shutil.copy2(requirements_file, config_dir / "requirements.txt")
        print("[OK] requirements.txt 已备份")
    
    return True

def create_archive():
    """创建压缩归档文件"""
    print("\n" + "="*80)
    print("创建压缩归档文件")
    print("="*80)
    
    archive_file = BACKUP_DIR / f"{BACKUP_NAME}.tar.gz"
    
    with tarfile.open(archive_file, "w:gz") as tar:
        tar.add(BACKUP_PATH, arcname=BACKUP_NAME)
    
    archive_size = archive_file.stat().st_size / 1024 / 1024  # MB
    print("[OK] 归档文件创建成功: {}".format(archive_file.name))
    print("   大小: {:.2f} MB".format(archive_size))
    
    # 删除临时目录
    shutil.rmtree(BACKUP_PATH)
    print("[OK] 已清理临时文件")
    
    return archive_file

def print_summary(archive_file):
    """打印备份摘要"""
    print("\n" + "="*80)
    print("📊 备份完成摘要")
    print("="*80)
    print("[OK] 备份时间: {}".format(TIMESTAMP))
    print("[OK] 归档文件: {}".format(archive_file))
    print("[OK] 归档大小: {:.2f} MB".format(archive_file.stat().st_size / 1024 / 1024))
    print(f"\n📦 备份内容包括:")
    print(f"  • 项目代码（排除临时文件和依赖）")
    print(f"  • {len(DATABASES)} 个MySQL数据库")
    print(f"  • 媒体文件")
    print(f"  • 配置文件（.env, settings.py, requirements.txt）")
    print("\n" + "="*80)
    print("[OK] 所有备份操作完成！")
    print("="*80)

def main():
    """主函数"""
    print("="*80)
    print("EIMS2026 完整备份脚本")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    try:
        # 1. 创建备份目录
        create_backup_directory()
        
        # 2. 备份代码
        backup_code()
        
        # 3. 备份数据库
        backup_databases()
        
        # 4. 备份媒体文件
        backup_media()
        
        # 5. 备份配置文件
        backup_env()
        
        # 6. 创建归档
        archive_file = create_archive()
        
        # 7. 打印摘要
        print_summary(archive_file)
        
    except Exception as e:
        print("\n[ERROR] 备份失败: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
