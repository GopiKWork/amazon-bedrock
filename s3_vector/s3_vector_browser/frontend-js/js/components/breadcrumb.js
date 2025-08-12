/**
 * S3 Vector Browser Breadcrumb Component
 * Displays hierarchical navigation breadcrumb trail
 */

class BreadcrumbComponent {
    constructor(container, router, stateManager) {
        this.container = container;
        this.router = router;
        this.stateManager = stateManager;
        this.currentBreadcrumb = [];
        
        this._setupEventListeners();
    }

    /**
     * Setup event listeners
     */
    _setupEventListeners() {
        // Listen for route changes
        this.router.addListener((routeData) => {
            this.render(routeData.breadcrumb);
        });
    }

    /**
     * Render breadcrumb navigation
     */
    render(breadcrumb = []) {
        this.currentBreadcrumb = breadcrumb || [];
        
        if (this.currentBreadcrumb.length === 0) {
            this._renderEmpty();
            return;
        }

        const breadcrumbHtml = this._createBreadcrumbItems();
        
        this.container.innerHTML = breadcrumbHtml;
    }

    /**
     * Render empty breadcrumb
     */
    _renderEmpty() {
        this.container.innerHTML = `
            <div class="breadcrumb-item">
                <span class="breadcrumb-current">S3 Vector Browser</span>
            </div>
        `;
    }

    /**
     * Create breadcrumb items HTML
     */
    _createBreadcrumbItems() {
        const items = this.currentBreadcrumb.map((item, index) => {
            const isLast = index === this.currentBreadcrumb.length - 1;
            const isFirst = index === 0;
            
            return `
                <div class="breadcrumb-item">
                    ${!isFirst ? '<span class="breadcrumb-separator">›</span>' : ''}
                    ${item.current || isLast ? 
                        `<span class="breadcrumb-current" title="${escapeHtml(item.label)}">
                            ${this._formatBreadcrumbLabel(item.label, isLast)}
                        </span>` :
                        `<a href="${escapeHtml(item.path)}" class="breadcrumb-link" 
                           title="Navigate to ${escapeHtml(item.label)}">
                            ${this._formatBreadcrumbLabel(item.label, false)}
                        </a>`
                    }
                </div>
            `;
        }).join('');

        return items;
    }

    /**
     * Format breadcrumb label with appropriate icons and truncation
     */
    _formatBreadcrumbLabel(label, isCurrent = false) {
        let icon = '';
        let formattedLabel = label;
        
        // Add appropriate icons based on label
        if (label === 'Buckets' || label.includes('bucket')) {
            icon = '📦';
        } else if (label.includes('index') || this._looksLikeIndexName(label)) {
            icon = '📊';
        } else if (this._looksLikeItemId(label)) {
            icon = '📄';
        }
        
        // Truncate long labels
        if (formattedLabel.length > 30) {
            formattedLabel = truncateText(formattedLabel, isCurrent ? 40 : 25);
        }
        
        return `${icon ? `<span class="breadcrumb-icon">${icon}</span>` : ''}${escapeHtml(formattedLabel)}`;
    }

    /**
     * Check if label looks like an index name
     */
    _looksLikeIndexName(label) {
        // Common patterns for index names
        return label.includes('index') || 
               label.includes('vector') || 
               label.includes('-') && label.length > 10;
    }

    /**
     * Check if label looks like an item ID
     */
    _looksLikeItemId(label) {
        // Common patterns for item IDs (UUIDs, hashes, etc.)
        return /^[a-f0-9-]{8,}$/i.test(label) || 
               /^[a-zA-Z0-9_-]{10,}$/.test(label) ||
               label.includes('_') && label.length > 8;
    }

    /**
     * Get current breadcrumb path as string
     */
    getCurrentPath() {
        return this.currentBreadcrumb
            .map(item => item.label)
            .join(' › ');
    }

    /**
     * Get current breadcrumb depth
     */
    getDepth() {
        return this.currentBreadcrumb.length;
    }

    /**
     * Navigate to a specific breadcrumb level
     */
    navigateToLevel(index) {
        if (index >= 0 && index < this.currentBreadcrumb.length) {
            const item = this.currentBreadcrumb[index];
            if (item.path && !item.current) {
                this.router.navigate(item.path);
            }
        }
    }

    /**
     * Navigate back one level
     */
    navigateBack() {
        if (this.currentBreadcrumb.length > 1) {
            const previousItem = this.currentBreadcrumb[this.currentBreadcrumb.length - 2];
            if (previousItem.path) {
                this.router.navigate(previousItem.path);
            }
        }
    }

    /**
     * Navigate to home (buckets)
     */
    navigateHome() {
        this.router.navigate('#/buckets');
    }

    /**
     * Update breadcrumb with additional context
     */
    updateContext(context = {}) {
        // Add AWS context information if available
        const awsContext = this.stateManager.getAWSContext();
        
        if (awsContext.region || awsContext.accountId) {
            const contextInfo = [];
            if (awsContext.region) contextInfo.push(`Region: ${awsContext.region}`);
            if (awsContext.accountId) contextInfo.push(`Account: ${awsContext.accountId}`);
            
            // Update container with context
            const contextHtml = `
                <div class="breadcrumb-context">
                    <span class="context-info">${contextInfo.join(' • ')}</span>
                </div>
            `;
            
            // Add context after breadcrumb if not already present
            if (!this.container.querySelector('.breadcrumb-context')) {
                this.container.insertAdjacentHTML('beforeend', contextHtml);
            }
        }
    }

    /**
     * Destroy component
     */
    destroy() {
        // Router listeners are cleaned up automatically
        this.currentBreadcrumb = [];
    }
}

// Export for use in other modules
window.BreadcrumbComponent = BreadcrumbComponent;