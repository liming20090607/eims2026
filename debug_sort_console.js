/**
 * 排序功能诊断和修复脚本
 * 
 * 使用方法：
 * 1. 打开项目信息列表页面
 * 2. 按 F12 打开开发者工具
 * 3. 切换到 Console 标签
 * 4. 复制粘贴此文件的所有内容到Console
 * 5. 按 Enter 执行
 */

(function() {
    console.log('%c=== 排序功能诊断工具 ===', 'color: #0d6efd; font-size: 16px; font-weight: bold;');
    console.log('');

    // 检查1: 变量是否存在
    console.log('%c[检查1] 变量状态', 'color: #28a745; font-weight: bold;');
    if (typeof sortFields !== 'undefined') {
        console.log('✓ sortFields:', sortFields);
    } else {
        console.error('✗ sortFields 未定义！');
    }
    
    if (typeof sortOrders !== 'undefined') {
        console.log('✓ sortOrders:', sortOrders);
    } else {
        console.error('✗ sortOrders 未定义！');
    }
    console.log('');

    // 检查2: 函数是否存在
    console.log('%c[检查2] 函数状态', 'color: #28a745; font-weight: bold;');
    const functions = ['handleSort', 'updateSortDisplay', 'initSortState', 'updateSortUrl'];
    functions.forEach(func => {
        if (typeof window[func] === 'function') {
            console.log(`✓ ${func}() 存在`);
        } else {
            console.error(`✗ ${func}() 不存在！`);
        }
    });
    console.log('');

    // 检查3: DOM元素
    console.log('%c[检查3] DOM元素', 'color: #28a745; font-weight: bold;');
    const sortableThs = document.querySelectorAll('th.sortable');
    console.log(`✓ 可排序表头数量: ${sortableThs.length}`);
    
    const prioritySpans = document.querySelectorAll('.sort-priority');
    console.log(`✓ 优先级徽章数量: ${prioritySpans.length}`);
    
    const directionSpans = document.querySelectorAll('.sort-direction');
    console.log(`✓ 方向箭头数量: ${directionSpans.length}`);
    console.log('');

    // 检查4: 表头属性
    console.log('%c[检查4] 表头属性检查（前3个）', 'color: #28a745; font-weight: bold;');
    sortableThs.forEach((th, index) => {
        if (index < 3) {
            const field = th.getAttribute('data-field');
            const onclick = th.getAttribute('onclick');
            console.log(`  表头${index + 1}: data-field="${field}", onclick="${onclick}"`);
        }
    });
    console.log('');

    // 检查5: 当前URL参数
    console.log('%c[检查5] URL参数', 'color: #28a745; font-weight: bold;');
    const url = new URL(window.location.href);
    const sortField = url.searchParams.get('sort_field');
    const sortOrder = url.searchParams.get('sort_order');
    console.log(`  sort_field: ${sortField || '(无)'}`);
    console.log(`  sort_order: ${sortOrder || '(无)'}`);
    console.log('');

    // 自动修复尝试
    console.log('%c[自动修复]', 'color: #ffc107; font-weight: bold;');
    
    try {
        // 如果变量未定义，手动初始化
        if (typeof sortFields === 'undefined' || typeof sortOrders === 'undefined') {
            console.log('⚠ 检测到变量未定义，正在初始化...');
            window.sortFields = ['created_at'];
            window.sortOrders = ['desc'];
            console.log('✓ 已初始化 sortFields 和 sortOrders');
        }
        
        // 强制更新显示
        if (typeof updateSortDisplay === 'function') {
            console.log('⚠ 强制更新排序显示...');
            updateSortDisplay();
            console.log('✓ 已调用 updateSortDisplay()');
        }
        
        // 检查是否有显示
        const visiblePriorities = Array.from(prioritySpans).filter(span => 
            span.textContent && span.textContent.trim() !== ''
        );
        
        if (visiblePriorities.length > 0) {
            console.log(`%c✓ 成功！找到 ${visiblePriorities.length} 个可见的优先级数字`, 'color: #28a745; font-weight: bold;');
            visiblePriorities.forEach(span => {
                console.log(`  - "${span.textContent}" (字段: ${span.parentElement.getAttribute('data-field')})`);
            });
        } else {
            console.warn('⚠ 仍未找到可见的优先级数字');
            console.log('💡 建议操作：');
            console.log('   1. 点击任意表头触发排序');
            console.log('   2. 硬刷新页面 (Ctrl+F5)');
            console.log('   3. 清除浏览器缓存');
        }
        
    } catch (error) {
        console.error('✗ 自动修复失败:', error);
    }
    
    console.log('');
    console.log('%c=== 诊断完成 ===', 'color: #0d6efd; font-size: 16px; font-weight: bold;');
    console.log('');
    console.log('💡 提示：如果看到错误，请截图发送给技术支持');
    console.log('💡 提示：点击任意表头测试排序功能是否正常');
    
})();
