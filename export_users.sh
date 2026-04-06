#!/bin/bash
# 在服务器上运行此脚本导出用户数据
cd /var/www/eims
source venv/bin/activate

# 重定向所有错误输出到/dev/null，只保留JSON
python manage.py dumpdata auth.User auth.Group auth.Permission \
  --indent 2 \
  --natural-foreign \
  --natural-primary \
  2>/dev/null \
  > /tmp/users_export_clean.json

# 检查导出结果
if [ -f /tmp/users_export_clean.json ]; then
  echo "导出成功！"
  echo "文件大小："
  wc -c /tmp/users_export_clean.json
  echo "文件行数："
  wc -l /tmp/users_export_clean.json
  echo "前3行内容："
  head -3 /tmp/users_export_clean.json
else
  echo "导出失败！"
fi
