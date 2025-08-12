/**
 * S3 Vector Browser Loading and Modal Components
 * Handles loading states, modals, toasts, and user interactions
 */

// Global modal and loading state
let currentModal = null;
let loadingOverlay = null;
let toastContainer = null;

/**
 * Initialize global UI components
 */
function initializeGlobalUI() {
    // Create toast container if it doesn't exist
    if (!toastContainer) {
        toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
    }
}

/**
 * Show loading overlay
 */
function showLoading(message = 'Loading...') {
    hideLoading(); // Remove any existing loading overlay
    
    loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner"></div>
            <p class="loading-message">${escapeHtml(message)}</p>
        </div>
    `;
    
    document.body.appendChild(loadingOverlay);
    
    // Fade in
    setTimeout(() => {
        loadingOverlay.classList.add('show');
    }, 10);
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    if (loadingOverlay) {
        loadingOverlay.classList.remove('show');
        setTimeout(() => {
            if (loadingOverlay && loadingOverlay.parentNode) {
                loadingOverlay.parentNode.removeChild(loadingOverlay);
            }
            loadingOverlay = null;
        }, 300);
    }
}

/**
 * Show modal dialog
 */
function showModal(title, content, options = {}) {
    hideModal(); // Remove any existing modal
    
    const {
        size = 'medium',
        closable = true,
        className = ''
    } = options;
    
    currentModal = document.createElement('div');
    currentModal.className = `modal ${className}`;
    currentModal.innerHTML = `
        <div class="modal-content modal-${size}">
            <div class="modal-header">
                <h3 class="modal-title">${escapeHtml(title)}</h3>
                ${closable ? '<button class="modal-close" onclick="closeModal()">&times;</button>' : ''}
            </div>
            <div class="modal-body">
                ${content}
            </div>
        </div>
    `;
    
    document.body.appendChild(currentModal);
    
    // Show modal
    setTimeout(() => {
        currentModal.classList.add('show');
    }, 10);
    
    // Close on backdrop click
    if (closable) {
        currentModal.addEventListener('click', (e) => {
            if (e.target === currentModal) {
                closeModal();
            }
        });
        
        // Close on escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    }
}

/**
 * Hide modal dialog
 */
function hideModal() {
    if (currentModal) {
        currentModal.classList.remove('show');
        setTimeout(() => {
            if (currentModal && currentModal.parentNode) {
                currentModal.parentNode.removeChild(currentModal);
            }
            currentModal = null;
        }, 300);
    }
}

/**
 * Close modal (global function for onclick handlers)
 */
function closeModal() {
    hideModal();
}

/**
 * Show confirmation dialog
 */
function showConfirm(title, message, confirmText = 'Confirm', confirmClass = 'btn-primary') {
    return new Promise((resolve) => {
        const content = `
            <div class="confirm-dialog">
                <p class="confirm-message">${escapeHtml(message)}</p>
                <div class="confirm-actions">
                    <button class="btn btn-secondary" onclick="resolveConfirm(false)">Cancel</button>
                    <button class="btn ${confirmClass}" onclick="resolveConfirm(true)">${escapeHtml(confirmText)}</button>
                </div>
            </div>
        `;
        
        // Store resolve function globally
        window.resolveConfirm = (result) => {
            closeModal();
            resolve(result);
            delete window.resolveConfirm;
        };
        
        showModal(title, content, { size: 'small' });
    });
}

/**
 * Show error dialog
 */
function showError(title, message, details = null) {
    const content = `
        <div class="error-dialog">
            <div class="error-icon">⚠️</div>
            <div class="error-content">
                <p class="error-message">${escapeHtml(message)}</p>
                ${details ? `
                    <div class="error-details" style="display: none;">
                        <h4>Technical Details:</h4>
                        <pre class="error-details-text">${escapeHtml(JSON.stringify(details, null, 2))}</pre>
                    </div>
                    <button class="btn btn-sm btn-secondary" onclick="toggleErrorDetails()">
                        Show Details
                    </button>
                ` : ''}
            </div>
        </div>
    `;
    
    // Global function to toggle error details
    window.toggleErrorDetails = () => {
        const detailsDiv = document.querySelector('.error-details');
        const toggleBtn = document.querySelector('.error-dialog .btn-secondary');
        
        if (detailsDiv && toggleBtn) {
            const isVisible = detailsDiv.style.display !== 'none';
            detailsDiv.style.display = isVisible ? 'none' : 'block';
            toggleBtn.textContent = isVisible ? 'Show Details' : 'Hide Details';
        }
    };
    
    showModal(title, content, { size: 'medium' });
}

/**
 * Show toast notification
 */
function showToast(type, title, message, duration = 5000) {
    initializeGlobalUI();
    
    const toastId = generateId('toast');
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-header">
            <div class="toast-icon">${getToastIcon(type)}</div>
            <h4 class="toast-title">${escapeHtml(title)}</h4>
            <button class="toast-close" onclick="closeToast('${toastId}')">&times;</button>
        </div>
        <div class="toast-body">
            ${escapeHtml(message)}
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Show toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Auto-hide after duration
    if (duration > 0) {
        setTimeout(() => {
            closeToast(toastId);
        }, duration);
    }
    
    return toastId;
}

/**
 * Close toast notification
 */
function closeToast(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
}

/**
 * Get icon for toast type
 */
function getToastIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return icons[type] || 'ℹ️';
}

/**
 * Show progress indicator
 */
function showProgress(title, progress = 0, message = '') {
    const content = `
        <div class="progress-dialog">
            <h4 class="progress-title">${escapeHtml(title)}</h4>
            <div class="progress-bar-container">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${Math.max(0, Math.min(100, progress))}%"></div>
                </div>
                <div class="progress-text">${Math.round(progress)}%</div>
            </div>
            ${message ? `<p class="progress-message">${escapeHtml(message)}</p>` : ''}
        </div>
    `;
    
    showModal('Progress', content, { closable: false, size: 'small' });
}

/**
 * Update progress
 */
function updateProgress(progress, message = '') {
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');
    const progressMessage = document.querySelector('.progress-message');
    
    if (progressFill) {
        progressFill.style.width = `${Math.max(0, Math.min(100, progress))}%`;
    }
    
    if (progressText) {
        progressText.textContent = `${Math.round(progress)}%`;
    }
    
    if (progressMessage && message) {
        progressMessage.textContent = message;
    }
}

/**
 * Hide progress
 */
function hideProgress() {
    hideModal();
}

/**
 * Show loading state for specific element
 */
function showElementLoading(element, message = 'Loading...') {
    if (!element) return;
    
    // Store original content
    element.dataset.originalContent = element.innerHTML;
    element.classList.add('loading-state');
    
    element.innerHTML = `
        <div class="element-loading">
            <div class="spinner-small"></div>
            <span class="loading-text">${escapeHtml(message)}</span>
        </div>
    `;
}

/**
 * Hide loading state for specific element
 */
function hideElementLoading(element) {
    if (!element) return;
    
    element.classList.remove('loading-state');
    
    if (element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        delete element.dataset.originalContent;
    }
}

/**
 * Create loading skeleton for content
 */
function createLoadingSkeleton(type = 'card', count = 1) {
    const skeletons = {
        card: `
            <div class="loading-skeleton-card">
                <div class="skeleton-header">
                    <div class="loading-skeleton skeleton-title"></div>
                </div>
                <div class="skeleton-body">
                    <div class="loading-skeleton skeleton-text"></div>
                    <div class="loading-skeleton skeleton-text"></div>
                    <div class="loading-skeleton skeleton-text" style="width: 60%;"></div>
                </div>
            </div>
        `,
        list: `
            <div class="loading-skeleton-list">
                <div class="loading-skeleton skeleton-text"></div>
                <div class="loading-skeleton skeleton-text" style="width: 80%;"></div>
            </div>
        `,
        table: `
            <div class="loading-skeleton-table">
                <div class="loading-skeleton skeleton-text" style="height: 40px;"></div>
                <div class="loading-skeleton skeleton-text" style="height: 30px;"></div>
                <div class="loading-skeleton skeleton-text" style="height: 30px;"></div>
            </div>
        `
    };
    
    const skeletonHtml = skeletons[type] || skeletons.card;
    return Array(count).fill(skeletonHtml).join('');
}

/**
 * Debounced function to prevent rapid successive calls
 */
function debounceAction(func, wait = 300) {
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

/**
 * Handle global errors
 */
function handleGlobalError(error, context = 'Application') {
    console.error(`${context} Error:`, error);
    
    let title = 'Unexpected Error';
    let message = 'An unexpected error occurred. Please try again.';
    let details = null;
    
    if (error instanceof APIError) {
        title = 'API Error';
        message = error.getUserMessage();
        details = {
            status: error.status,
            url: error.url,
            details: error.details
        };
    } else if (error instanceof Error) {
        message = error.message;
        details = {
            name: error.name,
            stack: error.stack
        };
    }
    
    showError(title, message, details);
}

/**
 * Initialize loading styles
 */
function initializeLoadingStyles() {
    // Add loading styles to document if not already present
    if (!document.getElementById('loading-styles')) {
        const style = document.createElement('style');
        style.id = 'loading-styles';
        style.textContent = `
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                opacity: 0;
                transition: opacity 0.3s ease-in-out;
            }
            
            .loading-overlay.show {
                opacity: 1;
            }
            
            .loading-content {
                background-color: white;
                padding: 2rem;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .loading-message {
                margin-top: 1rem;
                color: #666;
                font-size: 0.9rem;
            }
            
            .spinner-small {
                width: 20px;
                height: 20px;
                border: 2px solid #f3f3f3;
                border-top: 2px solid #1f77b4;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                display: inline-block;
                margin-right: 0.5rem;
            }
            
            .element-loading {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1rem;
                color: #666;
                font-size: 0.9rem;
            }
            
            .loading-state {
                position: relative;
                pointer-events: none;
                opacity: 0.7;
            }
            
            .progress-bar-container {
                margin: 1rem 0;
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .progress-bar {
                flex: 1;
                height: 8px;
                background-color: #f0f0f0;
                border-radius: 4px;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background-color: #1f77b4;
                transition: width 0.3s ease-in-out;
            }
            
            .progress-text {
                font-weight: bold;
                color: #333;
                min-width: 40px;
            }
            
            .error-dialog {
                text-align: center;
                padding: 1rem;
            }
            
            .error-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            
            .error-details {
                margin-top: 1rem;
                text-align: left;
            }
            
            .error-details-text {
                background-color: #f5f5f5;
                padding: 1rem;
                border-radius: 4px;
                font-size: 0.8rem;
                max-height: 200px;
                overflow-y: auto;
            }
            
            .confirm-dialog {
                text-align: center;
                padding: 1rem;
            }
            
            .confirm-message {
                margin-bottom: 2rem;
                font-size: 1.1rem;
                line-height: 1.5;
            }
            
            .confirm-actions {
                display: flex;
                gap: 1rem;
                justify-content: center;
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initializeGlobalUI();
        initializeLoadingStyles();
    });
} else {
    initializeGlobalUI();
    initializeLoadingStyles();
}

/**
 * Handle S3 link from modal (global function)
 */
function handleS3LinkFromModal(s3Uri) {
    // Close current modal first
    closeModal();
    
    // Show S3 content modal
    setTimeout(() => {
        const modalContent = `
            <div class="s3-content-modal">
                <div class="s3-uri-info">
                    <h4>S3 Object Reference</h4>
                    <div class="s3-uri-display">
                        <code>${escapeHtml(s3Uri)}</code>
                    </div>
                    <p class="text-muted">
                        This is a reference to an S3 object. Direct access requires proper AWS credentials and permissions.
                    </p>
                </div>
                
                <div class="s3-actions">
                    <button class="btn btn-secondary" onclick="copyToClipboard('${escapeHtml(s3Uri)}')">
                        📋 Copy URI
                    </button>
                    <button class="btn btn-primary" onclick="window.open('https://console.aws.amazon.com/s3/object/${escapeHtml(s3Uri.replace('s3://', ''))}', '_blank')">
                        🌐 Open in AWS Console
                    </button>
                </div>
                
                <div class="s3-note">
                    <p><strong>Note:</strong> To view the actual content, you would need:</p>
                    <ul>
                        <li>AWS credentials with S3 read permissions</li>
                        <li>A backend service to generate signed URLs</li>
                        <li>Or direct access through AWS CLI/SDK</li>
                    </ul>
                </div>
            </div>
        `;
        
        showModal('S3 Object Reference', modalContent, { size: 'medium' });
    }, 100);
}

// Export functions to global scope
window.handleS3LinkFromModal = handleS3LinkFromModal;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.showModal = showModal;
window.hideModal = hideModal;
window.closeModal = closeModal;
window.showConfirm = showConfirm;
window.showError = showError;
window.showToast = showToast;
window.closeToast = closeToast;
window.showProgress = showProgress;
window.updateProgress = updateProgress;
window.hideProgress = hideProgress;
window.showElementLoading = showElementLoading;
window.hideElementLoading = hideElementLoading;
window.createLoadingSkeleton = createLoadingSkeleton;
window.debounceAction = debounceAction;
window.handleGlobalError = handleGlobalError;