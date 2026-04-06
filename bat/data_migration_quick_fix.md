# 数据迁移 - 快速修复指南

**状态**: ✅ 导出和上传成功  
**问题**: ❌ 导入失败，编码问题（GBK vs UTF-8）  
**解决方案**: 在服务器上修复编码，然后导入

---

## 🚀 **快速修复（5 分钟）**

### **步骤 1：SSH 登录服务器**

```bash
ssh root@39.106.41.239
```

---

### **步骤 2：运行修复脚本**

我已经为您创建了脚本。只需运行：

```bash
bash /root/import_data_fix_encoding.sh
```

这个脚本会：
1. ✅ 修复文件编码（GBK → UTF-8）
2. ✅ 导入部门数据
3. ✅ 导入角色数据
4. ✅ 验证结果

---

### **预期输出**

```
======================================
EIMS Data Import - Fix Encoding
======================================

Files found. Starting encoding fix...

[1/3] Fixing file encoding...
SUCCESS: Fixed encoding for /root/department_data.json
SUCCESS: Fixed encoding for /root/role_data.json

[2/3] Importing data...
Importing departments...
Installed 10 object(s) from 1 fixture(s)
  SUCCESS: Department data imported

Importing roles...
Installed 7 object(s) from 1 fixture(s)
  SUCCESS: Role data imported

[3/3] Verifying import...

Import Statistics:
  Departments: 10
  Roles: 7

Sample departments:
  - DEV001: 研发部
  - HR001: 人力资源部
  ...

Sample roles:
  - 超级管理员
  - 系统管理员
  ...

======================================
Data import completed successfully!
======================================
```

---

## 🔧 **备选方案：手动修复**

如果脚本不工作，使用这些命令：

### **手动编码修复**

```bash
# SSH 登录
ssh root@39.106.41.239

# 使用 Python 修复编码
python3 << 'EOF'
for filepath in ['/root/department_data.json', '/root/role_data.json']:
    try:
        with open(filepath, 'rb') as f:
            content = f.read().decode('gbk')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'已修复：{filepath}')
    except Exception as e:
        print(f'错误：{filepath} - {e}')
EOF

# 导入数据
cd /var/www/eims
source venv/bin/activate
python manage.py loaddata /root/department_data.json
python manage.py loaddata /root/role_data.json

# 验证
python manage.py shell -c "from eims_app.models import Department, Role; print('成功！部门:', Department.objects.count(), '角色:', Role.objects.count())"
```

---

## ⚠️ **出了什么问题？**

### **问题描述**

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xbc in position 447
```

**为什么？**
- Windows 对中文字符使用 **GBK 编码**
- Linux Python 期望 **UTF-8 编码**
- JSON 文件包含中文文本
- Linux 无法解码 GBK 编码的文件

---

### **解决方案**

在服务器上导入前，将文件从 GBK 转换为 UTF-8。

---

## 📊 **为您创建的文件**

| 文件 | 用途 | 位置 |
|------|------|------|
| **export_department_role_data.bat** | 英文版本（无编码问题） | `bat\` |
| **import_data_fix_encoding.sh** | 服务器导入和编码修复 | 需上传到服务器 |
| **data_migration_fix_encoding.md** | 详细故障排除指南 | `bat\` |

---

## 🎯 **总结**

### **当前状态**

✅ **已导出** - 部门和角色数据（Windows）  
✅ **已上传** - 文件在服务器上  
❌ **导入失败** - 编码不匹配  

---

### **下一步操作**

**在服务器上运行**：

```bash
ssh root@39.106.41.239
bash /root/import_data_fix_encoding.sh
```

**或者手动**：

```bash
ssh root@39.106.41.239
python3 << 'EOF'
for f in ['/root/department_data.json', '/root/role_data.json']:
    open(f, 'w', encoding='utf-8').write(open(f, 'rb').read().decode('gbk'))
EOF
cd /var/www/eims && source venv/bin/activate
python manage.py loaddata /root/department_data.json
python manage.py loaddata /root/role_data.json
```

---

### **结果**

✅ **编码已修复** - GBK → UTF-8  
✅ **数据已导入** - 部门和角色  
✅ **数据库已更新** - 可以使用  

---

**位置**: `E:\EIMS2026\bat\data_migration_quick_fix.md`  
**状态**: ⚠️ 需要在服务器上手动操作  
**时间**: 约 5 分钟  
**下一步**: SSH 到服务器并运行修复脚本！

---

**修复编码问题后，导入就能完美工作了！** 🔧✨
