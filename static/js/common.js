// 返回上级，对应base.html中的返回按钮，所有页面共用
function goBack() {
    window.history.back();
}

// 返回主页（修正：跳转到仪表盘首页，对应urls.py中的根路由，与dashboard.html对应，根目录为/e/EIMS/，路由无需额外调整）
function goHome() {
    window.location.href = "/"; // 与主页路由一致，无需修改
}

// 全选/取消全选，对应list_mixin.html中的复选框，所有模块列表共用
function selectAllRows() {
    const selectAll = document.getElementById('selectAll');
    const rowChecks = document.querySelectorAll('.row-check');
    rowChecks.forEach(check => {
        check.checked = selectAll.checked;
    });
}

// 打开弹窗，对应list_mixin.html中的弹窗容器，所有模块共用
function openModal() {
    document.getElementById('modalContainer').style.display = 'flex';
}

// 关闭弹窗，对应list_mixin.html中的弹窗容器，所有模块共用
function closeModal() {
    document.getElementById('modalContainer').style.display = 'none';
}

// 打开详情页，对应list_mixin.html中的详情容器，所有模块共用
function openDetail(id) {
    // 实际项目中可通过id请求详情数据
    document.getElementById('detailContainer').style.display = 'block';
}

// 关闭详情页，对应list_mixin.html中的详情容器，所有模块共用
function closeDetail() {
    document.getElementById('detailContainer').style.display = 'none';
}

// 新增：仪表盘模块跳转（点击模块卡片跳转到对应列表页，与dashboard.html中的模块卡片对应，路由与urls.py一致）
function goToModule(url) {
    window.location.href = url;
}