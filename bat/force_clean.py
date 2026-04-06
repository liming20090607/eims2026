#!/usr/bin/env python3
import os, json

print("=" * 60)
print("强力清理 JSON 文件")
print("=" * 60)

files = ['/root/department_data.json', '/root/role_data.json']

for filepath in files:
    print(f"\n处理：{filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ❌ 文件不存在")
        continue
    
    # 读取原始字节
    with open(filepath, 'rb') as f:
        raw_bytes = f.read()
    
    print(f"  原始大小：{len(raw_bytes)} 字节")
    
    # 尝试不同编码
    content = None
    for enc in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']:
        try:
            content = raw_bytes.decode(enc)
            print(f"  ✓ 使用 {enc} 解码成功")
            break
        except:
            continue
    
    if not content:
        print(f"  ❌ 无法解码")
        continue
    
    # 移除开头的非 JSON 内容（如 "Fixed Python path..."）
    lines = content.split('\n')
    json_start = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('[') or line.strip().startswith('{'):
            json_start = i
            break
    
    if json_start > 0:
        print(f"  移除开头 {json_start} 行非 JSON 内容")
        content = '\n'.join(lines[json_start:])
    
    # 验证 JSON
    try:
        data = json.loads(content)
        print(f"  ✓ JSON 验证成功，记录数：{len(data)}")
        
        # 保存为干净的 UTF-8（无 BOM）
        backup = filepath + '.backup'
        with open(backup, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ 备份到：{backup}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ 已保存到：{filepath}")
        
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON 验证失败：{e}")
        print(f"  前 300 字符：\n{content[:300]}")

print("\n完成!")
