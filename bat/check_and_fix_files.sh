#!/bin/bash

echo "======================================"
echo "EIMS 数据迁移 - 检查和修复文件
echo "======================================"
echo ""

# 检查文件
echo "[1/4] 检查文件大小..."
ls -lh /root/*.json

echo ""
echo "[2/4] 检查文件编码..."
file -i /root/department_data.json
file -i /root/role_data.json

echo ""
echo "[3/4] 查看文件内容前几行..."
echo "--- department_data.json ---"
head -n 5 /root/department_data.json

echo ""
echo "--- role_data.json ---"
head -n 5 /root/role_data.json

echo ""
echo "[4/4] 使用 Python 安全转换..."
python3 << 'PYEOF'
import os
import json

def fix_json_file(filepath):
    """修复 JSON 文件编码"""
    if not os.path.exists(filepath):
        print(f"✗ 文件不存在：{filepath}")
        return False
    
    file_size = os.path.getsize(filepath)
    if file_size == 0:
        print(f"✗ 文件为空：{filepath}")
        return False
    
    print(f"\n处理文件：{filepath} ({file_size} 字节)")
    
    # 备份
    backup = filepath + '.bak'
    with open(filepath, 'rb') as f:
        raw_bytes = f.read()
    with open(backup, 'wb') as f:
        f.write(raw_bytes)
    print(f"✓ 已创建备份：{backup}")
    
    # 尝试不同编码
    encodings = [
        ('utf-8-sig', 'UTF-8 with BOM'),
        ('gbk', 'GBK (Simplified Chinese)'),
        ('gb2312', 'GB2312'),
        ('gb18030', 'GB18030'),
        ('utf-8', 'UTF-8')
    ]
    
    for encoding, desc in encodings:
        try:
            print(f"  尝试 {desc} ({encoding})...", end=' ')
            
            # 解码
            content = raw_bytes.decode(encoding)
            
            # 清理可能的 BOM
            if content.startswith('\ufeff'):
                content = content[1:]
            
            # 验证 JSON
            data = json.loads(content)
            
            # 保存为标准 UTF-8（无 BOM）
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            new_size = os.path.getsize(filepath)
            print(f"✓ 成功！({file_size} → {new_size} 字节)")
            print(f"  记录数：{len(data)}")
            return True
            
        except UnicodeDecodeError as e:
            print(f"✗ 解码失败")
            continue
        except json.JSONDecodeError as e:
            print(f"✗ JSON 无效：{e}")
            # 恢复备份
            with open(backup, 'rb') as f:
                raw_bytes = f.read()
            with open(filepath, 'wb') as f:
                f.write(raw_bytes)
            return False
        except Exception as e:
            print(f"✗ 错误：{e}")
            return False
    
    print("✗ 所有编码都失败")
    return False

# 修复两个文件
files = ['/root/department_data.json', '/root/role_data.json']
success_count = 0

for filepath in files:
    if fix_json_file(filepath):
        success_count += 1

print(f"\n{'='*50}")
print(f"处理完成：{success_count}/{len(files)} 个文件成功")
PYEOF

echo ""
echo "[5/4] 验证修复后的文件..."
file -i /root/*.json
ls -lh /root/*.json

echo ""
echo "======================================"
echo "✅ 文件修复完成！
echo "======================================"
echo ""
echo "下一步："
echo "  cd /var/www/eims"
echo "  source venv/bin/activate"
echo "  python manage.py loaddata /root/department_data.json"
echo "  python manage.py loaddata /root/role_data.json"
echo ""
