/**
 * EIMS 权限检查与提示系统
 * 用途：统一处理权限不足的情况，显示友好提示
 */

(function() {
    // 权限不足提示模态框 HTML
    const permissionDeniedModalHTML = `
        <div class="modal fade" id="permissionDeniedModal" tabindex="-1" aria-labelledby="permissionDeniedLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-danger">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title" id="permissionDeniedLabel">
                            <i class="bi bi-exclamation-triangle-fill"></i> 权限不足
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center py-4">
                        <i class="bi bi-lock-fill text-danger display-1 mb-3"></i>
                        <p class="lead fw-bold mb-3">权限不足，请于管理员联系！</p>
                        <p class="text-muted small">您需要相应的权限才能执行此操作</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // 未登录提示模态框 HTML
    const loginRequiredModalHTML = `
        <div class="modal fade" id="loginRequiredModal" tabindex="-1" aria-labelledby="loginRequiredLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-warning">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title" id="loginRequiredLabel">
                            <i class="bi bi-person-x-fill"></i> 未登录
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center py-4">
                        <i class="bi bi-person-x text-warning display-1 mb-3"></i>
                        <p class="lead fw-bold mb-3">用户未登录，请先登录！</p>
                        <p class="text-muted small">您需要登录后才能继续操作</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        <a href="/login/" class="btn btn-primary">去登录</a>
                    </div>
                </div>
            </div>
        </div>
    `;

    // 初始化模态框
    function initModals() {
        if (!document.getElementById('permissionDeniedModal')) {
            document.body.insertAdjacentHTML('beforeend', permissionDeniedModalHTML);
        }
        if (!document.getElementById('loginRequiredModal')) {
            document.body.insertAdjacentHTML('beforeend', loginRequiredModalHTML);
        }
    }

    // 显示权限不足提示
    window.showPermissionDenied = function() {
        initModals();
        const modal = new bootstrap.Modal(document.getElementById('permissionDeniedModal'));
        modal.show();
    };

    // 显示未登录提示
    window.showLoginRequired = function() {
        initModals();
        const modal = new bootstrap.Modal(document.getElementById('loginRequiredModal'));
        modal.show();
    };

    // 全局 AJAX 错误处理
    document.addEventListener('DOMContentLoaded', function() {
        // 拦截 fetch 请求
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            return originalFetch.apply(this, args).then(response => {
                // 检查 401 和 403 状态码
                if (response.status === 401) {
                    showLoginRequired();
                } else if (response.status === 403) {
                    showPermissionDenied();
                }
                return response;
            });
        };

        // 如果使用 jQuery，也拦截 jQuery AJAX
        if (window.jQuery) {
            $(document).ajaxError(function(event, jqxhr) {
                if (jqxhr.status === 401) {
                    showLoginRequired();
                } else if (jqxhr.status === 403) {
                    showPermissionDenied();
                }
            });
        }
    });

    // 页面加载时初始化
    initModals();

})();
