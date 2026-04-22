import re
from django.conf import settings

class AutoRefreshMiddleware:
    """Auto-refresh and manual fix button middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        if response.get('Content-Type', '').startswith('text/html'):
            content = response.content.decode('utf-8')
            
            is_error_page = (
                'error-container' in content or
                'OperationalError' in content or
                'Internal Server Error' in content or
                'Access denied' in content or
                response.status_code >= 500
            )
            
            if is_error_page:
                fix_button_html = """
<div id="emergency-fix-panel" style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:40px;border-radius:16px;box-shadow:0 10px 40px rgba(0,0,0,0.3);z-index:10000;text-align:center;max-width:500px;width:90%;">
    <div style="font-size:64px;margin-bottom:20px;">&#128295;</div>
    <h2 style="color:#d32f2f;margin-bottom:15px;font-size:24px;">System Error Detected</h2>
    <p style="color:#666;margin-bottom:25px;font-size:16px;">Database connection error detected. Auto-fixing...</p>
    
    <div id="fix-progress" style="margin-bottom:25px;">
        <div style="background:#e0e0e0;border-radius:10px;height:30px;overflow:hidden;margin-bottom:10px;">
            <div id="progress-bar" style="background:linear-gradient(90deg,#4CAF50,#8BC34A);height:100%;width:0%;transition:width 0.5s;border-radius:10px;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:14px;">
                0%
            </div>
        </div>
        <p id="progress-text" style="color:#666;font-size:14px;margin:0;">Fixing...</p>
    </div>
    
    <div style="display:flex;gap:15px;justify-content:center;margin-bottom:20px;">
        <button onclick="triggerManualFix()" style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border:none;padding:15px 30px;border-radius:8px;font-size:16px;cursor:pointer;box-shadow:0 4px 15px rgba(102,126,234,0.4);transition:all 0.3s;font-weight:bold;">
            &#9889; Manual Fix Now
        </button>
        <button onclick="location.reload()" style="background:#f5f5f5;color:#333;border:2px solid #ddd;padding:15px 30px;border-radius:8px;font-size:16px;cursor:pointer;transition:all 0.3s;font-weight:bold;">
            &#128260; Refresh Page
        </button>
    </div>
    
    <p style="color:#999;font-size:12px;margin:0;">
        &#128161; OpenClaw will auto-fix in 30-60 seconds
    </p>
</div>

<div id="fix-overlay" style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);z-index:9999;"></div>

<script>
(function() {
    var refreshCount = 0;
    var maxRefreshes = 30;
    var refreshInterval = 2000;
    var isFixing = false;
    
    function updateProgress(percent, text) {
        var bar = document.getElementById('progress-bar');
        var txt = document.getElementById('progress-text');
        if (bar) {
            bar.style.width = percent + '%';
            bar.textContent = percent + '%';
        }
        if (txt) {
            txt.textContent = text;
        }
    }
    
    window.triggerManualFix = function() {
        if (isFixing) return;
        isFixing = true;
        
        updateProgress(10, 'Connecting to server...');
        
        fetch('/openclaw/api/trigger-fix/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (data.status === 'success') {
                updateProgress(50, 'Fix script started, waiting...');
                
                var checkInterval = setInterval(function() {
                    fetch('/openclaw/api/check-status/')
                    .then(function(r) { return r.json(); })
                    .then(function(status) {
                        if (status.mysql === 'OK' || status.mysql === 'FIXED') {
                            clearInterval(checkInterval);
                            updateProgress(100, 'Fixed! Redirecting...');
                            setTimeout(function() {
                                window.location.href = '/login/';
                            }, 1000);
                        } else {
                            updateProgress(75, 'Fixing, please wait...');
                        }
                    })
                    .catch(function() {});
                }, 2000);
            } else {
                updateProgress(0, 'Failed, please retry');
                isFixing = false;
            }
        })
        .catch(function(error) {
            updateProgress(0, 'Network error, please retry');
            isFixing = false;
        });
    };
    
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    var refreshTimer = setInterval(function() {
        refreshCount++;
        
        if (refreshCount <= maxRefreshes) {
            updateProgress(Math.min(refreshCount * 3, 90), 'Auto-fixing (' + refreshCount + '/' + maxRefreshes + ')...');
            
            var hasError = document.querySelector('.error-container') || 
                          document.querySelector('h1')?.textContent?.includes('Error') ||
                          document.querySelector('h1')?.textContent?.includes('error');
            
            if (!hasError && refreshCount > 2) {
                clearInterval(refreshTimer);
                updateProgress(100, 'System restored! Redirecting...');
                setTimeout(function() {
                    window.location.href = '/login/';
                }, 1000);
            } else if (refreshCount >= maxRefreshes) {
                clearInterval(refreshTimer);
                updateProgress(100, 'Auto-fix incomplete, click Manual Fix');
            }
            
            setTimeout(function() {
                location.reload();
            }, 500);
        }
    }, refreshInterval);
    
    updateProgress(10, 'Error detected, starting auto-fix...');
})();
</script>
"""
                
                if '<body>' in content:
                    content = content.replace('<body>', '<body>' + fix_button_html, 1)
                else:
                    content = fix_button_html + content
                
                response.content = content.encode('utf-8')
                if 'Content-Length' in response:
                    del response['Content-Length']
        
        return response
