"""
EIMS2026 自动化部署配置文件
请在部署前填写以下配置信息
"""

# ==================== 服务器配置 ====================
# SSH 连接信息
SSH_HOST = "39.106.41.239"      # 阿里云服务器公网IP
SSH_PORT = 22                   # SSH端口，默认22
SSH_USER = "root"               # 宝塔面板默认root用户
SSH_PASSWORD = "fjkl546#"       # SSH密码（已在宝塔面板重置或使用密钥认证）
SSH_KEY_FILE = ""               # SSH私钥文件路径（例如: ~/.ssh/id_rsa）

# ==================== 部署路径配置 ====================
# 服务器上的项目部署路径（宝塔面板推荐路径）
REMOTE_PROJECT_PATH = "/www/wwwroot/EIMS2026"    # 项目根目录（宝塔默认网站目录）
REMOTE_BACKUP_PATH = "/www/backup/EIMS2026"      # 备份目录（宝塔备份目录）
REMOTE_VENV_PATH = "/www/wwwroot/EIMS2026/venv"  # 虚拟环境路径

# ==================== 数据库配置 ====================
# 服务器MySQL数据库配置
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_USER = "root"
MYSQL_PASSWORD = "EIMS2026_mysql"  # 服务器MySQL密码

# 需要备份的数据库列表
DATABASES = [
    'eims_root',
    'eims_dingce',
    'eims_shengchang',
    'eims_jiachengda',
]

# ==================== 部署选项 ====================
# 是否自动备份服务器数据（强烈建议开启）
AUTO_BACKUP_SERVER = True

# 是否自动执行数据库迁移
AUTO_MIGRATE = True

# 是否自动收集静态文件
AUTO_COLLECTSTATIC = True

# 是否自动重启服务
AUTO_RESTART = True

# 服务重启命令（宝塔面板使用supervisor管理Python应用）
# 如果使用宝塔面板的Python项目管理器：
RESTART_COMMAND = "bt 16"  # 宝塔菜单16是重启所有服务
# 或者使用supervisorctl：
# RESTART_COMMAND = "sudo supervisorctl restart eims2026"

# ==================== 本地备份配置 ====================
# 本地备份文件路径（使用之前创建的备份）
LOCAL_BACKUP_FILE = "backup/EIMS2026_backup_20260421_073419.tar.gz"

# ==================== 部署后验证 ====================
# 是否自动验证部署
AUTO_VERIFY = True

# 验证URL列表（使用您的服务器IP）
VERIFY_URLS = [
    "http://39.106.41.239:8000/",
    "http://39.106.41.239:8000/root/",
    "http://39.106.41.239:8000/dingce/",
    "http://39.106.41.239:8000/shengchang/",
    "http://39.106.41.239:8000/jiachengda/",
]
