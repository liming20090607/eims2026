// 列宽拖动功能（复用所有列表，与list_mixin.html中的列表组件对应，所有模块列表共用）
document.addEventListener('DOMContentLoaded', function() {
    const headerCols = document.querySelectorAll('.list-header > div');
    const bodyRows = document.querySelectorAll('.list-row');
    
    headerCols.forEach((col, index) => {
        col.addEventListener('mousedown', function(e) {
            const startX = e.clientX;
            const startWidth = col.offsetWidth;
            const colIndex = index;

            function mouseMoveHandler(e) {
                const width = startWidth + (e.clientX - startX);
                col.style.width = `${width}px`;
                // 同步修改列表行对应列的宽度，确保表头与内容列宽一致
                bodyRows.forEach(row => {
                    const rowCol = row.children[colIndex];
                    rowCol.style.width = `${width}px`;
                });
            }

            function mouseUpHandler() {
                document.removeEventListener('mousemove', mouseMoveHandler);
                document.removeEventListener('mouseup', mouseUpHandler);
            }

            document.addEventListener('mousemove', mouseMoveHandler);
            document.addEventListener('mouseup', mouseUpHandler);
        });
    });
});