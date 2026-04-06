# 数据迁移 - JSON 文件损坏修复

**问题**: JSON 文件在编码转换后变成空文件  
**错误**: `json.decoder.JSONDecodeError: Expecting value: line 1 column 1`  
**原因**: GBK 解码失败导致文件被清空  

---

## 🔍 **问题分析**

### **当前状态**

```bash
已修复：/root/department_data.json
已修复：/root/role_data.json
```

但文件实际上是**空的**！

### **为什么会这样？**

Python 代码在尝试 `decode('gbk')` 时失败，但 `open(f, 'w')` 已经执行，导致文件被清空。

---

## ✅ **解决方案**

### **方案 1：重新上传文件（推荐）** ⭐⭐⭐⭐⭐

#### **步骤 1：在本地重新导出**

**在 Windows 上执行**：

```powershell
cd E:\EIMS2026

# 确保使用 UTF-8 编码导出
$env:PYTHONIOENCODING="utf-8"

# 重新导出部门数据
python manage.py dumpdata eims_app.Department --indent 2 --format json > department_data_utf8.json

# 重新导出角色数据
python manage.py dumpdata eims_app.Role --indent 2 --format json > role_data_utf8.json

# 验证文件
dir *.json
```

---

#### **步骤 2：上传到服务器**

```powershell
# 上传新文件
scp department_data_utf8.json root@39.106.41.239:/root/
scp role_data_utf8.json root@39.106.41.239:/root/
```

---

#### **步骤 3：在服务器上导入**

```bash
# SSH 登录
ssh root@39.106.41.239

# 检查文件大小（应该不为 0）
ls -lh /root/*.json

# 导入
cd /var/www/eims
source venv/bin/activate
python manage.py loaddata /root/department_data_utf8.json
python manage.py loaddata /root/role_data_utf8.json

# 验证
python manage.py shell -c "from eims_app.models import Department, Role; print('部门:', Department.objects.count(), '角色:', Role.objects.count())"
```

---

### **方案 2：使用二进制模式安全转换** ⭐⭐⭐⭐

如果无法重新导出，尝试这个更安全的转换方法：

```bash
# SSH 登录（已经是 root）
ssh root@39.106.41.239

# 创建备份
cp /root/department_data.json /root/department_data.json.bak
cp /root/role_data.json /root/role_data.json.bak

# 使用更安全的 Python 脚本
python3 << 'PYEOF'
import os
import shutil

def safe_convert_encoding(filepath):
    """安全地转换文件编码"""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print(f"✗ 文件不存在或为空：{filepath}")
        return False
    
    backup = filepath + '.bak'
    
    try:
        # 先读取为二进制
        with open(filepath, 'rb') as f:
            raw_bytes = f.read()
        
        # 尝试不同编码
        encodings_to_try = ['utf-8', 'gbk', 'gb2312', 'gb18030']
        
        for encoding in encodings_to_try:
            try:
                content = raw_bytes.decode(encoding)
                
                # 验证是否是有效的 JSON
                import json
                json.loads(content[:1000])  # 只验证前 1000 字符
                
                # 保存为 UTF-8
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✓ 使用 {encoding} 编码成功转换：{filepath}")
                return True
                
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
        
        print(f"✗ 所有编码都失败：{filepath}")
        return False
        
    except Exception as e:
        print(f"✗ 错误：{filepath} - {e}")
        # 恢复备份
        if os.path.exists(backup):
            shutil.copy(backup, filepath)
        return False

# 转换文件
for filepath in ['/root/department_data.json', '/root/role_data.json']:
    safe_convert_encoding(filepath)
PYEOF

# 检查文件大小
ls -lh /root/*.json

# 导入
cd /var/www/eims
source venv/bin/activate
python manage.py loaddata /root/department_data.json
python manage.py loaddata /root/role_data.json
```

---

### **方案 3：直接在 Windows 上使用 UTF-8 导出** ⭐⭐⭐⭐⭐

这是最可靠的方法：

#### **创建专用导出脚本**

在 `E:\EIMS2026\export_utf8.py` 创建：

```python
#!/usr/bin/env python
import os
import sys
import django
import json

# 配置 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Department, Role

def export_model(model_class, filename):
    """导出数据为 UTF-8 JSON"""
    print(f"正在导出 {model_class.__name__}...")
    
    # 获取所有对象
    objects = model_class.objects.all()
    
    data = []
    for obj in objects:
        # 手动序列化
        fields = {}
        for field in obj._meta.fields:
            value = getattr(obj, field.name)
            # 处理外键
            if field.is_relation and value:
                value = value.pk
            fields[field.name] = value
        
        data.append({
            'model': f'{model_class._meta.app_label}.{model_class._meta.model_name}',
            'pk': obj.pk,
            'fields': fields
        })
    
    # 写入 UTF-8 文件
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 导出 {len(data)} 条记录到 {filename}")
    return len(data)

if __name__ == '__main__':
    dept_count = export_model(Department, 'department_data_utf8.json')
    role_count = export_model(Role, 'role_data_utf8.json')
    
    print(f"\n总计:")
print(f"  部门：{dept_count} 条")
print(f"  角色：{role_count} 条")
print("\n✅ 导出完成！文件已 UTF-8 编码")
```

---

#### **执行导出**

```powershell
cd E:\EIMS2026
python export_utf8.py
```

---

#### **上传到服务器**

```powershell
scp department_data_utf8.json root@39.106.41.239:/root/
scp role_data_utf8.json root@39.106.41.239:/root/
```

---

#### **在服务器上导入**

```bash
ssh root@39.106.41.239

cd /var/www/eims
source venv/bin/activate

python manage.py loaddata /root/department_data_utf8.json
python manage.py loaddata /root/role_data_utf8.json

# 验证
python manage.py shell -c "from eims_app.models import Department, Role; print('成功！部门:', Department.objects.count(), '角色:', Role.objects.count())"
```

---

## 📋 **快速诊断命令**

### **检查文件是否为空**

```bash
# SSH 登录
ssh root@39.106.41.239

# 查看文件大小
ls -lh /root/*.json

# 查看文件内容前几行
head -n 10 /root/department_data.json

# 如果是空的，会什么都不显示
# 如果正常，应该看到类似：
# [
#   {
#     "model": "eims_app.department",
#     "pk": 1,
#     ...
#   }
# ]
```

---

### **检查文件编码**

```bash
# 查看文件编码
file -i /root/department_data.json

# 正常应该显示：
# charset=utf-8 或 charset=us-ascii
# 如果显示 charset=binary 或其他，有问题
```

---

## ⚠️ **预防措施**

### **正确的编码转换方法**

```python
#!/usr/bin/env python3
import os

def convert_with_backup(filepath):
    """带备份的安全转换"""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print(f"✗ 文件无效：{filepath}")
        return
    
    backup = filepath + '.backup'
    
    # 创建备份
    with open(filepath, 'rb') as src:
        with open(backup, 'wb') as dst:
            dst.write(src.read())
    
    print(f"✓ 已创建备份：{backup}")
    
    # 读取原始内容
    with open(filepath, 'rb') as f:
        raw_bytes = f.read()
    
    # 尝试不同编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    
    for encoding in encodings:
        try:
            content = raw_bytes.decode(encoding)
            
            # 验证 JSON
            import json
            json.loads(content[:500])
            
            # 保存为 UTF-8
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ 成功使用 {encoding} 编码转换")
            return
            
        except:
            continue
    
    # 如果都失败，恢复备份
    print("✗ 转换失败，恢复备份")
    with open(backup, 'rb') as src:
        with open(filepath, 'wb') as dst:
            dst.write(src.read())

# 使用
convert_with_backup('/root/department_data.json')
convert_with_backup('/root/role_data.json')
```

---

## 🎯 **推荐流程**

### **最简单可靠的方式**

```powershell
# 1. 在 Windows 上重新导出（使用重定向，自动 UTF-8）
cd E:\EIMS2026
python manage.py dumpdata eims_app.Department --indent 2 > department_data_utf8.json
python manage.py dumpdata eims_app.Role --indent 2 > role_data_utf8.json

# 2. 上传到服务器
scp department_data_utf8.json root@39.106.41.239:/root/
scp role_data_utf8.json root@39.106.41.239:/root/

# 3. SSH 登录并导入
ssh root@39.106.41.239

cd /var/www/eims
source venv/bin/activate
python manage.py loaddata /root/department_data_utf8.json
python manage.py loaddata /root/role_data_utf8.json

# 4. 验证
python manage.py shell -c "from eims_app.models import Department, Role; print('成功！部门:', Department.objects.count(), '角色:', Role.objects.count())"
```

---

## 🎊 **总结**

### **问题根源**

❌ 之前的转换代码直接 `open(f, 'w')` 导致文件被清空  
✅ 需要先读取验证，再写入  

---

### **解决方案**

**首选**: **重新导出为 UTF-8**

```powershell
# Windows 上
python manage.py dumpdata eims_app.Department --indent 2 > department_data_utf8.json
python manage.py dumpdata eims_app.Role --indent 2 > role_data_utf8.json

# 上传
scp *.json root@39.106.41.239:/root/

# 服务器上导入
ssh root@39.106.41.239
cd /var/www/eims && source venv/bin/activate
python manage.py loaddata /root/department_data_utf8.json
python manage.py loaddata /root/role_data_utf8.json
```

---

### **预期结果**

```
Installed 10 object(s) from 1 fixture(s)
Installed 7 object(s) from 1 fixture(s)
成功！部门：10 角色：7
```

---

**位置**: `E:\EIMS2026\bat\JSON 文件损坏修复指南.md`  
**状态**: ⚠️ 需要重新导出或安全转换  
**下一步**: 在 Windows 上重新导出 JSON 文件！

---

**重新导出为 UTF-8，问题就能解决！** 🚀✨
