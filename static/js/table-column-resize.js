/**
 * 表格列宽拖拽调整功能
 * 支持所有列表表格的列宽拖动，单元格内容自动换行，行高自适应
 */

(function() {
    'use strict';
    
    // 初始化所有可调整列宽的表格
    function initAllTables() {
        const tables = document.querySelectorAll('.table');
        tables.forEach(function(table) {
            if (!table.hasAttribute('data-resizable-initialized')) {
                makeTableResizable(table);
                table.setAttribute('data-resizable-initialized', 'true');
            }
        });
    }
    
    // 使表格可调整列宽
    function makeTableResizable(table) {
        const thead = table.querySelector('thead');
        if (!thead) return;
        
        const headers = thead.querySelectorAll('th');
        
        // 为每个表头（除了最后一列）添加拖拽手柄
        headers.forEach(function(th, index) {
            if (index < headers.length - 1) {
                addResizeHandle(th, table);
            }
            
            // 设置表头样式：允许内容换行
            th.style.whiteSpace = 'normal';
            th.style.wordWrap = 'break-word';
            th.style.verticalAlign = 'middle';
            th.style.padding = '8px';
        });
        
        // 设置表格样式
        table.style.tableLayout = 'auto';
        table.style.width = '100%';
        
        // 设置所有单元格允许换行
        const cells = table.querySelectorAll('td');
        cells.forEach(function(td) {
            td.style.whiteSpace = 'normal';
            td.style.wordWrap = 'break-word';
            td.style.overflowWrap = 'break-word';
            td.style.verticalAlign = 'top';
            td.style.padding = '8px';
        });
    }
    
    // 为表头添加拖拽手柄
    function addResizeHandle(th, table) {
        // 创建拖拽手柄
        const handle = document.createElement('div');
        handle.className = 'col-resize-handle';
        handle.style.cssText = `
            position: absolute;
            right: 0;
            top: 0;
            bottom: 0;
            width: 5px;
            cursor: col-resize;
            background: transparent;
            z-index: 10;
            transition: background-color 0.2s;
        `;
        
        // 鼠标悬停效果
        handle.addEventListener('mouseenter', function() {
            this.style.background = 'rgba(13, 110, 253, 0.5)';
        });
        
        handle.addEventListener('mouseleave', function() {
            if (!this.classList.contains('dragging')) {
                this.style.background = 'transparent';
            }
        });
        
        // 拖拽开始
        let startX = 0;
        let startWidth = 0;
        let isDragging = false;
        
        handle.addEventListener('mousedown', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            isDragging = true;
            this.classList.add('dragging');
            this.style.background = '#0d6efd';
            
            startX = e.pageX;
            startWidth = th.offsetWidth;
            
            // 添加全局事件监听
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
            
            // 防止文本选择
            document.body.style.userSelect = 'none';
            document.body.style.cursor = 'col-resize';
        });
        
        const onMouseMove = function(e) {
            if (!isDragging) return;
            
            const diff = e.pageX - startX;
            const newWidth = Math.max(40, startWidth + diff);
            
            th.style.width = newWidth + 'px';
            th.style.minWidth = newWidth + 'px';
            
            // 更新同列的所有单元格宽度
            const cellIndex = Array.from(th.parentNode.children).indexOf(th);
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(function(row) {
                const cell = row.children[cellIndex];
                if (cell) {
                    cell.style.width = newWidth + 'px';
                    cell.style.minWidth = newWidth + 'px';
                }
            });
        };
        
        const onMouseUp = function() {
            if (isDragging) {
                isDragging = false;
                handle.classList.remove('dragging');
                handle.style.background = 'transparent';
                
                // 移除全局事件监听
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
                
                // 恢复文本选择和光标
                document.body.style.userSelect = '';
                document.body.style.cursor = '';
                
                // 触发行高重新计算
                adjustRowHeights(table);
            }
        };
        
        // 将手柄添加到表头
        th.style.position = 'relative';
        th.appendChild(handle);
    }
    
    // 调整所有行的行高以适应内容
    function adjustRowHeights(table) {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(function(row) {
            // 重置行高，让浏览器自动计算
            row.style.height = 'auto';
            
            // 获取当前行高
            const computedHeight = row.offsetHeight;
            
            // 检查是否有单元格内容溢出
            const cells = row.querySelectorAll('td');
            let needsAdjustment = false;
            
            cells.forEach(function(cell) {
                if (cell.scrollHeight > cell.clientHeight) {
                    needsAdjustment = true;
                }
            });
            
            // 如果需要调整，设置最小高度
            if (needsAdjustment) {
                row.style.minHeight = computedHeight + 'px';
            }
        });
    }
    
    // 当页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(initAllTables, 100);
        });
    } else {
        setTimeout(initAllTables, 100);
    }
    
    // 暴露全局函数，供动态加载的内容调用
    window.initTableResize = function(tableElement) {
        if (tableElement) {
            makeTableResizable(tableElement);
            tableElement.setAttribute('data-resizable-initialized', 'true');
        } else {
            initAllTables();
        }
    };
    
    // 监听DOM变化，自动初始化新添加的表格
    if (window.MutationObserver) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        if (node.tagName === 'TABLE' && node.classList.contains('table')) {
                            makeTableResizable(node);
                            node.setAttribute('data-resizable-initialized', 'true');
                        }
                        // 检查子元素中的表格
                        const tables = node.querySelectorAll ? node.querySelectorAll('table.table') : [];
                        tables.forEach(function(table) {
                            if (!table.hasAttribute('data-resizable-initialized')) {
                                makeTableResizable(table);
                                table.setAttribute('data-resizable-initialized', 'true');
                            }
                        });
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
})();
