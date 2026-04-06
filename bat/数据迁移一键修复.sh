#!/bin/bash

echo "======================================"
echo "EIMS 数据迁移 - 一键修复和导入
echo "======================================"
echo ""

# 检查是否是 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  当前不是 root 用户，尝试切换..."
    
    # 尝试使用 sudo
    if sudo -v 2>/dev/null; then
        echo "✓ 重新以 root 权限执行此脚本"
        sudo bash "$0" "$@"
        exit $?
    else
        echo "❌ 错误：需要 root 权限"
        echo ""
        echo "请执行以下命令切换到 root："
        echo "  sudo su -"
        echo ""
        echo "然后重新运行此脚本"
        exit 1
    fi
fi

echo "✅ 当前用户：root"
echo ""

# 检查文件是否存在
if [ ! -f "/root/department_data.json" ]; then
    echo "❌ 错误：找不到 /root/department_data.json"
    echo ""
    echo "提示："
    echo "  1. 确认文件已从 Windows 上传到服务器"
    echo "  2. 使用 SCP 或 FTP 工具上传文件到 /root/"
    exit 1
fi

if [ ! -f "/root/role_data.json" ]; then
    echo "❌ 错误：找不到 /root/role_data.json"
    exit 1
fi

echo "✓ 找到数据文件"
echo ""

# 创建 Python 修复脚本
cat > /tmp/fix_encoding.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import sys
import os

def fix_encoding(filepath):
    """将文件从 GBK 转换为 UTF-8"""
    if not os.path.exists(filepath):
        print(f"✗ 文件不存在：{filepath}")
        return False
    
    try:
        # 读取原始内容
        with open(filepath, 'rb') as f:
            raw_content = f.read()
        
        # 尝试解码为 GBK
        try:
            content = raw_content.decode('gbk')
            
            # 保存为 UTF-8
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ 已修复：{filepath}")
            return True
            
        except UnicodeDecodeError:
            # 可能已经是 UTF-8
            try:
                content = raw_content.decode('utf-8')
                print(f"- 已是 UTF-8: {filepath}")
                return True
            except:
                print(f"✗ 无法识别的编码：{filepath}")
                return False
                
    except Exception as e:
        print(f"✗ 错误：{filepath} - {e}")
        return False

if __name__ == '__main__':
    files = sys.argv[1:]
    success_count = 0
    
    for filepath in files:
        if fix_encoding(filepath):
            success_count += 1
    
    print(f"\n处理完成：{success_count}/{len(files)} 个文件")
PYTHON_EOF

# 步骤 1：修复编码
echo "[1/4] 修复文件编码..."
python3 /tmp/fix_encoding.py /root/department_data.json /root/role_data.json

if [ $? -ne 0 ]; then
    echo "⚠️  警告：部分文件编码修复失败"
fi

echo ""

# 步骤 2：进入项目目录
echo "[2/4] 准备导入数据..."
cd /var/www/eims || {
    echo "❌ 错误：找不到项目目录 /var/www/eims"
    exit 1
}

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误：找不到虚拟环境 venv"
    exit 1
fi

source venv/bin/activate

echo "✓ 虚拟环境已激活"
echo ""

# 步骤 3：导入数据
echo "[3/4] 导入部门数据..."
python manage.py loaddata /root/department_data.json

if [ $? -eq 0 ]; then
    echo "  ✓ 部门数据导入成功"
else
    echo "  ✗ 部门数据导入失败"
    echo ""
    echo "可能的原因："
    echo "  1. JSON 文件格式不正确"
    echo "  2. 数据库连接问题"
    echo "  3. 模型定义不匹配"
    exit 1
fi

echo ""
echo "导入角色数据..."
python manage.py loaddata /root/role_data.json

if [ $? -eq 0 ]; then
    echo "  ✓ 角色数据导入成功"
else
    echo "  ✗ 角色数据导入失败"
    exit 1
fi

echo ""

# 步骤 4：验证
echo "[4/4] 验证导入结果..."
echo ""

DEPT_COUNT=$(python manage.py shell -c "from eims_app.models import Department; print(Department.objects.count())")
ROLE_COUNT=$(python manage.py shell -c "from eims_app.models import Role; print(Role.objects.count())")

echo "📊 导入统计："
echo "  部门总数：$DEPT_COUNT"
echo "  角色总数：$ROLE_COUNT"
echo ""

if [ "$DEPT_COUNT" -gt 0 ] || [ "$ROLE_COUNT" -gt 0 ]; then
    echo "✓ 数据导入成功！"
    echo ""
    
    echo "最新部门（前 5 个）："
    python manage.py shell -c "from eims_app.models import Department; [print(f'  • {d.department_code}: {d.department_name}') for d in Department.objects.all()[:5]]"
    
    echo ""
    echo "最新角色（前 5 个）："
    python manage.py shell -c "from eims_app.models import Role; [print(f'  • {r.get_role_display()}') for r in Role.objects.all()[:5]]"
    
    echo ""
    echo "======================================"
    echo "✅ 数据迁移完成！
    echo "======================================"
    echo ""
    echo "下一步："
    echo "  1. 访问网站验证数据"
    echo "  2. 检查后台管理系统"
    echo "  3. 测试部门和角色功能"
    echo ""
else
    echo "⚠️  警告：导入后数据量为 0"
    echo ""
    echo "请检查："
    echo "  1. JSON 文件格式是否正确"
    echo "  2. 数据库表是否存在"
    echo "  3. Django 模型是否匹配"
    exit 1
fi
