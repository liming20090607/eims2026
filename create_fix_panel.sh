#!/bin/bash
# Quick frontend panel setup

SERVER_PATH="/var/www/eims"

echo "Creating fix panel..."

# Create directory
mkdir -p $SERVER_PATH/templates/includes

# Create template file
cat > $SERVER_PATH/templates/includes/openclaw_fix_panel.html << 'TEMPLATE_EOF'
{% load static %}
<!-- OpenClaw Manual Fix Panel -->
<div id="openclaw-fix-panel" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); z-index:99999; background:white; border-radius:12px; box-shadow:0 10px 40px rgba(0,0,0,0.3); padding:40px; min-width:450px; max-width:600px; text-align:center;">
    <div style="font-size:64px; margin-bottom:20px;">🔧</div>
    <h2 style="margin:0 0 10px 0; color:#333; font-size:24px;">系统检测到错误</h2>
    <p style="color:#666; margin:0 0 30px 0; font-size:14px;">System Error Detected</p>
    
    <div style="background:#f0f0f0; border-radius:10px; height:30px; overflow:hidden; margin-bottom:20px; position:relative;">
        <div id="fix-progress-bar" style="background:linear-gradient(90deg, #667eea 0%, #764ba2 100%); height:100%; width:0%; transition:width 0.5s ease; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:14px;">
            0%
        </div>
    </div>
    
    <div id="fix-status-text" style="color:#667eea; font-size:16px; margin-bottom:30px; font-weight:500;">
        准备修复...
    </div>
    
    <div style="display:flex; gap:15px; justify-content:center;">
        <button id="btn-manual-fix" onclick="triggerManualFix()" style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; border:none; padding:12px 30px; border-radius:8px; font-size:16px; cursor:pointer; box-shadow:0 4px 15px rgba(102,126,234,0.4);">
            ⚡ 立即手动修复
        </button>
        <button id="btn-refresh-page" onclick="location.reload()" style="background:#f0f0f0; color:#333; border:2px solid #ddd; padding:12px 30px; border-radius:8px; font-size:16px; cursor:pointer;">
            🔄 刷新页面
        </button>
    </div>
    
    <div style="margin-top:20px; color:#999; font-size:12px;">
        💡 提示：系统将每2秒自动刷新，最多尝试30次
    </div>
</div>

<script>
let refreshCount = 0;
const maxRefreshes = 30;
let isFixing = false;

window.addEventListener('load', function() {
    const isErrorPage = document.title.includes('错误') || 
                       document.title.includes('Error') ||
                       document.body.innerHTML.includes('OperationalError') ||
                       document.body.innerHTML.includes('DatabaseError');
    
    if (isErrorPage) {
        showFixPanel();
        startAutoRefresh();
    }
});

function showFixPanel() {
    document.getElementById('openclaw-fix-panel').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function updateProgress(percent, statusText) {
    const bar = document.getElementById('fix-progress-bar');
    const text = document.getElementById('fix-status-text');
    bar.style.width = percent + '%';
    bar.textContent = percent + '%';
    text.textContent = statusText;
}

async function triggerManualFix() {
    if (isFixing) return;
    isFixing = true;
    
    const btn = document.getElementById('btn-manual-fix');
    btn.disabled = true;
    btn.style.opacity = '0.6';
    btn.textContent = '⏳ 修复中...';
    
    try {
        updateProgress(10, '正在触发修复...');
        
        const response = await fetch('/openclaw/api/trigger-fix/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        updateProgress(30, '修复脚本已启动...');
        
        let pollCount = 0;
        const pollInterval = setInterval(async () => {
            pollCount++;
            
            try {
                const statusResp = await fetch('/openclaw/api/status/');
                const status = await statusResp.json();
                
                if (status.mysql === 'OK' || status.mysql === 'FIXED') {
                    updateProgress(100, '✅ 修复成功！');
                    clearInterval(pollInterval);
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                } else if (pollCount > 30) {
                    updateProgress(100, '⚠️ 修复超时，请刷新页面');
                    clearInterval(pollInterval);
                    btn.disabled = false;
                    btn.style.opacity = '1';
                    btn.textContent = '⚡ 再次尝试修复';
                } else {
                    const progress = 30 + (pollCount * 2);
                    updateProgress(Math.min(progress, 90), '修复进行中... (' + pollCount + '/30)');
                }
            } catch (e) {
                console.error('Status check failed:', e);
            }
        }, 2000);
        
    } catch (error) {
        console.error('Fix trigger failed:', error);
        updateProgress(0, '❌ 触发失败，请重试');
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.textContent = '⚡ 立即手动修复';
        isFixing = false;
    }
}

function startAutoRefresh() {
    const refreshInterval = setInterval(() => {
        refreshCount++;
        
        const statusText = document.getElementById('fix-status-text');
        if (statusText && !isFixing) {
            statusText.textContent = `自动刷新中... ${refreshCount}/${maxRefreshes}`;
        }
        
        fetch('/openclaw/api/status/')
            .then(resp => resp.json())
            .then(status => {
                if (status.mysql === 'OK' && status.http_code === '200') {
                    clearInterval(refreshInterval);
                    updateProgress(100, '✅ 系统已恢复！');
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                }
            })
            .catch(err => {
                console.log('Still checking...', err);
            });
        
        if (refreshCount >= maxRefreshes) {
            clearInterval(refreshInterval);
            const statusText = document.getElementById('fix-status-text');
            if (statusText) {
                statusText.textContent = '⚠️ 自动刷新已达上限，请手动修复或刷新';
            }
        }
    }, 2000);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
</script>
<!-- End OpenClaw Fix Panel -->
TEMPLATE_EOF

echo "Template created: $(test -f $SERVER_PATH/templates/includes/openclaw_fix_panel.html && echo 'YES' || echo 'NO')"
