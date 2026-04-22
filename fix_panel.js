# Fix Panel JavaScript
var fixPanelJS = """
(function() {
    var hasError = document.body.innerHTML.indexOf('OperationalError') !== -1 || 
                   document.body.innerHTML.indexOf('DatabaseError') !== -1;
    if (!hasError) return;
    
    var panel = document.getElementById('openclaw-fix-panel');
    if (panel) panel.style.display = 'block';
    
    var btnRefresh = document.getElementById('btn-refresh');
    var btnFix = document.getElementById('btn-fix');
    
    if (btnRefresh) {
        btnRefresh.addEventListener('click', function() {
            window.location.reload();
        });
    }
    
    if (btnFix) {
        btnFix.addEventListener('click', function() {
            var btn = this;
            var bar = document.getElementById('fix-progress-bar');
            var status = document.getElementById('fix-status');
            btn.disabled = true;
            btn.textContent = 'Fixing...';
            
            fetch('/openclaw/api/trigger-fix/')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.success) {
                        status.textContent = 'Fix triggered! Monitoring...';
                        bar.style.width = '20%';
                        
                        var count = 0;
                        var timer = setInterval(function() {
                            count++;
                            bar.style.width = Math.min(20 + (count/30)*80, 100) + '%';
                            status.textContent = 'Checking... ' + count + '/30';
                            
                            fetch('/openclaw/api/status/')
                                .then(function(r) { return r.json(); })
                                .then(function(s) {
                                    if (s.mysql === 'OK' || s.mysql === 'FIXED') {
                                        clearInterval(timer);
                                        bar.style.width = '100%';
                                        status.textContent = 'Fixed! Refreshing...';
                                        setTimeout(function() { window.location.reload(); }, 2000);
                                    }
                                    if (count >= 30) {
                                        clearInterval(timer);
                                        status.textContent = 'Please refresh manually';
                                        btn.disabled = false;
                                        btn.textContent = 'Retry';
                                    }
                                });
                        }, 2000);
                    } else {
                        status.textContent = 'Error: ' + (data.error || 'Unknown');
                        btn.disabled = false;
                        btn.textContent = 'Retry';
                    }
                })
                .catch(function() {
                    status.textContent = 'Network error';
                    btn.disabled = false;
                    btn.textContent = 'Retry';
                });
        });
    }
    
    var autoCount = 0;
    var autoTimer = setInterval(function() {
        autoCount++;
        if (autoCount > 20) { clearInterval(autoTimer); return; }
        window.location.reload();
    }, 3000);
})();
"""
