#!/bin/bash
# 数据库自动备份脚本
# 使用方法：
# 1. 添加到 crontab: crontab -e
# 2. 添加定时任务：0 2 * * * /var/www/eims/backup_db.sh（每天凌晨 2 点备份）

# 配置
DB_NAME="eims"
DB_USER="eims_user"
DB_PASSWORD="你的数据库密码"
BACKUP_DIR="/var/backups/eims"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30  # 保留 30 天备份

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份文件名
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_$DATE.sql"

# 执行备份
echo "开始备份数据库：$BACKUP_FILE"
mysqldump -u $DB_USER -p$DB_PASSWORD --default-character-set=utf8mb4 $DB_NAME > $BACKUP_FILE

# 压缩备份
echo "压缩备份文件..."
gzip $BACKUP_FILE

# 删除过期备份
echo "删除 $RETENTION_DAYS 天前的备份..."
find $BACKUP_DIR -name "${DB_NAME}_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# 显示备份大小
BACKUP_SIZE=$(ls -lh ${BACKUP_FILE}.gz | awk '{print $5}')
echo "备份完成！文件大小：$BACKUP_SIZE"

# 可选：上传到云存储（如阿里云 OSS）
# ossutil cp ${BACKUP_FILE}.gz oss://your-bucket/backups/
