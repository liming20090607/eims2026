#!/usr/bin/env python
"""
安全地转换 JSON 文件编码（带备份和验证）
"""
import os
import sys
import json
import shutil

def safe_convert(filepath):
    """安全转换文件编码"""
    if not os.path.exists(filepath):
        print(f"✗ 文件不存在：{filepath}")
        return False
    
    file_size = os.path.getsize(filepath)
    if file_size == 0:
        print(f"✗ 文件为空：{filepath}")
        return False
    
    print(f"正在处理：{filepath} ({file_size} 字节)")
    
    # 创建备份
    backup = filepath + '.backup'
    try:
        shutil.copy2(filepath, backup)
        print(f"✓ 已创建备份：{backup}")
    except Exception as e:
        print(f"⚠ 无法创建备份：{e}")
    
    # 读取原始字节
    try:
        with open(filepath, 'rb') as f:
            raw_bytes = f.read()
    except Exception as e:
        print(f"✗ 读取失败：{e}")
        return False
    
    # 尝试不同编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    
    for encoding in encodings:
        try:
            # 尝试解码
            content = raw_bytes.decode(encoding)
            
            # 验证 JSON 格式（只验证前 1000 字符）
            test_content = content[:1000] if len(content) > 1000 else content
            json.loads(test_content)
            
            # 完整验证
            json.loads(content)
            
            # 保存为 UTF-8
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            new_size = os.path.getsize(filepath)
            print(f"✓ 使用 {encoding} 编码成功转换 ({file_size} → {new_size} 字节)")
            return True
            
        except UnicodeDecodeError:
            print(f"  - {encoding} 解码失败")
            continue
        except json.JSONDecodeError as e:
            print(f"  - {encoding} 解码成功但 JSON 无效：{e}")
            # 恢复备份
            if os.path.exists(backup):
                shutil.copy2(backup, filepath)
                print(f"✓ 已恢复备份")
            return False
        except Exception as e:
            print(f"  - {encoding} 发生错误：{e}")
            continue
    
    # 所有编码都失败
    print(f"✗ 所有编码转换都失败")
    # 恢复备份
    if os.path.exists(backup):
        shutil.copy2(backup, filepath)
        print(f"✓ 已恢复备份")
    return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python safe_convert_encoding.py <文件路径>")
        print("示例：python safe_convert_encoding.py /root/department_data.json")
        sys.exit(1)
    
    files = sys.argv[1:]
    success_count = 0
    
    for filepath in files:
        if safe_convert(filepath):
            success_count += 1
        print()
    
    print(f"处理完成：{success_count}/{len(files)} 个文件成功")
