/**
 * Serena Admin Dashboard JavaScript
 */

// 全局配置
const CONFIG = {
    toastDuration: 3000,
    animationDuration: 300,
    debounceDelay: 300
};

// 状态管理
const state = {
    isLoading: false,
    activeProject: null,
    toasts: []
};

// 工具函数：防抖
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 工具函数：节流
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 显示/隐藏加载状态
function setLoading(buttonElement, loading) {
    if (!buttonElement) return;

    if (loading) {
        buttonElement.classList.add('loading');
        buttonElement.disabled = true;
        const originalText = buttonElement.textContent;
        buttonElement.dataset.originalText = originalText;
        buttonElement.innerHTML = '<span class="spinner"></span>';
    } else {
        buttonElement.classList.remove('loading');
        buttonElement.disabled = false;
        const originalText = buttonElement.dataset.originalText;
        if (originalText) {
            buttonElement.textContent = originalText;
            delete buttonElement.dataset.originalText;
        }
    }
}

// 创建加载遮罩
function showLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'global-loading-overlay';
    overlay.innerHTML = '<div class="spinner spinner-lg"></div>';
    document.body.appendChild(overlay);
    return overlay;
}

// 移除加载遮罩
function hideLoadingOverlay() {
    const overlay = document.getElementById('global-loading-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => overlay.remove(), CONFIG.animationDuration);
    }
}

// 项目操作
function activateProject(name, buttonElement) {
    if (confirm(`确定要激活项目 "${name}" 吗？`)) {
        setLoading(buttonElement, true);

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
                setLoading(buttonElement, false);
            }
        })
        .catch(error => {
            showToast('error', '网络错误，请稍后重试');
            console.error('Error:', error);
            setLoading(buttonElement, false);
        });
    }
}

function editProject(name) {
    window.location.href = `/admin/projects/${name}/edit`;
}

function deleteProject(name, buttonElement) {
    if (confirm(`确定要删除项目 "${name}" 吗？此操作不可撤销。`)) {
        setLoading(buttonElement, true);

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
                setLoading(buttonElement, false);
            }
        })
        .catch(error => {
            showToast('error', '网络错误，请稍后重试');
            console.error('Error:', error);
            setLoading(buttonElement, false);
        });
    }
}

// Toast 通知系统
class ToastManager {
    constructor() {
        this.container = null;
        this.counter = 0;
        this.toasts = new Map();
        this.maxToasts = 5;
    }

    ensureContainer() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
        return this.container;
    }

    show(type, message, options = {}) {
        const container = this.ensureContainer();

        // 如果 toast 太多，移除最旧的
        if (this.toasts.size >= this.maxToasts) {
            const oldestToast = this.toasts.keys().next().value;
            this.close(oldestToast);
        }

        // 创建 toast 元素
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        const toastId = `toast-${++this.counter}`;
        toast.id = toastId;

        // 设置内容
        const icon = this.getIcon(type);
        const title = options.title || this.getDefaultTitle(type);
        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${escapeHtml(title)}</div>` : ''}
                <div class="toast-message">${escapeHtml(message)}</div>
            </div>
            <button class="toast-close" data-toast-id="${toastId}" aria-label="关闭">&times;</button>
        `;

        // 添加到容器和状态
        container.appendChild(toast);
        this.toasts.set(toastId, toast);

        // 绑定关闭事件
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.close(toastId));

        // 触发进入动画
        requestAnimationFrame(() => {
            toast.classList.add('toast-show');
        });

        // 自动关闭
        const duration = options.duration ?? CONFIG.toastDuration;
        if (duration > 0) {
            setTimeout(() => this.close(toastId), duration);
        }

        return toastId;
    }

    close(toastId) {
        const toast = this.toasts.get(toastId);
        if (toast) {
            toast.classList.remove('toast-show');
            toast.classList.add('toast-hide');

            // 等待动画结束后移除元素
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.parentElement.removeChild(toast);
                }
                this.toasts.delete(toastId);
            }, CONFIG.animationDuration);
        }
    }

    closeAll() {
        this.toasts.forEach((toast, id) => this.close(id));
    }

    getIcon(type) {
        const icons = {
            success: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM8 15L3 10L4.41 8.59L8 12.17L15.59 4.58L17 6L8 15Z" fill="currentColor"/></svg>',
            error: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V13H11V15ZM11 11H9V5H11V11Z" fill="currentColor"/></svg>',
            warning: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M1 17H19L10 2L1 17ZM11 14H9V12H11V14ZM11 10H9V6H11V10Z" fill="currentColor"/></svg>',
            info: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V9H11V15ZM11 7H9V5H11V7Z" fill="currentColor"/></svg>'
        };
        return icons[type] || icons.info;
    }

    getDefaultTitle(type) {
        const titles = {
            success: '成功',
            error: '错误',
            warning: '警告',
            info: '信息'
        };
        return titles[type] || '';
    }
}

// 创建全局 toast 管理器实例
const toastManager = new ToastManager();

// 便捷函数
function showToast(type, message, options = {}) {
    return toastManager.show(type, message, options);
}

function closeToast(toastId) {
    toastManager.close(toastId);
}

function closeAllToasts() {
    toastManager.closeAll();
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化页面
    initializePage();
});

async function initializePage() {
    // 添加页面加载动画
    document.body.style.opacity = '0';
    requestAnimationFrame(() => {
        document.body.style.transition = 'opacity 0.3s ease';
        document.body.style.opacity = '1';
    });

    // 加载当前活跃项目
    await loadActiveProject();

    // 初始化表格行动画
    initTableRowAnimations();

    // 初始化按钮增强
    initButtonEnhancements();

    // 初始化表单验证
    initFormValidation();
}

// 加载活跃项目
async function loadActiveProject() {
    const activeProjectEl = document.getElementById('active-project');
    if (activeProjectEl) {
        try {
            const response = await fetch('/admin/api/active-project');
            const data = await response.json();

            if (data.project_name) {
                activeProjectEl.textContent = `活跃项目: ${data.project_name}`;
                activeProjectEl.title = data.project_name;
            } else {
                activeProjectEl.textContent = '无活跃项目';
            }
        } catch (error) {
            console.error('Error loading active project:', error);
            activeProjectEl.textContent = '加载失败';
        }
    }
}

// 表格行动画
function initTableRowAnimations() {
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    tableRows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateX(-20px)';
        row.style.transition = 'all 0.3s ease';

        setTimeout(() => {
            row.style.opacity = '1';
            row.style.transform = 'translateX(0)';
        }, index * 50);
    });
}

// 按钮增强功能
function initButtonEnhancements() {
    // 为所有按钮添加点击波纹效果
    document.querySelectorAll('button, .btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const ripple = document.createElement('span');
            ripple.style.cssText = `
                position: absolute;
                background: rgba(255, 255, 255, 0.5);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            `;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            ripple.style.width = ripple.style.height = '20px';
            ripple.style.marginLeft = ripple.style.marginTop = '-10px';

            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// 表单验证
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const errors = [];

    form.querySelectorAll('[data-required]').forEach(field => {
        const value = field.value.trim();
        if (!value) {
            isValid = false;
            errors.push(`${getFieldLabel(field)} 是必填项`);
            showFieldError(field, '此字段为必填项');
        } else {
            clearFieldError(field);
        }
    });

    form.querySelectorAll('[data-pattern]').forEach(field => {
        const pattern = new RegExp(field.dataset.pattern);
        if (field.value && !pattern.test(field.value)) {
            isValid = false;
            errors.push(`${getFieldLabel(field)} 格式不正确`);
            showFieldError(field, '格式不正确');
        }
    });

    if (!isValid) {
        showToast('error', errors[0] || '请检查表单填写是否正确');
    }

    return isValid;
}

function getFieldLabel(field) {
    const label = field.querySelector('label') ||
                  document.querySelector(`label[for="${field.id}"]`);
    return label ? label.textContent : '此字段';
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('error');

    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        color: #dc3545;
        font-size: 0.85rem;
        margin-top: 0.25rem;
    `;

    field.parentElement.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('error');
    const errorDiv = field.parentElement.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// HTML 转义工具
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 格式化日期
function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 格式化文件大小
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 复制到剪贴板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('success', '已复制到剪贴板');
        return true;
    } catch (err) {
        // 回退方案
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            showToast('success', '已复制到剪贴板');
            return true;
        } catch (err) {
            showToast('error', '复制失败');
            return false;
        } finally {
            document.body.removeChild(textarea);
        }
    }
}

// 导出功能（如果需要）
function exportToCSV(data, filename) {
    const csv = data.map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
}

// 键盘快捷键
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K 打开命令面板（如果有的话）
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // TODO: 打开命令面板
    }

    // ESC 关闭所有 toast
    if (e.key === 'Escape') {
        closeAllToasts();
    }
});

// 在线/离线状态检测
window.addEventListener('online', () => {
    showToast('success', '网络连接已恢复');
});

window.addEventListener('offline', () => {
    showToast('warning', '网络连接已断开');
});

// 性能监控（开发模式）
if (window.performance) {
    window.addEventListener('load', () => {
        setTimeout(() => {
            const perfData = window.performance.timing;
            const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
            console.log(`页面加载时间: ${pageLoadTime}ms`);
        }, 0);
    });
}
