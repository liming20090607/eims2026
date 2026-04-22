#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EIMS2026 自动化部署脚本
自动完成：备份 -> 上传 -> 部署 -> 迁移 -> 重启 -> 验证
"""
import os
import sys
import time
import subprocess
import tarfile
from pathlib import Path
from datetime import datetime

try:
    import paramiko
except ImportError:
    print("[ERROR] 缺少 paramiko 库，请运行: pip install paramiko")
    sys.exit(1)

# 导入配置
from deploy_config import (
    SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD, SSH_KEY_FILE,
    REMOTE_PROJECT_PATH, REMOTE_BACKUP_PATH, REMOTE_VENV_PATH,
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, DATABASES,
    AUTO_BACKUP_SERVER, AUTO_MIGRATE, AUTO_COLLECTSTATIC, AUTO_RESTART,
    RESTART_COMMAND, LOCAL_BACKUP_FILE, AUTO_VERIFY, VERIFY_URLS
)

class EIMSDeployer:
    """EIMS2026 自动化部署器"""
    
    def __init__(self):
        self.ssh = None
        self.sftp = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def connect(self):
        """建立SSH连接"""
        print("\n" + "="*80)
        print("步骤 1/7: 连接服务器")
        print("="*80)
        print("正在连接到 {}@{}:{} ...".format(SSH_USER, SSH_HOST, SSH_PORT))
        
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 尝试密钥认证
            if SSH_KEY_FILE and os.path.exists(SSH_KEY_FILE):
                print("使用密钥文件认证: {}".format(SSH_KEY_FILE))
                private_key = paramiko.RSAKey.from_private_key_file(SSH_KEY_FILE)
                self.ssh.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, pkey=private_key)
            elif SSH_PASSWORD:
                print("使用密码认证")
                self.ssh.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD)
            else:
                print("[ERROR] 未提供SSH密码或密钥文件")
                return False
            
            self.sftp = self.ssh.open_sftp()
            print("[OK] SSH连接成功！")
            return True
            
        except Exception as e:
            print("[ERROR] SSH连接失败: {}".format(str(e)))
            return False
    
    def exec_command(self, command, timeout=300):
        """执行远程命令"""
        print("执行: {}".format(command))
        stdin, stdout, stderr = self.ssh.exec_command(command, timeout=timeout)
        
        # 读取输出
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        if output:
            print(output)
        if error:
            print("[WARN] {}".format(error))
        
        return stdout.channel.recv_exit_status(), output, error
    
    def backup_server(self):
        """备份服务器现有数据"""
        if not AUTO_BACKUP_SERVER:
            print("\n跳过服务器备份")
            return True
        
        print("\n" + "="*80)
        print("步骤 2/7: 备份服务器现有数据")
        print("="*80)
        
        # 1. 备份数据库
        print("\n[2.1] 备份MySQL数据库...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not os.path.exists(REMOTE_BACKUP_PATH):
            self.exec_command("mkdir -p {}".format(REMOTE_BACKUP_PATH))
        
        for db_name in DATABASES:
            # 检查数据库是否存在
            check_cmd = "mysql -h{} -P{} -u{} -p{} -e 'SHOW DATABASES;' 2>&1 | grep -w {}".format(
                MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, db_name
            )
            status, output, error = self.exec_command(check_cmd)
            
            if db_name in output:
                # 数据库存在，进行备份
                backup_file = "{}/{}_{}.sql".format(REMOTE_BACKUP_PATH, db_name, timestamp)
                cmd = "mysqldump -h{} -P{} -u{} -p{} --single-transaction {} > {}".format(
                    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, db_name, backup_file
                )
                status, output, error = self.exec_command(cmd)
                
                if status == 0:
                    print("  [OK] {} 备份成功".format(db_name))
                else:
                    print("  [WARN] {} 备份失败: {}".format(db_name, error))
            else:
                # 数据库不存在，跳过备份（首次部署正常情况）
                print("  [SKIP] {} 数据库不存在，跳过备份".format(db_name))
        
        # 2. 备份项目文件
        print("\n[2.2] 备份项目文件...")
        if os.path.exists(REMOTE_PROJECT_PATH):
            backup_archive = "{}/EIMS2026_backup_{}.tar.gz".format(REMOTE_BACKUP_PATH, timestamp)
            cmd = "tar -czf {} -C {} .".format(backup_archive, os.path.dirname(REMOTE_PROJECT_PATH))
            status, output, error = self.exec_command(cmd)
            
            if status == 0:
                print("  [OK] 项目文件备份成功: {}".format(backup_archive))
            else:
                print("  [WARN] 项目文件备份失败: {}".format(error))
        
        print("\n[OK] 服务器备份完成")
        return True
    
    def upload_backup(self):
        """上传本地备份文件到服务器"""
        print("\n" + "="*80)
        print("步骤 3/7: 上传备份文件")
        print("="*80)
        
        local_file = Path(LOCAL_BACKUP_FILE)
        if not local_file.exists():
            print("[ERROR] 本地备份文件不存在: {}".format(local_file))
            return False
        
        remote_file = "{}/EIMS2026_deploy_{}.tar.gz".format(REMOTE_BACKUP_PATH, self.timestamp)
        
        print("本地文件: {}".format(local_file))
        print("远程文件: {}".format(remote_file))
        print("文件大小: {:.2f} MB".format(local_file.stat().st_size / 1024 / 1024))
        print("上传中...")
        
        try:
            self.sftp.put(str(local_file), remote_file)
            print("[OK] 上传完成！")
            self.deploy_file = remote_file
            return True
        except Exception as e:
            print("[ERROR] 上传失败: {}".format(str(e)))
            return False
    
    def deploy_code(self):
        """在服务器上部署代码"""
        print("\n" + "="*80)
        print("步骤 4/7: 部署代码")
        print("="*80)
        
        # 1. 创建项目目录
        print("\n[4.1] 创建项目目录...")
        self.exec_command("mkdir -p {}".format(REMOTE_PROJECT_PATH))
        
        # 2. 解压备份文件（处理嵌套目录结构）
        print("\n[4.2] 解压代码包...")
        # 先解压到临时目录
        temp_extract = "/tmp/eims_deploy_{}".format(self.timestamp)
        self.exec_command("mkdir -p {}".format(temp_extract))
        cmd = "tar -xzf {} -C {}".format(self.deploy_file, temp_extract)
        status, output, error = self.exec_command(cmd, timeout=600)
        
        if status != 0:
            print("[ERROR] 解压失败: {}".format(error))
            return False
        
        # 查找code目录并移动到项目路径
        print("\n[4.2.1] 移动代码到项目目录...")
        # 查找实际的code目录
        find_cmd = "find {} -maxdepth 3 -name 'code' -type d".format(temp_extract)
        status, output, error = self.exec_command(find_cmd)
        code_dir = output.strip().split('\n')[0] if output.strip() else ""
        
        if code_dir:
            print("找到代码目录: {}".format(code_dir))
            # 移动所有文件到项目目录
            move_cmd = "cp -r {}/* {}/".format(code_dir, REMOTE_PROJECT_PATH)
            status, output, error = self.exec_command(move_cmd)
            if status != 0:
                print("[WARN] 移动文件警告: {}".format(error))
        else:
            # 如果没有找到code目录，直接移动整个提取的内容
            print("[WARN] 未找到code目录，移动整个内容...")
            move_cmd = "cp -r {}/* {}/".format(temp_extract, REMOTE_PROJECT_PATH)
            self.exec_command(move_cmd)
        
        # 清理临时目录
        self.exec_command("rm -rf {}".format(temp_extract))
        
        print("[OK] 代码解压完成")
        
        # 3. 设置权限
        print("\n[4.3] 设置文件权限...")
        self.exec_command("chmod -R 755 {}".format(REMOTE_PROJECT_PATH))
        self.exec_command("chmod -R 644 {}/eims_app/**/*.py".format(REMOTE_PROJECT_PATH))
        self.exec_command("chmod -R 644 {}/eims_jiachengda/**/*.py".format(REMOTE_PROJECT_PATH))
        
        # 4. 创建必要的目录
        print("\n[4.4] 创建必要的目录...")
        dirs_to_create = [
            "{}/logs".format(REMOTE_PROJECT_PATH),
            "{}/media".format(REMOTE_PROJECT_PATH),
            "{}/staticfiles".format(REMOTE_PROJECT_PATH),
        ]
        for dir_path in dirs_to_create:
            self.exec_command("mkdir -p {}".format(dir_path))
        
        print("[OK] 代码部署完成")
        return True
    
    def setup_virtualenv(self):
        """配置虚拟环境"""
        print("\n" + "="*80)
        print("步骤 5/7: 配置Python环境")
        print("="*80)
        
        # 1. 创建虚拟环境
        print("\n[5.1] 创建/更新虚拟环境...")
        cmd = "cd {} && python3 -m venv venv".format(REMOTE_PROJECT_PATH)
        status, output, error = self.exec_command(cmd, timeout=120)
        
        if status != 0:
            print("[WARN] 虚拟环境创建警告: {}".format(error))
        
        # 2. 安装依赖
        print("\n[5.2] 安装Python依赖...")
        cmd = "cd {} && {}/bin/pip install -r requirements.txt".format(
            REMOTE_PROJECT_PATH, REMOTE_VENV_PATH
        )
        status, output, error = self.exec_command(cmd, timeout=600)
        
        if status != 0:
            print("[ERROR] 依赖安装失败: {}".format(error))
            return False
        
        print("[OK] Python环境配置完成")
        return True
    
    def migrate_database(self):
        """执行数据库迁移"""
        if not AUTO_MIGRATE:
            print("\n跳过数据库迁移")
            return True
        
        print("\n" + "="*80)
        print("步骤 6/7: 数据库迁移")
        print("="*80)
        
        # 1. 执行makemigrations
        print("\n[6.1] 生成迁移文件...")
        cmd = "cd {} && {}/bin/python manage.py makemigrations".format(
            REMOTE_PROJECT_PATH, REMOTE_VENV_PATH
        )
        status, output, error = self.exec_command(cmd, timeout=120)
        
        # 2. 执行migrate
        print("\n[6.2] 执行数据库迁移...")
        cmd = "cd {} && {}/bin/python manage.py migrate".format(
            REMOTE_PROJECT_PATH, REMOTE_VENV_PATH
        )
        status, output, error = self.exec_command(cmd, timeout=300)
        
        if status != 0:
            print("[ERROR] 数据库迁移失败: {}".format(error))
            return False
        
        # 3. 收集静态文件
        if AUTO_COLLECTSTATIC:
            print("\n[6.3] 收集静态文件...")
            cmd = "cd {} && {}/bin/python manage.py collectstatic --noinput".format(
                REMOTE_PROJECT_PATH, REMOTE_VENV_PATH
            )
            status, output, error = self.exec_command(cmd, timeout=120)
        
        print("[OK] 数据库迁移完成")
        return True
    
    def restart_service(self):
        """重启服务"""
        if not AUTO_RESTART:
            print("\n跳过服务重启")
            return True
        
        print("\n" + "="*80)
        print("步骤 7/7: 重启服务")
        print("="*80)
        
        print("重启命令: {}".format(RESTART_COMMAND))
        status, output, error = self.exec_command(RESTART_COMMAND, timeout=60)
        
        if status != 0:
            print("[ERROR] 服务重启失败: {}".format(error))
            return False
        
        print("[OK] 服务重启完成")
        return True
    
    def verify_deployment(self):
        """验证部署"""
        if not AUTO_VERIFY:
            print("\n跳过部署验证")
            return True
        
        print("\n" + "="*80)
        print("验证部署")
        print("="*80)
        
        # 检查服务状态
        print("\n[验证] 检查服务状态...")
        cmd = "ps aux | grep -E 'python.*manage.py|gunicorn|uwsgi' | grep -v grep"
        status, output, error = self.exec_command(cmd)
        
        if output.strip():
            print("[OK] 服务正在运行")
        else:
            print("[WARN] 未检测到运行中的服务")
        
        # 检查端口
        print("\n[验证] 检查端口监听...")
        cmd = "netstat -tlnp | grep :8000"
        status, output, error = self.exec_command(cmd)
        
        if output.strip():
            print("[OK] 端口 8000 正在监听")
        else:
            print("[WARN] 端口 8000 未监听")
        
        print("\n[OK] 部署验证完成")
        print("\n" + "="*80)
        print("部署完成摘要")
        print("="*80)
        print("项目路径: {}".format(REMOTE_PROJECT_PATH))
        print("备份路径: {}".format(REMOTE_BACKUP_PATH))
        print("部署时间: {}".format(self.timestamp))
        print("\n后续操作:")
        print("1. 检查网站访问: {}".format(VERIFY_URLS[0] if VERIFY_URLS else "http://your_server_ip:8000"))
        print("2. 查看服务日志: journalctl -u eims2026 -f")
        print("3. 如有问题，可以回滚: {}".format(REMOTE_BACKUP_PATH))
        print("="*80)
        
        return True
    
    def deploy(self):
        """执行完整部署流程"""
        print("="*80)
        print("EIMS2026 自动化部署脚本")
        print("时间: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        print("="*80)
        
        try:
            # 1. 连接服务器
            if not self.connect():
                return False
            
            # 2. 备份服务器
            if not self.backup_server():
                return False
            
            # 3. 上传备份文件
            if not self.upload_backup():
                return False
            
            # 4. 部署代码
            if not self.deploy_code():
                return False
            
            # 5. 配置Python环境
            if not self.setup_virtualenv():
                return False
            
            # 6. 数据库迁移
            if not self.migrate_database():
                return False
            
            # 7. 重启服务
            if not self.restart_service():
                return False
            
            # 8. 验证部署
            if not self.verify_deployment():
                return False
            
            print("\n[SUCCESS] 自动化部署全部完成！")
            return True
            
        except KeyboardInterrupt:
            print("\n[WARN] 用户中断部署")
            return False
        except Exception as e:
            print("\n[ERROR] 部署失败: {}".format(str(e)))
            import traceback
            traceback.print_exc()
            return False
        finally:
            # 关闭连接
            if self.sftp:
                self.sftp.close()
            if self.ssh:
                self.ssh.close()

def main():
    """主函数"""
    deployer = EIMSDeployer()
    success = deployer.deploy()
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
