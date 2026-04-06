# 📤 Upload Admin.py to Server - Manual Instructions

## ❗ Problem
The script failed because it couldn't find the file path.

## ✅ Solution: Manual Upload

### **Step 1: Open PowerShell or Command Prompt**

Press `Win + R`, type `cmd`, press Enter

### **Step 2: Navigate to EIMS2026 Directory**

```bash
cd E:\EIMS2026
```

### **Step 3: Upload admin.py to Server**

```bash
scp eims_app\admin.py root@39.106.41.239:/var/www/eims/eims_app/admin.py
```

**Enter password when prompted:** (your server password)

### **Step 4: SSH to Server**

```bash
ssh root@39.106.41.239
```

### **Step 5: Clear Python Cache**

```bash
cd /var/www/eims
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
echo "Cache cleared!"
```

### **Step 6: Restart Gunicorn**

```bash
supervisorctl restart eims
```

### **Step 7: Verify Installation**

```bash
grep -n "ImportExportModelAdmin" eims_app/admin.py
```

**You should see output like:**
```
17:    from import_export.admin import ImportExportModelAdmin
43:class ProjectAdmin(ImportExportModelAdmin if IMPORT_EXPORT_AVAILABLE else admin.ModelAdmin):
57:class EmployeeAdmin(ImportExportModelAdmin if IMPORT_EXPORT_AVAILABLE else admin.ModelAdmin):
77:class ContractAdmin(ImportExportModelAdmin if IMPORT_EXPORT_AVAILABLE else admin.ModelAdmin):
```

### **Step 8: Test in Browser**

1. Open browser
2. Press `Ctrl + F5` to hard refresh
3. Visit: `http://39.106.41.239:8000/admin/eims_app/employee/`
4. You should see **[导入]** button in the top right!

---

## 🚀 Quick Command Summary

Copy and paste these commands one by one:

```bash
# Upload file
scp eims_app\admin.py root@39.106.41.239:/var/www/eims/eims_app/admin.py

# SSH to server
ssh root@39.106.41.239

# Clear cache
cd /var/www/eims
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Restart
supervisorctl restart eims

# Verify
grep -n "ImportExportModelAdmin" eims_app/admin.py
```

---

## ✅ Success Indicators

After completing all steps, you should see:

1. ✓ Upload successful (no error messages)
2. ✓ Gunicorn restarted (shows "OK")
3. ✓ grep shows 4 lines with "ImportExportModelAdmin"
4. ✓ Browser shows [导入] button

---

## 💡 If Upload Still Fails

Try these alternatives:

### **Option 1: Use Full Path**

```bash
scp E:\EIMS2026\eims_app\admin.py root@39.106.41.239:/var/www/eims/eims_app/admin.py
```

### **Option 2: Use WinSCP or FileZilla**

1. Download WinSCP from https://winscp.net
2. Connect to: `39.106.41.239`
3. Username: `root`
4. Password: (your password)
5. Navigate to `/var/www/eims/eims_app/`
6. Drag and drop `admin.py` from local to server

### **Option 3: Copy via SSH**

```bash
# SSH to server
ssh root@39.106.41.239

# Create backup
cd /var/www/eims/eims_app
cp admin.py admin.py.backup

# Exit SSH
exit

# Then use SCP from step 3
```

---

## 🎯 Next Steps After Success

Once you see the [导入] button:

1. Click on **员工信息管理** (Employee Management)
2. Click **[导入]** button (top right)
3. Upload your Excel file
4. Preview data
5. Click **Submit** to import

---

**Need help? Run the fixed script:**
```
E:\EIMS2026\bat\upload-and-restart.bat
```

(The script now automatically changes to the correct directory)
