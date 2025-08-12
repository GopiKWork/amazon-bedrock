/**
 * S3 Vector Browser Bucket List Component
 * Displays list of S3 Vector buckets with comprehensive metadata
 */

class BucketListComponent {
    constructor(container, apiClient, stateManager, router) {
        this.container = container;
        this.apiClient = apiClient;
        this.stateManager = stateManager;
        this.router = router;
        this.isLoading = false;
        this.buckets = [];
        this.filteredBuckets = [];
        this.searchQuery = '';
        
        this._setupEventListeners();
    }

    /**
     * Setup event listeners
     */
    _setupEventListeners() {
        // Listen for refresh requests
        this.stateManager.addListener('refreshBuckets', () => {
            this.refresh();
        });
    }

    /**
     * Render the bucket list
     */
    async render() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.stateManager.setLoading('buckets', true);
        
        try {
            // Show loading state
            this._renderLoading();
            
            // Get buckets from API
            const buckets = await this.apiClient.getBuckets();
            this.buckets = buckets || [];
            
            // Update AWS context from first bucket
            if (this.buckets.length > 0) {
                this.stateManager.updateAWSContextFromResource(this.buckets[0]);
            }
            
            // Cache the data
            this.stateManager.setResourceData('buckets', this.buckets);
            
            // Apply search filter
            this._applySearchFilter();
            
            // Render the buckets
            this._renderBuckets();
            
        } catch (error) {
            console.error('Failed to load buckets:', error);
            this.stateManager.setResourceError('buckets', error);
            this._renderError(error);
        } finally {
            this.isLoading = false;
            this.stateManager.setLoading('buckets', false);
        }
    }

    /**
     * Refresh bucket list
     */
    async refresh() {
        // Clear cache
        this.stateManager.clearCache('buckets');
        await this.render();
    }

    /**
     * Render loading state
     */
    _renderLoading() {
        this.container.innerHTML = `
            <div class="content-header">
                <h2>📦 Vector Buckets</h2>
                <p class="text-muted">Loading your S3 Vector buckets...</p>
            </div>
            <div class="loading-container">
                ${this._createSkeletonCards(3)}
            </div>
        `;
    }

    /**
     * Render bucket list
     */
    _renderBuckets() {
        if (this.buckets.length === 0) {
            this._renderEmptyState();
            return;
        }

        const bucketsHtml = this.filteredBuckets.map(bucket => this._createBucketCard(bucket)).join('');
        
        this.container.innerHTML = `
            <div class="content-header">
                <div class="header-main">
                    <h2>📦 Vector Buckets</h2>
                    <p class="text-muted">
                        ${this.filteredBuckets.length !== this.buckets.length ? 
                            `Showing ${formatNumber(this.filteredBuckets.length)} of ${formatNumber(this.buckets.length)} buckets` :
                            `Found ${formatNumber(this.buckets.length)} vector bucket${this.buckets.length !== 1 ? 's' : ''}`
                        }
                    </p>
                </div>
                <div class="header-actions">
                    <div class="search-container">
                        <input type="text" 
                               id="bucket-search" 
                               class="search-input" 
                               placeholder="Search buckets..." 
                               value="${this.searchQuery || ''}"
                               oninput="window.bucketListComponent.handleSearch(this.value)">
                        <span class="search-icon">🔍</span>
                    </div>
                    <button class="btn btn-secondary" onclick="window.bucketListComponent.refresh()" title="Refresh bucket list">
                        <span class="btn-icon">🔄</span>
                        Refresh
                    </button>
                </div>
            </div>
            <div class="card-grid">
                ${bucketsHtml}
            </div>
        `;

        // Store reference for global access
        window.bucketListComponent = this;
    }

    /**
     * Render empty state
     */
    _renderEmptyState() {
        this.container.innerHTML = `
            <div class="content-header">
                <h2>📦 Vector Buckets</h2>
                <p class="text-muted">No vector buckets found in your AWS account</p>
            </div>
            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <h3 class="empty-state-title">No Vector Buckets Found</h3>
                <p class="empty-state-description">
                    You don't have any S3 Vector buckets in this region yet.<br>
                    Create your first vector bucket to get started with vector search.
                </p>
                <div class="empty-state-actions">
                    <button class="btn btn-secondary" onclick="window.bucketListComponent.refresh()">
                        <span class="btn-icon">🔄</span>
                        Refresh
                    </button>
                </div>
            </div>
        `;

        // Store reference for global access
        window.bucketListComponent = this;
    }

    /**
     * Render error state
     */
    _renderError(error) {
        const errorMessage = error instanceof APIError ? error.getUserMessage() : formatError(error);
        const recoveryActions = error instanceof APIError ? error.getRecoveryActions() : ['Try again'];
        
        this.container.innerHTML = `
            <div class="content-header">
                <h2>📦 Vector Buckets</h2>
                <p class="text-muted">Failed to load buckets</p>
            </div>
            <div class="error-state">
                <div class="error-message">
                    <h3>Failed to Load Buckets</h3>
                    <p>${escapeHtml(errorMessage)}</p>
                    <div class="error-actions">
                        ${recoveryActions.map(action => 
                            `<button class="btn btn-primary" onclick="window.bucketListComponent.refresh()">
                                ${escapeHtml(action)}
                            </button>`
                        ).join('')}
                    </div>
                </div>
            </div>
        `;

        // Store reference for global access
        window.bucketListComponent = this;
    }

    /**
     * Create bucket card HTML
     */
    _createBucketCard(bucket) {
        const creationTime = formatTimestamp(bucket.creation_time);
        const relativeTime = formatRelativeTime(bucket.creation_time);

        return `
            <div class="card resource-card card-clickable" onclick="window.bucketListComponent.navigateToBucket('${escapeHtml(bucket.name)}')">
                <div class="card-header">
                    <div class="resource-header">
                        <div class="resource-icon">📦</div>
                        <div class="resource-title">
                            <div class="resource-name">${escapeHtml(bucket.name)}</div>
                            <div class="resource-arn" title="${escapeHtml(bucket.arn)}">
                                ${truncateText(bucket.arn, 60)}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="resource-details">
                        <div class="detail-item">
                            <div class="detail-label">Created</div>
                            <div class="detail-value" title="${creationTime}">${relativeTime}</div>
                        </div>
                    </div>
                </div>
                <div class="card-footer">
                    <div class="footer-info">
                        <span class="text-muted">Click to explore indexes</span>
                    </div>
                    <div class="footer-actions">
                        <span class="btn-icon">→</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create skeleton loading cards
     */
    _createSkeletonCards(count) {
        return Array(count).fill(0).map(() => `
            <div class="card resource-card">
                <div class="card-header">
                    <div class="resource-header">
                        <div class="loading-skeleton skeleton-title"></div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="resource-details">
                        <div class="detail-item">
                            <div class="loading-skeleton skeleton-text"></div>
                        </div>
                        <div class="detail-item">
                            <div class="loading-skeleton skeleton-text"></div>
                        </div>
                        <div class="detail-item">
                            <div class="loading-skeleton skeleton-text"></div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Handle search input
     */
    handleSearch(query) {
        this.searchQuery = query.toLowerCase();
        this._applySearchFilter();
        this._renderBuckets();
    }

    /**
     * Apply search filter to buckets
     */
    _applySearchFilter() {
        if (!this.searchQuery) {
            this.filteredBuckets = [...this.buckets];
            return;
        }

        this.filteredBuckets = this.buckets.filter(bucket => {
            return bucket.name.toLowerCase().includes(this.searchQuery) ||
                   (bucket.arn && bucket.arn.toLowerCase().includes(this.searchQuery));
        });
    }

    /**
     * Navigate to bucket's indexes
     */
    navigateToBucket(bucketName) {
        const url = this.router.generateUrl('indexes', { bucketName });
        this.router.navigate(url);
    }

    /**
     * Show bucket details modal
     */
    async showBucketDetails(bucketName) {
        try {
            showLoading('Loading bucket details...');
            const details = await this.apiClient.getBucketDetails(bucketName);
            hideLoading();
            
            const modalContent = this._createBucketDetailsModal(bucketName, details);
            showModal('Bucket Details', modalContent);
            
        } catch (error) {
            hideLoading();
            showError('Failed to Load Details', formatError(error));
        }
    }

    /**
     * Create bucket details modal content
     */
    _createBucketDetailsModal(bucketName, details) {
        const arnInfo = formatARN(details.arn || '');
        
        return `
            <div class="detail-modal">
                <div class="detail-section">
                    <h4>Basic Information</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">Bucket Name</div>
                            <div class="detail-value detail-value-mono">${escapeHtml(bucketName)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">ARN</div>
                            <div class="detail-value detail-value-mono" title="${escapeHtml(details.arn || '')}">${escapeHtml(details.arn || 'N/A')}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Region</div>
                            <div class="detail-value">${escapeHtml(details.region || 'N/A')}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Account ID</div>
                            <div class="detail-value detail-value-mono">${extractAccountFromARN(details.arn) || 'N/A'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Created</div>
                            <div class="detail-value">${formatTimestamp(details.creation_time)}</div>
                        </div>
                    </div>
                </div>
                
                ${Object.keys(details).length > 5 ? `
                    <div class="detail-section">
                        <h4>Additional Details</h4>
                        <pre class="detail-json">${formatJSON(details)}</pre>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Delete bucket with confirmation
     */
    async deleteBucket(bucketName) {
        const confirmed = await showConfirm(
            'Delete Bucket',
            `Are you sure you want to delete the bucket "${bucketName}"? This action cannot be undone.`,
            'Delete',
            'btn-danger'
        );
        
        if (!confirmed) return;
        
        try {
            showLoading('Deleting bucket...');
            await this.apiClient.deleteBucket(bucketName);
            hideLoading();
            
            showToast('success', 'Bucket Deleted', `Bucket "${bucketName}" has been deleted successfully.`);
            
            // Refresh the list
            await this.refresh();
            
        } catch (error) {
            hideLoading();
            showError('Delete Failed', formatError(error));
        }
    }

    /**
     * Destroy component
     */
    destroy() {
        this.stateManager.removeAllListeners('refreshBuckets');
        if (window.bucketListComponent === this) {
            delete window.bucketListComponent;
        }
    }
}

// Export for use in other modules
window.BucketListComponent = BucketListComponent;