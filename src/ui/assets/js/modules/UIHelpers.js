// UI Helper Functions Module
class UIHelpers {
    constructor() {
        this.loadingElements = new Set();
    }

    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.disabled = true;
            const originalText = element.innerHTML;
            element.setAttribute('data-original-text', originalText);
            element.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading...';
            this.loadingElements.add(elementId);
        }
    }

    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element && this.loadingElements.has(elementId)) {
            element.disabled = false;
            const originalText = element.getAttribute('data-original-text');
            if (originalText) {
                element.innerHTML = originalText;
                element.removeAttribute('data-original-text');
            }
            this.loadingElements.delete(elementId);
        }
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastBody = toast.querySelector('.toast-body');
        const toastHeader = toast.querySelector('.toast-header');
        
        // Update toast content
        toastBody.textContent = message;
        
        // Update toast style based on type
        toast.className = 'toast';
        toastHeader.className = 'toast-header';
        
        switch (type) {
            case 'success':
                toast.classList.add('bg-success', 'text-white');
                toastHeader.classList.add('bg-success', 'text-white');
                toastHeader.querySelector('i').className = 'fas fa-check-circle me-2';
                break;
            case 'error':
                toast.classList.add('bg-danger', 'text-white');
                toastHeader.classList.add('bg-danger', 'text-white');
                toastHeader.querySelector('i').className = 'fas fa-exclamation-circle me-2';
                break;
            case 'warning':
                toast.classList.add('bg-warning', 'text-dark');
                toastHeader.classList.add('bg-warning', 'text-dark');
                toastHeader.querySelector('i').className = 'fas fa-exclamation-triangle me-2';
                break;
            default:
                toast.classList.add('bg-info', 'text-white');
                toastHeader.classList.add('bg-info', 'text-white');
                toastHeader.querySelector('i').className = 'fas fa-info-circle me-2';
        }
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: type === 'error' ? 8000 : 5000
        });
        bsToast.show();
    }

    getConfidenceClass(confidence) {
        if (confidence >= 0.8) return 'high';
        if (confidence >= 0.5) return 'medium';
        return 'low';
    }

    updatePerformanceMonitor(metrics) {
        const apiTimeElement = document.getElementById('api-time');
        const aiTimeElement = document.getElementById('ai-time');
        const cacheStatusElement = document.getElementById('cache-status');
        const totalTimeElement = document.getElementById('total-time');

        if (apiTimeElement && metrics.apiTime !== null) {
            apiTimeElement.textContent = `${metrics.apiTime}ms`;
        }

        if (aiTimeElement && metrics.aiTime !== null) {
            aiTimeElement.textContent = `${metrics.aiTime}ms`;
        }

        if (cacheStatusElement) {
            cacheStatusElement.textContent = metrics.cached ? 'HIT' : 'MISS';
            cacheStatusElement.className = `fw-bold text-${metrics.cached ? 'success' : 'warning'}`;
        }

        if (totalTimeElement && metrics.totalTime) {
            totalTimeElement.textContent = `${metrics.totalTime}ms`;
        }
    }

    togglePerformanceMonitor() {
        const monitor = document.getElementById('performance-monitor');
        if (monitor) {
            monitor.style.display = monitor.style.display === 'none' ? 'block' : 'none';
        }
    }

    findCommentElementById(commentId) {
        return document.querySelector(`[data-comment-id="${commentId}"]`);
    }

    animateElement(element, animationClass, duration = 1000) {
        element.classList.add(animationClass);
        setTimeout(() => {
            element.classList.remove(animationClass);
        }, duration);
    }

    createLoadingSpinner(text = 'Loading...') {
        return `
            <div class="text-center p-3">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 mb-0">${text}</p>
            </div>
        `;
    }

    createErrorMessage(message, showRetry = false, retryAction = null) {
        const retryButton = showRetry && retryAction ? `
            <button class="btn btn-sm btn-outline-primary mt-2" onclick="${retryAction}">
                <i class="fas fa-redo me-1"></i>Retry
            </button>
        ` : '';

        return `
            <div class="alert alert-warning m-3">
                <div class="d-flex align-items-center mb-2">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Error</strong>
                </div>
                <p class="mb-2">${message}</p>
                ${retryButton}
            </div>
        `;
    }

    createEmptyState(icon, message) {
        return `
            <div class="text-center text-muted p-3">
                <i class="fas ${icon} fa-2x mb-2"></i>
                <p class="mb-0">${message}</p>
            </div>
        `;
    }
}

// Export for use in other modules
window.UIHelpers = UIHelpers;
