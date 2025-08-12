/**
 * S3 Vector Browser Index List Component
 * Displays list of vector indexes with comprehensive technical details
 */

class IndexListComponent {
    constructor(container, apiClient, stateManager, router) {
        this.container = container;
        this.apiClient = apiClient;
        this.stateManager = stateManager;
        this.router = router;
        this.isLoading = false;
        this.indexes = [];
        this.filteredIndexes = [];
        this.bucketName = null;
        this.searchQuery = '';

        this._setupEventListeners();
    }

    /**
     * Setup event listeners
     */
    _setupEventListeners() {
        // Listen for refresh requests
        this.stateManager.addListener('refreshIndexes', () => {
            this.refresh();
        });
    }

    /**
     * Render the index list for a specific bucket
     */
    async render(bucketName) {
        if (this.isLoading) return;

        this.bucketName = bucketName;
        this.isLoading = true;
        this.stateManager.setLoading(`indexes_${bucketName}`, true);

        try {
            // Show loading state
            this._renderLoading();

            // Get indexes from API
            const indexes = await this.apiClient.getIndexes(bucketName);
            this.indexes = indexes || [];

            // Cache the data
            this.stateManager.setResourceData(`indexes_${bucketName}`, this.indexes);

            // Apply search filter
            this._applySearchFilter();

            // Render the indexes
            this._renderIndexes();

        } catch (error) {
            console.error('Failed to load indexes:', error);
            this.stateManager.setResourceError(`indexes_${bucketName}`, error);
            this._renderError(error);
        } finally {
            this.isLoading = false;
            this.stateManager.setLoading(`indexes_${bucketName}`, false);
        }
    }

    /**
     * Refresh index list
     */
    async refresh() {
        if (!this.bucketName) return;

        // Clear cache
        this.stateManager.clearCache(`indexes_${this.bucketName}`);
        await this.render(this.bucketName);
    }

    /**
     * Render loading state
     */
    _renderLoading() {
        this.container.innerHTML = `
            <div class="content-header">
                <h2>📊 Vector Indexes</h2>
                <p class="text-muted">Loading indexes in bucket "${escapeHtml(this.bucketName)}"...</p>
            </div>
            <div class="loading-container">
                ${this._createSkeletonCards(3)}
            </div>
        `;
    }

    /**
     * Render index list
     */
    _renderIndexes() {
        if (this.indexes.length === 0) {
            this._renderEmptyState();
            return;
        }

        const indexesHtml = this.filteredIndexes.map(index => this._createIndexCard(index)).join('');

        this.container.innerHTML = `
            <div class="content-header">
                <div class="header-main">
                    <h2>📊 Vector Indexes</h2>
                    <p class="text-muted">
                        ${this.filteredIndexes.length !== this.indexes.length ?
                `Showing ${formatNumber(this.filteredIndexes.length)} of ${formatNumber(this.indexes.length)} indexes` :
                `Found ${formatNumber(this.indexes.length)} vector index${this.indexes.length !== 1 ? 'es' : ''}`
            } in bucket "${escapeHtml(this.bucketName)}"
                    </p>
                </div>
                <div class="header-actions">
                    <div class="search-container">
                        <input type="text" 
                               id="index-search" 
                               class="search-input" 
                               placeholder="Search indexes..." 
                               value="${this.searchQuery || ''}"
                               oninput="window.indexListComponent.handleSearch(this.value)">
                        <span class="search-icon">🔍</span>
                    </div>
                    <button class="btn btn-secondary" onclick="window.indexListComponent.refresh()" title="Refresh index list">
                        <span class="btn-icon">🔄</span>
                        Refresh
                    </button>
                </div>
            </div>
            <div class="card-grid">
                ${indexesHtml}
            </div>
        `;

        // Store reference for global access
        window.indexListComponent = this;
    }

    /**
     * Render empty state
     */
    _renderEmptyState() {
        this.container.innerHTML = `
            <div class="content-header">
                <h2>📊 Vector Indexes</h2>
                <p class="text-muted">No vector indexes found in bucket "${escapeHtml(this.bucketName)}"</p>
            </div>
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <h3 class="empty-state-title">No Vector Indexes Found</h3>
                <p class="empty-state-description">
                    This bucket doesn't contain any vector indexes yet.<br>
                    Create your first vector index to start storing and searching vectors.
                </p>
                <div class="empty-state-actions">
                    <button class="btn btn-secondary" onclick="window.indexListComponent.refresh()">
                        <span class="btn-icon">🔄</span>
                        Refresh
                    </button>
                </div>
            </div>
        `;

        // Store reference for global access
        window.indexListComponent = this;
    }

    /**
     * Render error state
     */
    _renderError(error) {
        const errorMessage = error instanceof APIError ? error.getUserMessage() : formatError(error);
        const recoveryActions = error instanceof APIError ? error.getRecoveryActions() : ['Try again'];

        this.container.innerHTML = `
            <div class="content-header">
                <h2>📊 Vector Indexes</h2>
                <p class="text-muted">Failed to load indexes</p>
            </div>
            <div class="error-state">
                <div class="error-message">
                    <h3>Failed to Load Indexes</h3>
                    <p>${escapeHtml(errorMessage)}</p>
                    <div class="error-actions">
                        ${recoveryActions.map(action =>
            `<button class="btn btn-primary" onclick="window.indexListComponent.refresh()">
                                ${escapeHtml(action)}
                            </button>`
        ).join('')}
                    </div>
                </div>
            </div>
        `;

        // Store reference for global access
        window.indexListComponent = this;
    }

    /**
     * Create index card HTML
     */
    _createIndexCard(index) {
        const creationTime = formatTimestamp(index.creation_time);
        const relativeTime = formatRelativeTime(index.creation_time);
        const distanceMetric = formatDistanceMetric(index.distance_metric);
        const dataType = formatDataType(index.data_type);
        const itemCount = formatItemCount(index.item_count);

        return `
            <div class="card resource-card card-clickable" onclick="window.indexListComponent.navigateToIndex('${escapeHtml(index.name)}')">
                <div class="card-header">
                    <div class="resource-header">
                        <div class="resource-icon">📊</div>
                        <div class="resource-title">
                            <div class="resource-name">${escapeHtml(index.name)}</div>
                            <div class="resource-arn" title="${escapeHtml(index.arn)}">
                                ${truncateText(index.arn, 60)}
                            </div>
                        </div>
                        <div class="resource-actions" onclick="event.stopPropagation()">
                            <button class="btn btn-sm btn-danger" 
                                    onclick="window.indexListComponent.deleteIndex('${escapeHtml(index.name)}')"
                                    title="Delete index">
                                <span class="btn-icon">🗑️</span>
                            </button>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="resource-details">
                        <div class="detail-item">
                            <div class="detail-label">Dimensions</div>
                            <div class="detail-value">
                                <span class="metric-badge metric-dimension">${formatNumber(index.dimension)}</span>
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Distance Metric</div>
                            <div class="detail-value">
                                <span class="metric-badge metric-distance">${distanceMetric}</span>
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Data Type</div>
                            <div class="detail-value">
                                <span class="metric-badge metric-type">${dataType}</span>
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Item Count</div>
                            <div class="detail-value">
                                <span class="metric-badge metric-count">${itemCount}</span>
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Created</div>
                            <div class="detail-value" title="${creationTime}">${relativeTime}</div>
                        </div>
                        ${index.item_count && index.dimension ? `
                            <div class="detail-item">
                                <div class="detail-label">Estimated Size</div>
                                <div class="detail-value">${this._estimateIndexSize(index.item_count, index.dimension)}</div>
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="card-footer">
                    <div class="footer-info">
                        <span class="text-muted">Click to explore items</span>
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
                        <div class="detail-item">
                            <div class="loading-skeleton skeleton-text"></div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Estimate index size based on item count and dimensions
     */
    _estimateIndexSize(itemCount, dimension) {
        if (!itemCount || !dimension) return 'Unknown';

        // Rough estimate: 4 bytes per float32 dimension + metadata overhead
        const bytesPerItem = (dimension * 4) + 100; // 100 bytes metadata overhead
        const totalBytes = itemCount * bytesPerItem;

        return formatBytes(totalBytes);
    }

    /**
     * Handle search input
     */
    handleSearch(query) {
        this.searchQuery = query.toLowerCase();
        this._applySearchFilter();
        this._renderIndexes();
    }

    /**
     * Apply search filter to indexes
     */
    _applySearchFilter() {
        if (!this.searchQuery) {
            this.filteredIndexes = [...this.indexes];
            return;
        }

        this.filteredIndexes = this.indexes.filter(index => {
            return index.name.toLowerCase().includes(this.searchQuery) ||
                (index.arn && index.arn.toLowerCase().includes(this.searchQuery)) ||
                (index.distance_metric && index.distance_metric.toLowerCase().includes(this.searchQuery)) ||
                (index.data_type && index.data_type.toLowerCase().includes(this.searchQuery));
        });
    }

    /**
     * Navigate to index's items
     */
    navigateToIndex(indexName) {
        const url = this.router.generateUrl('items', {
            bucketName: this.bucketName,
            indexName
        });
        this.router.navigate(url);
    }

    /**
     * Show index details modal
     */
    async showIndexDetails(indexName) {
        try {
            showLoading('Loading index details...');
            const details = await this.apiClient.getIndexDetails(this.bucketName, indexName);
            hideLoading();

            const modalContent = this._createIndexDetailsModal(indexName, details);
            showModal('Index Details', modalContent);

        } catch (error) {
            hideLoading();
            showError('Failed to Load Details', formatError(error));
        }
    }

    /**
     * Create index details modal content
     */
    _createIndexDetailsModal(indexName, details) {
        const index = details.index || details;
        const arnInfo = formatARN(index.arn || '');

        return `
            <div class="detail-modal">
                <div class="detail-section">
                    <h4>Basic Information</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">Index Name</div>
                            <div class="detail-value detail-value-mono">${escapeHtml(indexName)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">ARN</div>
                            <div class="detail-value detail-value-mono" title="${escapeHtml(index.arn || '')}">${escapeHtml(index.arn || 'N/A')}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Bucket</div>
                            <div class="detail-value detail-value-mono">${escapeHtml(this.bucketName)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Region</div>
                            <div class="detail-value">${extractRegionFromARN(index.arn) || 'N/A'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Account ID</div>
                            <div class="detail-value detail-value-mono">${extractAccountFromARN(index.arn) || 'N/A'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Created</div>
                            <div class="detail-value">${formatTimestamp(index.creation_time)}</div>
                        </div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>Technical Specifications</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">Dimensions</div>
                            <div class="detail-value">
                                <span class="metric-badge metric-dimension">${formatNumber(index.dimension)}</span>
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Distance Metric</div>
                            <div class="detail-value">
                                <span class="metric-badge metric-distance">${formatDistanceMetric(index.distance_metric)}</span>
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Data Type</div>
                            <div class="detail-value">
                                <span class="metric-badge metric-type">${formatDataType(index.data_type)}</span>
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Item Count</div>
                            <div class="detail-value">
                                <span class="metric-badge metric-count">${formatItemCount(index.item_count)}</span>
                            </div>
                        </div>
                        ${index.item_count && index.dimension ? `
                            <div class="detail-item">
                                <div class="detail-label">Estimated Size</div>
                                <div class="detail-value">${this._estimateIndexSize(index.item_count, index.dimension)}</div>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                ${Object.keys(details).length > 8 ? `
                    <div class="detail-section">
                        <h4>Additional Details</h4>
                        <pre class="detail-json">${formatJSON(details)}</pre>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Delete index with confirmation
     */
    async deleteIndex(indexName) {
        const confirmed = await showConfirm(
            'Delete Index',
            `Are you sure you want to delete the index "${indexName}"? This will permanently delete all vector data in this index. This action cannot be undone.`,
            'Delete',
            'btn-danger'
        );

        if (!confirmed) return;

        try {
            showLoading('Deleting index...');
            await this.apiClient.deleteIndex(this.bucketName, indexName);
            hideLoading();

            showToast('success', 'Index Deleted', `Index "${indexName}" has been deleted successfully.`);

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
        this.stateManager.removeAllListeners('refreshIndexes');
        if (window.indexListComponent === this) {
            delete window.indexListComponent;
        }
    }
}

// Export for use in other modules
window.IndexListComponent = IndexListComponent;