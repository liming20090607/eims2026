#!/usr/bin/env python3
import os, json, re

print("=" * 60)
print("清理并修复 JSON 文件")
print("=" * 60)

files = [
    '/root/department_data.json',
    '/root/role_data.json'
]

for filepath in files:
    print(f"\n处理：{filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ❌ 文件不存在")
        continue
    
    # 读取文件内容
    with open(filepath, 'rb') as f:
        raw = f.read()
    
    print(f"  原始大小：{len(raw)} 字节")
    
    # 尝试不同编码解码
    content = None
    for enc in ['utf-8-sig', 'gbk', 'gb2312', 'gb18030']:
        try:
            content = raw.decode(enc)
            print(f"  ✓ 使用 {enc} 解码成功")
            break
        except:
            continue
    
    if not content:
        print(f"  ❌ 无法解码")
        continue
    
    # 移除开头的非 JSON 内容（Fixed Python path 等）
    # 找到第一个 [ 或 { 的位置
    start_pos = -1
    for i, char in enumerate(content):
        if char == '[' or char == '{':
            start_pos = i
            break
    
    if start_pos > 0:
        print(f"  移除开头 {start_pos} 字节的非 JSON 内容")
        content = content[start_pos:]
    
    # 移除可能的尾部垃圾内容
    # 找到最后一个 ] 或 } 的位置
    end_pos = -1
    for i in range(len(content)-1, -1, -1):
        if content[i] == ']' or content[i] == '}':
            end_pos = i + 1
            break
    
    if end_pos > 0 and end_pos < len(content):
        print(f"  移除尾部 {len(content)-end_pos} 字节的垃圾内容")
        content = content[:end_pos]
    
    # 清理后的内容
    print(f"  清理后大小：{len(content)} 字节")
    
    # 验证 JSON
    try:
        data = json.loads(content)
        print(f"  ✓ JSON 验证成功，记录数：{len(data)}")
        
        # 保存为干净的 UTF-8
        backup = filepath + '.clean.bak'
        with open(backup, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ 备份到：{backup}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ 已保存到：{filepath}")
        
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON 验证失败：{e}")
        print(f"  前 200 字符：{content[:200]}")

print("\n完成!")
