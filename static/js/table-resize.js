// 表格列宽拖动 - 支持所有表格
document.addEventListener('DOMContentLoaded', function() {
    var dragging = null;
    var startX = 0;
    var startWidth = 0;
    
    function initTable(tableId) {
        var table = document.getElementById(tableId);
        if (!table) return;
        
        var thead = table.querySelector('thead');
        if (!thead) return;
        
        var ths = thead.querySelectorAll('th');
        
        ths.forEach(function(th, index) {
            if (index === ths.length - 1) return;
            
            th.style.position = 'relative';
            
            var grip = document.createElement('div');
            grip.className = 'col-grip';
            grip.innerHTML = '⋮';
            grip.style.cssText = 'position:absolute;right:-2px;top:0;bottom:0;width:8px;cursor:col-resize;' +
                'display:flex;align-items:center;justify-content:center;color:#adb5bd;font-size:14px;' +
                'z-index:10;transition:background 0.2s;user-select:none;';
            
            grip.addEventListener('mouseenter', function() {
                grip.style.background = '#0d6efd';
                grip.style.color = '#fff';
            });
            grip.addEventListener('mouseleave', function() {
                grip.style.background = 'transparent';
                grip.style.color = '#adb5bd';
            });
            
            grip.addEventListener('mousedown', function(e) {
                e.preventDefault();
                e.stopPropagation();
                dragging = th;
                startX = e.clientX;
                startWidth = th.offsetWidth;
                grip.style.background = '#0d6efd';
                grip.style.color = '#fff';
            });
            
            th.appendChild(grip);
        });
    }
    
    initTable('contract-table');
    initTable('project-table');
    initTable('dynamics-table');
    initTable('output-table');
    initTable('personnel-table');
    
    document.addEventListener('mousemove', function(e) {
        if (dragging) {
            var diff = e.clientX - startX;
            dragging.style.width = Math.max(40, startWidth + diff) + 'px';
        }
    });
    
    document.addEventListener('mouseup', function() {
        dragging = null;
    });
});
