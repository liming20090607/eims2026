#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EIMS 系统备份和嘉诚达子系统创建脚本

功能：
1. 自动备份广西鼎策工程顾问有限责任公司子系统（数据库 + 代码）
2. 参照鼎策子系统创建广西嘉诚达工程造价咨询有限公司子系统
   - 复制所有文件结构
   - 复制所有功能和样式
   - 使用测试数据初始化
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# ==================== 配置区域 ====================
BASE_DIR = Path(__file__).resolve().parent
PROJECT_NAME = "EIMS2026"

# 公司配置
COMPANIES = {
    'dingce': {
        'name': '广西鼎策工程顾问有限责任公司',
        'db_name': 'eims_dingce',
        'app_dir': 'eims_app',  # 当前主应用作为鼎策模板
    },
    'jiachengda': {
        'name': '广西嘉诚达工程造价咨询有限公司',
        'db_name': 'eims_jiachengda',
        'app_dir': 'eims_jiachengda',
    }
}

# MySQL 配置
MYSQL_CONFIG = {
    'user': 'root',
    'password': 'root123',
    'host': 'localhost',
    'port': '3306'
}

# 备份目录
BACKUP_DIR = BASE_DIR / 'backup' / 'system_backup'
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_step(step_num, description):
    """打印步骤"""
    print(f"\n[步骤 {step_num}] {description}")
    print("-" * 80)


def run_command(cmd, description="", cwd=None):
    """执行命令并返回结果"""
    try:
        print(f"  执行: {cmd}")
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"  ✓ {description or '成功'}")
            return True, result.stdout
        else:
            print(f"  ✗ {description or '失败'}")
            print(f"    错误: {result.stderr[:200]}")
            return False, result.stderr
            
    except Exception as e:
        print(f"  ✗ 执行失败: {str(e)}")
        return False, str(e)


def backup_database():
    """备份鼎策数据库"""
    print_step(1, "备份广西鼎策工程顾问有限责任公司数据库")
    
    backup_file = BACKUP_DIR / f"eims_dingce_{TIMESTAMP}.sql"
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 构建 mysqldump 命令
    cmd = (
        f"mysqldump -u{MYSQL_CONFIG['user']} "
        f"-p{MYSQL_CONFIG['password']} "
        f"-h{MYSQL_CONFIG['host']} "
        f"-P{MYSQL_CONFIG['port']} "
        f"--single-transaction "
        f"--routines "
        f"--triggers "
        f"--default-character-set=utf8mb4 "
        f"{COMPANIES['dingce']['db_name']} > \"{backup_file}\""
    )
    
    success, output = run_command(cmd, f"数据库备份到 {backup_file.name}")
    
    if success and backup_file.exists():
        file_size = backup_file.stat().st_size
        print(f"  备份文件大小: {file_size / 1024:.2f} KB")
        return True, str(backup_file)
    else:
        print("  ⚠ 数据库备份失败，将继续执行其他步骤")
        return False, None


def backup_code():
    """备份代码文件"""
    print_step(2, "备份代码文件")
    
    code_backup_dir = BACKUP_DIR / f"code_backup_{TIMESTAMP}"
    code_backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 需要备份的关键文件和目录
    items_to_backup = [
        'eims_app',
        'settings.py',
        'urls.py',
        'manage.py',
        'static',
        'templates',
    ]
    
    for item in items_to_backup:
        src = BASE_DIR / item
        if src.exists():
            dst = code_backup_dir / item
            try:
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
                print(f"  ✓ 已备份: {item}")
            except Exception as e:
                print(f"  ✗ 备份 {item} 失败: {str(e)}")
        else:
            print(f"  ⚠ 跳过不存在的路径: {item}")
    
    print(f"  代码备份位置: {code_backup_dir}")
    return True


def create_jiachengda_database():
    """创建嘉诚达数据库"""
    print_step(3, "创建广西嘉诚达工程造价咨询有限公司数据库")
    
    db_name = COMPANIES['jiachengda']['db_name']
    
    # 检查数据库是否已存在
    check_cmd = f"mysql -u{MYSQL_CONFIG['user']} -p{MYSQL_CONFIG['password']} -e \"SHOW DATABASES LIKE '{db_name}';\""
    success, output = run_command(check_cmd, "检查数据库是否存在")
    
    if db_name in output:
        print(f"  ⚠ 数据库 {db_name} 已存在")
        response = input("  是否删除并重新创建？(yes/no): ")
        if response.lower() == 'yes':
            drop_cmd = f"mysql -u{MYSQL_CONFIG['user']} -p{MYSQL_CONFIG['password']} -e \"DROP DATABASE {db_name};\""
            run_command(drop_cmd, "删除现有数据库")
        else:
            print("  跳过数据库创建")
            return True
    
    # 创建新数据库
    create_cmd = (
        f"mysql -u{MYSQL_CONFIG['user']} "
        f"-p{MYSQL_CONFIG['password']} "
        f"-e \"CREATE DATABASE {db_name} "
        f"DEFAULT CHARACTER SET utf8mb4 "
        f"DEFAULT COLLATE utf8mb4_unicode_ci;\""
    )
    
    success, output = run_command(create_cmd, f"创建数据库 {db_name}")
    return success


def copy_eims_app_to_jiachengda():
    """复制 eims_app 到 eims_jiachengda"""
    print_step(4, "复制鼎策子系统代码到嘉诚达子系统")
    
    src_dir = BASE_DIR / 'eims_app'
    dst_dir = BASE_DIR / 'eims_jiachengda'
    
    if not src_dir.exists():
        print(f"  ✗ 源目录不存在: {src_dir}")
        return False
    
    # 如果目标目录已存在，先询问是否删除
    if dst_dir.exists():
        print(f"  ⚠ 目标目录已存在: {dst_dir}")
        response = input("  是否覆盖？(yes/no): ")
        if response.lower() == 'yes':
            shutil.rmtree(dst_dir)
        else:
            print("  跳过代码复制")
            return True
    
    # 复制整个目录
    try:
        shutil.copytree(src_dir, dst_dir)
        print(f"  ✓ 已复制 eims_app → eims_jiachengda")
        print(f"    源目录: {src_dir}")
        print(f"    目标目录: {dst_dir}")
        return True
    except Exception as e:
        print(f"  ✗ 复制失败: {str(e)}")
        return False


def update_jiachengda_config():
    """更新嘉诚达子系统的配置文件"""
    print_step(5, "更新嘉诚达子系统配置")
    
    jiachengda_dir = BASE_DIR / 'eims_jiachengda'
    
    # 1. 更新 apps.py
    apps_py = jiachengda_dir / 'apps.py'
    if apps_py.exists():
        try:
            content = apps_py.read_text(encoding='utf-8')
            content = content.replace('eims_app', 'eims_jiachengda')
            content = content.replace('EimsAppConfig', 'EimsJiachengdaConfig')
            if 'name =' in content:
                content = content.replace(
                    "name = 'eims_app'",
                    "name = 'eims_jiachengda'"
                )
            apps_py.write_text(content, encoding='utf-8')
            print("  ✓ 已更新 apps.py")
        except Exception as e:
            print(f"  ✗ 更新 apps.py 失败: {str(e)}")
    
    # 2. 更新 __init__.py
    init_py = jiachengda_dir / '__init__.py'
    if init_py.exists():
        try:
            content = init_py.read_text(encoding='utf-8')
            if 'default_app_config' in content:
                content = content.replace(
                    "default_app_config = 'eims_app.apps.EimsAppConfig'",
                    "default_app_config = 'eims_jiachengda.apps.EimsJiachengdaConfig'"
                )
            init_py.write_text(content, encoding='utf-8')
            print("  ✓ 已更新 __init__.py")
        except Exception as e:
            print(f"  ✗ 更新 __init__.py 失败: {str(e)}")
    
    # 3. 重命名 templates 目录中的子目录
    templates_dir = jiachengda_dir / 'templates' / 'eims_app'
    new_templates_dir = jiachengda_dir / 'templates' / 'eims_jiachengda'
    if templates_dir.exists():
        try:
            templates_dir.rename(new_templates_dir)
            print("  ✓ 已重命名 templates/eims_app → templates/eims_jiachengda")
        except Exception as e:
            print(f"  ✗ 重命名模板目录失败: {str(e)}")
    
    # 4. 更新模板文件中的命名空间引用
    if new_templates_dir.exists():
        updated_count = 0
        for html_file in new_templates_dir.rglob('*.html'):
            try:
                content = html_file.read_text(encoding='utf-8')
                original_content = content
                
                # 替换 URL 命名空间
                content = content.replace("{% url 'eims_app:", "{% url 'eims_jiachengda:")
                content = content.replace("{% static 'eims_app/", "{% static 'eims_jiachengda/")
                
                if content != original_content:
                    html_file.write_text(content, encoding='utf-8')
                    updated_count += 1
            except Exception as e:
                print(f"  ⚠ 更新模板文件 {html_file.name} 时出错: {str(e)[:50]}")
        
        print(f"  ✓ 已更新 {updated_count} 个模板文件的命名空间引用")
    
    return True


def update_main_settings():
    """更新主 settings.py 添加嘉诚达应用"""
    print_step(6, "更新主配置文件")
    
    settings_file = BASE_DIR / 'settings.py'
    
    try:
        content = settings_file.read_text(encoding='utf-8')
        
        # 检查是否已经添加了 eims_jiachengda
        if 'eims_jiachengda' not in content:
            # 在 INSTALLED_APPS 中添加 eims_jiachengda
            if "'eims_shengchang'," in content:
                content = content.replace(
                    "'eims_shengchang',",
                    "'eims_shengchang',\n    'eims_jiachengda',  # 广西嘉诚达工程造价咨询有限公司"
                )
                print("  ✓ 已在 INSTALLED_APPS 中添加 eims_jiachengda")
            
            settings_file.write_text(content, encoding='utf-8')
        else:
            print("  ⚠ eims_jiachengda 已存在于配置中")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 更新 settings.py 失败: {str(e)}")
        return False


def update_main_urls():
    """更新主 urls.py 添加嘉诚达路由"""
    print_step(7, "更新主 URL 配置")
    
    urls_file = BASE_DIR / 'urls.py'
    
    try:
        content = urls_file.read_text(encoding='utf-8')
        
        # 检查是否已经添加了嘉诚达路由
        if 'eims_jiachengda' not in content:
            # 在 shengchang 路由后添加 jiachengda 路由
            if "path('shengchang/', include('eims_shengchang.urls'" in content:
                content = content.replace(
                    "path('shengchang/', include('eims_shengchang.urls', namespace='eims_shengchang')),",
                    "path('shengchang/', include('eims_shengchang.urls', namespace='eims_shengchang')),\n    path('jiachengda/', include('eims_jiachengda.urls', namespace='eims_jiachengda')),  # 广西嘉诚达"
                )
                print("  ✓ 已添加嘉诚达 URL 路由")
            
            urls_file.write_text(content, encoding='utf-8')
        else:
            print("  ⚠ 嘉诚达路由已存在于配置中")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 更新 urls.py 失败: {str(e)}")
        return False


def run_migrations():
    """为嘉诚达数据库执行迁移"""
    print_step(8, "执行嘉诚达数据库迁移")
    
    cmd = "python manage.py migrate --database=jiachengda"
    success, output = run_command(cmd, "执行数据库迁移")
    
    if success:
        print("  ✓ 数据库迁移完成")
        return True
    else:
        print("  ⚠ 迁移过程中出现警告，请检查输出")
        return True  # 即使有警告也继续


def create_test_data():
    """为嘉诚达创建测试数据"""
    print_step(9, "创建嘉诚达测试数据")
    
    # 从鼎策导出数据
    print("  正在从鼎策导出测试数据...")
    export_cmd = "python manage.py dumpdata --database=dingce --indent 2 --natural-foreign --natural-primary -e contenttypes -e auth.Permission -e sessions.session > temp_dingce_data.json"
    success, output = run_command(export_cmd, "导出鼎策数据")
    
    if not success:
        print("  ⚠ 导出数据失败，将创建基础测试数据")
        return create_basic_test_data()
    
    # 导入到嘉诚达
    print("  正在导入数据到嘉诚达...")
    import_cmd = "python manage.py loaddata --database=jiachengda temp_dingce_data.json"
    success, output = run_command(import_cmd, "导入数据到嘉诚达")
    
    # 清理临时文件
    temp_file = BASE_DIR / 'temp_dingce_data.json'
    if temp_file.exists():
        temp_file.unlink()
    
    if success:
        print("  ✓ 测试数据创建完成")
        return True
    else:
        print("  ⚠ 数据导入失败，将创建基础测试数据")
        return create_basic_test_data()


def create_basic_test_data():
    """创建基础测试数据（备用方案）"""
    print("  创建基础测试数据...")
    
    test_script = BASE_DIR / 'create_jiachengda_test_data.py'
    
    script_content = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from eims_jiachengda.models import UserProfile, Department

# 创建测试用户
test_users = [
    {'username': 'admin_jcd', 'email': 'admin@jiachengda.com', 'password': 'admin123'},
    {'username': 'test_user_jcd', 'email': 'test@jiachengda.com', 'password': 'test123'},
]

for user_data in test_users:
    if not User.objects.filter(username=user_data['username']).exists():
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
        print(f"✓ 创建用户: {user_data['username']}")
    else:
        print(f"⚠ 用户已存在: {user_data['username']}")

print("\\n基础测试数据创建完成！")
print("用户名: admin_jcd / test_user_jcd")
print("密码: admin123 / test123")
'''
    
    test_script.write_text(script_content, encoding='utf-8')
    
    cmd = "python create_jiachengda_test_data.py"
    success, output = run_command(cmd, "创建基础测试数据")
    
    # 清理临时脚本
    if test_script.exists():
        test_script.unlink()
    
    return success


def print_summary(success_steps, total_steps):
    """打印总结"""
    print_header("操作完成总结")
    
    print(f"总步骤数: {total_steps}")
    print(f"成功步骤: {success_steps}")
    print(f"成功率: {success_steps/total_steps*100:.1f}%")
    
    print("\n📁 备份文件位置:")
    print(f"   数据库备份: {BACKUP_DIR / f'eims_dingce_{TIMESTAMP}.sql'}")
    print(f"   代码备份: {BACKUP_DIR / f'code_backup_{TIMESTAMP}'}")
    
    print("\n🏢 嘉诚达子系统信息:")
    print(f"   应用目录: eims_jiachengda/")
    print(f"   数据库: eims_jiachengda")
    print(f"   访问地址: http://localhost:8000/jiachengda/")
    
    print("\n✅ 下一步操作:")
    print("   1. 启动 Django 服务器: python manage.py runserver")
    print("   2. 访问嘉诚达系统: http://localhost:8000/jiachengda/")
    print("   3. 如需自定义，修改 eims_jiachengda/ 目录下的文件")
    print("")


def main():
    """主函数"""
    print_header("EIMS 系统备份和嘉诚达子系统创建")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目目录: {BASE_DIR}")
    print("")
    
    # 确认操作
    print("⚠️  即将执行以下操作:")
    print("   1. 备份鼎策子系统（数据库 + 代码）")
    print("   2. 创建嘉诚达子系统（复制鼎策所有内容）")
    print("")
    
    response = input("是否继续？(yes/no): ")
    if response.lower() != 'yes':
        print("操作已取消")
        return
    
    total_steps = 9
    success_steps = 0
    
    # 步骤 1: 备份数据库
    if backup_database()[0]:
        success_steps += 1
    
    # 步骤 2: 备份代码
    if backup_code():
        success_steps += 1
    
    # 步骤 3: 创建嘉诚达数据库
    if create_jiachengda_database():
        success_steps += 1
    
    # 步骤 4: 复制代码
    if copy_eims_app_to_jiachengda():
        success_steps += 1
    
    # 步骤 5: 更新嘉诚达配置
    if update_jiachengda_config():
        success_steps += 1
    
    # 步骤 6: 更新主 settings.py
    if update_main_settings():
        success_steps += 1
    
    # 步骤 7: 更新主 urls.py
    if update_main_urls():
        success_steps += 1
    
    # 步骤 8: 执行迁移
    if run_migrations():
        success_steps += 1
    
    # 步骤 9: 创建测试数据
    if create_test_data():
        success_steps += 1
    
    # 打印总结
    print_summary(success_steps, total_steps)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
