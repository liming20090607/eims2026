#!/usr/bin/env python3
import os, sys

print("=" * 60)
print("检查文件状态")
print("=" * 60)

files = ['/root/department_data.json', '/root/role_data.json']

for filepath in files:
    print(f"\n文件：{filepath}")
    
    if not os.path.exists(filepath):
        print("  ❌ 文件不存在")
        continue
    
    size = os.path.getsize(filepath)
    print(f"  大小：{size} 字节")
    
    if size == 0:
        print("  ❌ 文件是空的")
        continue
    
    # 读取前 100 字节查看内容
    with open(filepath, 'rb') as f:
        raw = f.read(100)
    
    print(f"  前 100 字节（十六进制）: {raw.hex()}")
    print(f"  前 100 字节（文本）: {raw}")
    
    # 尝试不同编码
    print("\n  尝试解码:")
    for enc in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030', 'latin1']:
        try:
            content = raw.decode(enc)
            print(f"    ✓ {enc}: {repr(content[:50])}")
        except Exception as e:
            print(f"    ✗ {enc}: {e}")
