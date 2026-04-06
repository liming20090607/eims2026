# Data Migration - Fix Encoding Issue

**Problem**: `UnicodeDecodeError: 'utf-8' codec can't decode byte`  
**Cause**: Windows saves files in GBK encoding, Linux expects UTF-8  
**Solution**: Convert file encoding before importing

---

## ✅ **Current Status**

```
✅ Department data exported (5590 bytes)
✅ Role data exported (1449 bytes)
✅ Files uploaded to server
❌ Import failed due to encoding issue
```

---

## 🔧 **Fix the Encoding Issue**

### **Step 1: SSH to Server**

```bash
ssh root@39.106.41.239
```

---

### **Step 2: Convert File Encoding**

The JSON files were created on Windows with GBK encoding. We need to convert them to UTF-8.

**Option A: Using iconv (if available)**

```bash
# Convert department data
iconv -f GBK -t UTF-8 /root/department_data.json > /root/department_data_utf8.json
mv /root/department_data_utf8.json /root/department_data.json

# Convert role data
iconv -f GBK -t UTF-8 /root/role_data.json > /root/role_data_utf8.json
mv /root/role_data_utf8.json /root/role_data.json
```

---

**Option B: Using Python (recommended)**

```bash
# Create conversion script
cat > /root/fix_encoding.py << 'EOF'
#!/usr/bin/env python3
import os

def fix_encoding(filepath):
    """Convert file from GBK to UTF-8"""
    try:
        # Try reading as GBK
        with open(filepath, 'r', encoding='gbk') as f:
            content = f.read()
        
        # Write as UTF-8
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Fixed: {filepath}")
        return True
    except UnicodeDecodeError:
        # Already UTF-8 or other encoding
        print(f"- Already UTF-8 or different encoding: {filepath}")
        return False
    except Exception as e:
        print(f"✗ Error: {filepath} - {e}")
        return False

if __name__ == '__main__':
    files = [
        '/root/department_data.json',
        '/root/role_data.json'
    ]
    
    for filepath in files:
        if os.path.exists(filepath):
            fix_encoding(filepath)
        else:
            print(f"File not found: {filepath}")
EOF

# Run the script
python3 /root/fix_encoding.py
```

---

### **Step 3: Import Data**

After fixing the encoding:

```bash
cd /var/www/eims
source venv/bin/activate

# Import departments
python manage.py loaddata /root/department_data.json

# Import roles
python manage.py loaddata /root/role_data.json
```

---

### **Step 4: Verify**

```bash
python manage.py shell -c "from eims_app.models import Department, Role; print('Departments:', Department.objects.count(), 'Roles:', Role.objects.count())"
```

---

## 🚀 **Quick Fix Commands (Copy & Paste)**

```bash
# SSH login
ssh root@39.106.41.239

# Fix encoding using Python
python3 << 'EOF'
import os

for filepath in ['/root/department_data.json', '/root/role_data.json']:
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='gbk') as f:
                content = f.read()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed: {filepath}')
        except:
            print(f'Skip: {filepath}')
EOF

# Import data
cd /var/www/eims
source venv/bin/activate
python manage.py loaddata /root/department_data.json
python manage.py loaddata /root/role_data.json

# Verify
python manage.py shell -c "from eims_app.models import Department, Role; print('Result - Departments:', Department.objects.count(), 'Roles:', Role.objects.count())"
```

---

## ⚠️ **Alternative Solution**

If the above doesn't work, you can export directly in UTF-8 format:

### **Export with UTF-8 Encoding**

**On Windows (PowerShell)**:

```powershell
cd E:\EIMS2026

# Set environment to UTF-8
$env:PYTHONIOENCODING="utf-8"

# Export with explicit UTF-8
python -c "import json; from eims_app.models import Department; data = [{'model': 'eims_app.department', 'pk': d.id, 'fields': {f.name: getattr(d, f.name) for f in d._meta.fields}} for d in Department.objects.all()]; open('department_data_utf8.json', 'w', encoding='utf-8').write(json.dumps(data, indent=2, ensure_ascii=False))"
```

This is complex. **Better approach**: Use the manual import instructions below.

---

## 📋 **Manual Import Instructions**

### **Simple Method**

Since the automatic script has issues, use this simple manual process:

1. **SSH to server**:
   ```bash
   ssh root@39.106.41.239
   ```

2. **Fix encoding and import**:
   ```bash
   cd /var/www/eims
   source venv/bin/activate
   
   # Fix encoding
   python3 /root/fix_encoding.py
   
   # Import
   python manage.py loaddata /root/department_data.json
   python manage.py loaddata /root/role_data.json
   
   # Verify
   python manage.py shell -c "from eims_app.models import Department, Role; print('Departments:', Department.objects.count(), 'Roles:', Role.objects.count())"
   ```

---

## 🎯 **Summary**

### **What Happened**

✅ **Export successful** - Data exported correctly  
✅ **Upload successful** - Files on server  
❌ **Import failed** - Encoding mismatch (GBK vs UTF-8)  

---

### **Root Cause**

- Windows CMD uses **GBK encoding** for Chinese characters
- Django on Linux expects **UTF-8 encoding**
- JSON files contain Chinese text (部门名称，etc.)
- Linux Python cannot decode GBK-encoded JSON

---

### **Solution**

**Convert files to UTF-8 on the server**:

```bash
ssh root@39.106.41.239

# Run the fix script
python3 << 'EOF'
for filepath in ['/root/department_data.json', '/root/role_data.json']:
    try:
        with open(filepath, 'r', encoding='gbk') as f:
            content = f.read()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed: {filepath}')
    except Exception as e:
        print(f'Error: {filepath} - {e}')
EOF

# Import
cd /var/www/eims
source venv/bin/activate
python manage.py loaddata /root/department_data.json
python manage.py loaddata /root/role_data.json

# Check result
python manage.py shell -c "from eims_app.models import Department, Role; print('Success! Departments:', Department.objects.count(), 'Roles:', Role.objects.count())"
```

---

### **Expected Output**

```
Fixed: /root/department_data.json
Fixed: /root/role_data.json
Installed 10 object(s) from 1 fixture(s)
Installed 7 object(s) from 1 fixture(s)
Success! Departments: 10 Roles: 7
```

---

**Status**: ⚠️ Needs manual fix  
**Next Step**: SSH to server and run encoding fix  
**Time Required**: ~5 minutes

---

**Fix the encoding issue on the server, then import will work!** 🔧✨
