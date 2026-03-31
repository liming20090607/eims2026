document.addEventListener('DOMContentLoaded', function() {
    // 1. 列宽拖动功能
    initResizableTable();
    // 2. 批量选择功能
    initBatchSelect();
    // 3. 自动换行适配
    initAutoWrap();
});

// 列宽拖动初始化
function initResizableTable() {
    const tables = document.querySelectorAll('.resizable-table');
    tables.forEach(table => {
        const ths = table.querySelectorAll('.resizable-th');
        ths.forEach(th => {
            const handle = document.createElement('div');
            handle.className = 'resizable-handle';
            th.appendChild(handle);

            let startX, startWidth;
            const startResize = (e) => {
                startX = e.pageX;
                startWidth = th.offsetWidth;
                document.addEventListener('mousemove', resize);
                document.addEventListener('mouseup', stopResize);
            };

            const resize = (e) => {
                const width = startWidth + (e.pageX - startX);
                if (width > 80) { // 最小列宽80px
                    th.style.width = `${width}px`;
                    th.style.minWidth = `${width}px`;
                }
            };

            const stopResize = () => {
                document.removeEventListener('mousemove', resize);
                document.removeEventListener('mouseup', stopResize);
            };

            handle.addEventListener('mousedown', startResize);
        });
    });
}

// 批量选择初始化
function initBatchSelect() {
    const selectAll = document.getElementById('select-all');
    if (!selectAll) return;

    const checkboxes = document.querySelectorAll('.table-checkbox');
    // 全选/取消全选
    selectAll.addEventListener('change', function() {
        checkboxes.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
        updateBatchButtonStatus();
    });

    // 单个选择
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateBatchButtonStatus);
    });

    // 更新批量按钮状态
    function updateBatchButtonStatus() {
        const checkedCount = document.querySelectorAll('.table-checkbox:checked').length;
        const batchButtons = document.querySelectorAll('.batch-btn');
        batchButtons.forEach(btn => {
            btn.disabled = checkedCount === 0;
            btn.style.opacity = checkedCount === 0 ? '0.5' : '1';
        });
    }
}

// 自动换行初始化
function initAutoWrap() {
    const wrapCells = document.querySelectorAll('.table-cell-wrap');
    wrapCells.forEach(cell => {
        // 根据内容长度调整高度
        cell.style.height = 'auto';
        cell.style.minHeight = '40px';
    });
} 
