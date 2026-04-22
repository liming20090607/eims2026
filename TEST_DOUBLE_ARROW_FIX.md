# Quick Test Guide - Double Arrow & Sorting Fix

## What Was Fixed

1. ✅ **Double Arrows**: Removed duplicate arrow indicators (▲▼) - now shows single arrow
2. ⚠️ **Sorting Not Updating**: Added missing fields to database query - should now sort correctly

---

## How to Test

### Step 1: Clear Browser Cache
**IMPORTANT**: You MUST clear cache to see the changes!

**Option A - Hard Refresh (Recommended)**:
- Press `Ctrl + F5` while on the page
- Or `Ctrl + Shift + R`

**Option B - Incognito Window**:
- Open new incognito/private window
- Navigate to the page

**Option C - Clear Cache Manually**:
- Chrome: Settings → Privacy → Clear browsing data → Cached images and files
- Edge: Settings → Privacy → Clear browsing data

---

### Step 2: Test Single Arrow Display

1. Go to: http://127.0.0.1:8000/cost-consulting/project-info/
2. Click on any column header (e.g., "项目编号")
3. **Check**: 
   - ✅ Should show ONE arrow only (▲ or ▼)
   - ❌ Should NOT show both arrows (▲▼)
4. Click same header again
5. **Check**: Arrow direction changes, still single arrow

---

### Step 3: Test Sorting Actually Works

1. Note the current order of projects
2. Click "项目编号" header
3. **Check**:
   - ✅ Arrow appears (▲ for ascending, ▼ for descending)
   - ✅ Priority number "1" displays in blue badge
   - ✅ Table data REORDERS by project code
4. Click "项目名称" header
5. **Check**:
   - ✅ Both columns show arrows
   - ✅ "项目名称" shows priority "1"
   - ✅ "项目编号" shows priority "2"
   - ✅ Data sorts by name FIRST, then by code as tiebreaker

---

### Step 4: Check Terminal Output

Look at the terminal where Django server is running. After clicking sort headers, you should see messages like:

```
DEBUG SORT - sort_field: project_code, sort_order: asc
DEBUG SORT - Single-field order: project_code

DEBUG SORT - sort_field: project_name,project_code, sort_order: asc,asc
DEBUG SORT - Multi-field order: ['project_name', 'project_code']
```

If you see these messages, the backend is receiving sort parameters correctly.

---

## Expected Behavior

### Before Fix (What You Reported):
- ❌ Double arrows showing (▲▼)
- ❌ Priority numbers correct (1,2,3...) but data doesn't reorder

### After Fix (What You Should See):
- ✅ Single arrow showing (▲ OR ▼)
- ✅ Priority numbers correct (1,2,3...)
- ✅ Data actually reorders when you click headers
- ✅ Multi-field sorting works (last clicked = priority 1)

---

## If It Still Doesn't Work

### Problem: Still seeing double arrows
**Solution**: 
- Make sure you did a HARD refresh (Ctrl+F5)
- Check browser console for JavaScript errors (F12 → Console tab)
- Try different browser

### Problem: Sorting still not updating
**Solution**:
1. Check terminal for DEBUG SORT messages
2. If no messages appear, frontend isn't sending request
3. If messages appear but data doesn't change, check:
   - Browser Network tab (F12 → Network)
   - Look for the actual URL being requested
   - Verify it contains `sort_field=` and `sort_order=` parameters

### Problem: No DEBUG messages in terminal
**Solution**:
- The view might not be called
- Check if you're on the right URL
- Verify page reloads after clicking (URL should change)

---

## Files Modified

1. `eims_app/views/views_cost_sub_modules.py` - Added missing fields + debug logging
2. All 6 cost consulting list templates - Removed duplicate arrow code

---

## Server Status

✅ Django server running at: http://127.0.0.1:8000/
✅ No errors detected
✅ System check passed

---

## Need Help?

If issues persist after testing:
1. Take a screenshot of the problem
2. Copy any error messages from browser console (F12)
3. Share terminal output from Django server
4. Describe exact steps you took

---

*Test Date: March 21, 2026*
