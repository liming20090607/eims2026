#!/usr/bin/env python3
import os
import json

def fix_json(filepath):
    """修复 JSON 文件编码"""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
    
    size = os.path.getsize(filepath)
    if size == 0:
        print(f"File is empty: {filepath}")
        return False
    
    print(f"Processing: {filepath} ({size} bytes)")
    
    # Backup
    backup = filepath + '.backup'
    with open(filepath, 'rb') as f:
        raw = f.read()
    with open(backup, 'wb') as f:
        f.write(raw)
    print(f"Backup created: {backup}")
    
    # Try different encodings
    encodings = [
        ('utf-8-sig', 'UTF-8 with BOM'),
        ('gbk', 'GBK Chinese'),
        ('gb2312', 'GB2312'),
        ('gb18030', 'GB18030'),
        ('latin1', 'Latin-1'),
        ('utf-8', 'UTF-8')
    ]
    
    for enc, desc in encodings:
        try:
            print(f"  Trying {desc} ({enc})...", end=' ')
            content = raw.decode(enc)
            
            # Remove BOM if present
            if content.startswith('\ufeff'):
                content = content[1:]
            
            # Validate JSON
            data = json.loads(content)
            
            # Save as clean UTF-8
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            new_size = os.path.getsize(filepath)
            print(f"SUCCESS! ({size} -> {new_size} bytes)")
            print(f"  Records: {len(data)}")
            return True
            
        except Exception as e:
            print(f"Failed: {e}")
            continue
    
    print("All encodings failed!")
    # Restore backup
    with open(backup, 'rb') as f:
        raw = f.read()
    with open(filepath, 'wb') as f:
        f.write(raw)
    print(f"Restored from backup")
    return False

if __name__ == '__main__':
    files = ['/root/department_data.json', '/root/role_data.json']
    success = sum(1 for f in files if fix_json(f))
    print(f"\nCompleted: {success}/{len(files)} files fixed")
