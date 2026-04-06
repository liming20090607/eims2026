#!/bin/bash

echo "======================================"
echo "EIMS 数据导入工具 - 部门和角色
echo "======================================"
echo ""

# 检查是否 root
if [ "$EUID" -ne 0 ]; then 
  echo "❌ 请使用 root 用户或 sudo 执行"
  exit 1
fi

# 检查文件是否存在
if [ ! -f "/root/department_data.json" ]; then
    echo "❌ 部门数据文件不存在"
    echo "请先从本地上传文件："
    echo "  scp department_data.json root@39.106.41.239:/root/"
    exit 1
fi

if [ ! -f "/root/role_data.json" ]; then
    echo "❌ 角色数据文件不存在"
    echo "请先从本地上传文件："
    echo "  scp role_data.json root@39.106.41.239:/root/"
    exit 1
fi

echo "✅ 数据文件检查通过"
echo ""

# 进入项目目录
cd /var/www/eims || exit 1

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

echo "======================================"
echo "开始导入数据...
echo "======================================"
echo ""

# 备份现有数据
echo "[准备] 备份现有数据..."
BACKUP_DIR="/root/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

python manage.py dumpdata eims_app.Department > $BACKUP_DIR/department_backup.json
python manage.py dumpdata eims_app.Role > $BACKUP_DIR/role_backup.json

echo "  ✅ 备份到：$BACKUP_DIR"
echo ""

# 导入部门数据
echo "[1/2] 导入部门数据..."
python manage.py loaddata /root/department_data.json

if [ $? -eq 0 ]; then
    echo "  ✅ 部门数据导入成功"
else
    echo "  ❌ 部门数据导入失败"
    echo ""
    echo "错误信息："
    echo "  1. 检查 JSON 文件格式是否正确"
    echo "  2. 检查是否有 ID 冲突"
    echo "  3. 查看错误日志"
    exit 1
fi

echo ""

# 导入角色数据
echo "[2/2] 导入角色数据..."
python manage.py loaddata /root/role_data.json

if [ $? -eq 0 ]; then
    echo "  ✅ 角色数据导入成功"
else
    echo "  ❌ 角色数据导入失败"
    exit 1
fi

echo ""

# 验证导入
echo "======================================"
echo "验证导入结果...
echo "======================================"
echo ""

DEPT_COUNT=$(python manage.py shell -c "from eims_app.models import Department; print(Department.objects.count())")
ROLE_COUNT=$(python manage.py shell -c "from eims_app.models import Role; print(Role.objects.count())")

echo "📊 导入统计："
echo "  部门总数：$DEPT_COUNT"
echo "  角色总数：$ROLE_COUNT"
echo ""

# 显示最新数据
echo "最新部门："
python manage.py shell -c "from eims_app.models import Department; [print(f'  ✅ {d.department_code} - {d.department_name}') for d in Department.objects.all()[:5]]"

echo ""
echo "最新角色："
python manage.py shell -c "from eims_app.models import Role; [print(f'  ✅ {r.get_role_display()}') for r in Role.objects.all()[:5]]"

echo ""
echo "======================================"
echo "✅ 数据导入完成！
echo "======================================"
echo ""
echo "备份位置：$BACKUP_DIR"
echo ""
echo "下一步："
echo "  1. 访问网站验证：https://yourdomain.com"
echo "  2. 检查后台管理：https://yourdomain.com/admin/"
echo "  3. 测试部门功能"
echo ""
