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

// Toast 通知
function showToast(type, message) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
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
