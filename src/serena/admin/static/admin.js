/**
 * Serena Admin Dashboard JavaScript
 */

// 项目操作
function activateProject(name) {
    if (confirm(`确定要激活项目 "${name}" 吗？`)) {
        fetch('/admin/projects/activate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_name: name })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('success', data.message);
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast('error', data.message);
            }
        })
        .catch(error => {
            showToast('error', '网络错误，请稍后重试');
            console.error('Error:', error);
        });
    }
}

function editProject(name) {
    // This will be implemented in task 10 (project editing)
    window.location.href = `/admin/projects/${name}/edit`;
}

function deleteProject(name) {
    if (confirm(`确定要删除项目 "${name}" 吗？此操作不可撤销。`)) {
        fetch('/admin/projects/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_name: name })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('success', data.message);
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast('error', data.message);
            }
        })
        .catch(error => {
            showToast('error', '网络错误，请稍后重试');
            console.error('Error:', error);
        });
    }
}

// Toast 通知系统
let toastContainer = null;
let toastCounter = 0;

function showToast(type, message, options = {}) {
    // 确保存在 toast 容器
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }

    // 创建 toast 元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.id = `toast-${++toastCounter}`;
    
    // 设置内容
    const icon = getToastIcon(type);
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-content">
            <div class="toast-message">${escapeHtml(message)}</div>
        </div>
        <button class="toast-close" onclick="closeToast('${toast.id}')">&times;</button>
    `;
    
    // 添加到容器
    toastContainer.appendChild(toast);
    
    // 触发进入动画
    requestAnimationFrame(() => {
        toast.classList.add('toast-show');
    });
    
    // 自动关闭
    const duration = options.duration || 3000;
    if (duration > 0) {
        setTimeout(() => {
            closeToast(toast.id);
        }, duration);
    }
    
    return toast.id;
}

function closeToast(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.classList.remove('toast-show');
        toast.classList.add('toast-hide');
        
        // 等待动画结束后移除元素
        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
        }, 300);
    }
}

function getToastIcon(type) {
    const icons = {
        success: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM8 15L3 10L4.41 8.59L8 12.17L15.59 4.58L17 6L8 15Z" fill="currentColor"/></svg>',
        error: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V13H11V15ZM11 11H9V5H11V11Z" fill="currentColor"/></svg>',
        warning: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M1 17H19L10 2L1 17ZM11 14H9V12H11V14ZM11 10H9V6H11V10Z" fill="currentColor"/></svg>',
        info: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V9H11V15ZM11 7H9V5H11V7Z" fill="currentColor"/></svg>'
    };
    return icons[type] || icons.info;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 加载当前活跃项目
    loadActiveProject();
});

function loadActiveProject() {
    const activeProjectEl = document.getElementById('active-project');
    if (activeProjectEl) {
        fetch('/admin/api/active-project')
            .then(response => response.json())
            .then(data => {
                if (data.project_name) {
                    activeProjectEl.textContent = `活跃项目: ${data.project_name}`;
                } else {
                    activeProjectEl.textContent = '无活跃项目';
                }
            })
            .catch(error => {
                console.error('Error loading active project:', error);
                activeProjectEl.textContent = '加载失败';
            });
    }
}
