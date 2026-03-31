// colResizable - 简单可靠的列宽拖动
(function() {
    'use strict';
    
    function initResizableColumns(tableId) {
        var table = document.getElementById(tableId);
        if (!table) return;
        
        var thead = table.querySelector('thead');
        if (!thead) return;
        
        var ths = thead.querySelectorAll('th');
        
        ths.forEach(function(th, index) {
            if (index === ths.length - 1) return;
            
            var grip = document.createElement('div');
            grip.className = 'col-grip';
            grip.innerHTML = '⋮';
            grip.style.cssText = 'position:absolute;right:-2px;top:0;bottom:0;width:6px;cursor:col-resize;' +
                'display:flex;align-items:center;justify-content:center;color:#adb5bd;font-size:12px;' +
                'z-index:10;transition:background 0.2s;';
            
            grip.addEventListener('mouseenter', function() {
                grip.style.background = '#0d6efd';
                grip.style.color = '#fff';
            });
            grip.addEventListener('mouseleave', function() {
                grip.style.background = 'transparent';
                grip.style.color = '#adb5bd';
            });
            
            th.style.position = 'relative';
            th.style.verticalAlign = 'middle';
            th.appendChild(grip);
            
            var startX = 0;
            var startWidth = 0;
            var isDragging = false;
            
            grip.addEventListener('mousedown', function(e) {
                e.preventDefault();
                e.stopPropagation();
                isDragging = true;
                startX = e.pageX;
                startWidth = th.offsetWidth;
                grip.style.background = '#0d6efd';
                grip.style.color = '#fff';
            });
            
            document.addEventListener('mousemove', function(e) {
                if (!isDragging) return;
                
                var diff = e.pageX - startX;
                th.style.width = Math.max(40, startWidth + diff) + 'px';
            });
            
            document.addEventListener('mouseup', function() {
                if (isDragging) {
                    isDragging = false;
                    grip.style.background = 'transparent';
                    grip.style.color = '#adb5bd';
                }
            });
        });
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initResizableColumns('contract-table');
            initResizableColumns('project-table');
        });
    } else {
        initResizableColumns('contract-table');
        initResizableColumns('project-table');
    }
})();
