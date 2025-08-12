/**
 * S3 Vector Browser Item List Component
 * Displays list of vector items with metadata preview and detailed views
 */

class ItemListComponent {
    constructor(container, apiClient, stateManager, router) {
        this.container = container;
        this.apiClient = apiClient;
        this.stateManager = stateManager;
        this.router = router;
        this.isLoading = false;
        this.items = [];
        this.bucketName = null;
        this.indexName = null;
        this.expandedItems = new Set();
        this.currentLimit = 50;
        this.currentOffset = 0;
        
        this._setupEventListeners();
    }

    /**
     * Setup event listeners
     */
    _setupEventListeners() {
        // Listen for refresh requests
        this.stateManager.addListener('refreshItems', () => {
            this.refresh();
        });
    }

    /**
     * Render the item list for a specific index
     */
    async render(bucketName, indexName, options = {}) {
        if (this.isLoading) return;
        
        this.bucketName = bucketName;
        this.indexName = indexName;
        this.currentLimit = options.limit || 50;
        this.currentOffset = options.offset || 0;
        
        this.isLoading = true;
        const cacheKey = `items_${bucketName}_${indexName}`;
        this.stateManager.setLoading(cacheKey, true);
        
        try {
            // Show loading state
            this._renderLoading();
            
            // Get items from API
            const items = await this.apiClient.getItems(bucketName, indexName, {
                limit: this.currentLimit,
                offset: this.currentOffset
            });
            this.items = items || [];
            
            // Cache the data
            this.stateManager.setResourceData(cacheKey, this.items);
            
            // Render the items
            this._renderItems();
            
        } catch (error) {
            console.error('Failed to load items:', error);
            this.stateManager.setResourceError(cacheKey, error);
            this._renderError(error);
        } finally {
            this.isLoading = false;
            this.stateManager.setLoading(cacheKey, false);
        }
    }

    /**
     * Refresh item list
     */
    async refresh() {
        if (!this.bucketName || !this.indexName) return;
        
        // Clear cache and expanded items
        this.stateManager.clearCache(`items_${this.bucketName}_${this.indexName}`);
        this.expandedItems.clear();
        // Preserve search query
        const currentSearch = this.searchQuery;
        await this.render(this.bucketName, this.indexName);
        // Restore search query
        if (currentSearch) {
            this.searchQuery = currentSearch;
            this._applySearchFilter();
            this._renderItems();
        }
    }

    /**
     * Clear search query
     */
    clearSearch() {
        this.searchQuery = '';
        this._applySearchFilter();
        this._renderItems();
        
        // Clear the search input
        const searchInput = document.getElementById('item-search');
        if (searchInput) {
            searchInput.value = '';
        }
    }

    /**
     * Highlight search terms in text
     */
    _highlightSearchTerm(text, searchTerm) {
        if (!searchTerm || !text) return escapeHtml(text);
        
        const escapedText = escapeHtml(text);
        const escapedSearchTerm = escapeHtml(searchTerm);
        
        // Create a case-insensitive regex
        const regex = new RegExp(`(${escapedSearchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        
        return escapedText.replace(regex, '<span class="search-highlight">$1</span>');
    }

    /**
     * Render loading state
     */
    _renderLoading() {
        this.container.innerHTML = `
            <div class="content-header">
                <h2>📄 Vector Items</h2>
                <p class="text-muted">Loading items in index "${escapeHtml(this.indexName)}"...</p>
            </div>
            <div class="loading-container">
                ${this._createSkeletonCards(5)}
            </div>
        `;
    }

    /**
     * Render item list
     */
    _renderItems() {
        if (this.items.length === 0) {
            this._renderEmptyState();
            return;
        }

        const itemsHtml = this.items.map(item => this._createItemCard(item)).join('');
        
        this.container.innerHTML = `
            <div class="content-header">
                <div class="header-main">
                    <h2>📄 Vector Items</h2>
                    <p class="text-muted">
                        Found ${formatNumber(this.items.length)} vector item${this.items.length !== 1 ? 's' : ''} 
                        in index "${escapeHtml(this.indexName)}"
                        ${this.currentOffset > 0 ? ` (showing from ${this.currentOffset + 1})` : ''}
                    </p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-secondary" onclick="window.itemListComponent.refresh()" title="Refresh item list">
                        <span class="btn-icon">🔄</span>
                        Refresh
                    </button>
                    <button class="btn btn-secondary" onclick="window.itemListComponent.showLoadMoreOptions()" title="Load more items">
                        <span class="btn-icon">📄</span>
                        Load More
                    </button>
                </div>
            </div>
            <div class="items-container">
                ${itemsHtml}
            </div>
            ${this.items.length >= this.currentLimit ? `
                <div class="pagination-container">
                    <button class="btn btn-primary" onclick="window.itemListComponent.loadMore()">
                        Load More Items
                    </button>
                </div>
            ` : ''}
        `;

        // Store reference for global access
        window.itemListComponent = this;
    }

    /**
     * Render empty state
     */
    _renderEmptyState() {
        this.container.innerHTML = `
            <div class="content-header">
                <h2>📄 Vector Items</h2>
                <p class="text-muted">No vector items found in index "${escapeHtml(this.indexName)}"</p>
            </div>
            <div class="empty-state">
                <div class="empty-state-icon">📄</div>
                <h3 class="empty-state-title">No Vector Items Found</h3>
                <p class="empty-state-description">
                    This index doesn't contain any vector items yet.<br>
                    Add vector data to this index to start searching and browsing.
                </p>
                <div class="empty-state-actions">
                    <button class="btn btn-secondary" onclick="window.itemListComponent.refresh()">
                        <span class="btn-icon">🔄</span>
                        Refresh
                    </button>
                </div>
            </div>
        `;

        // Store reference for global access
        window.itemListComponent = this;
    }

    /**
     * Render error state
     */
    _renderError(error) {
        const errorMessage = error instanceof APIError ? error.getUserMessage() : formatError(error);
        const recoveryActions = error instanceof APIError ? error.getRecoveryActions() : ['Try again'];
        
        this.container.innerHTML = `
            <div class="content-header">
                <h2>📄 Vector Items</h2>
                <p class="text-muted">Failed to load items</p>
            </div>
            <div class="error-state">
                <div class="error-message">
                    <h3>Failed to Load Items</h3>
                    <p>${escapeHtml(errorMessage)}</p>
                    <div class="error-actions">
                        ${recoveryActions.map(action => 
                            `<button class="btn btn-primary" onclick="window.itemListComponent.refresh()">
                                ${escapeHtml(action)}
                            </button>`
                        ).join('')}
                    </div>
                </div>
            </div>
        `;

        // Store reference for global access
        window.itemListComponent = this;
    }

    /**
     * Create item card HTML
     */
    _createItemCard(item) {
        const metadataPreview = createMetadataPreview(item.metadata, 3);
        const metadataCount = item.metadata ? Object.keys(item.metadata).length : 0;
        const isExpanded = this.expandedItems.has(item.id);
        const similarityScore = item.similarity_score ? formatSimilarityScore(item.similarity_score) : null;

        return `
            <div class="card item-card ${isExpanded ? 'expanded' : ''}" data-item-id="${escapeHtml(item.id)}">
                <div class="card-header">
                    <div class="item-header">
                        <div class="item-icon">📄</div>
                        <div class="item-title">
                            <div class="item-id">${this.searchQuery ? this._highlightSearchTerm(item.id, this.searchQuery) : escapeHtml(item.id)}</div>
                            <div class="item-metadata-preview">
                                ${metadataCount > 0 ? `${metadataCount} metadata field${metadataCount !== 1 ? 's' : ''}` : 'No metadata'}
                            </div>
                        </div>
                        <div class="item-actions">
                            ${similarityScore ? `
                                <span class="similarity-score" title="Similarity Score">
                                    ${similarityScore}
                                </span>
                            ` : ''}
                            <button class="btn btn-sm btn-secondary" 
                                    onclick="window.itemListComponent.toggleItemDetails('${escapeHtml(item.id)}')"
                                    title="${isExpanded ? 'Hide details' : 'Show details'}">
                                <span class="btn-icon">${isExpanded ? '▼' : '▶'}</span>
                            </button>
                            <button class="btn btn-sm btn-danger" 
                                    onclick="window.itemListComponent.deleteItem('${escapeHtml(item.id)}')"
                                    title="Delete item">
                                <span class="btn-icon">🗑️</span>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="card-body">
                    <div class="item-summary">
                        <div class="summary-item">
                            <div class="summary-label">Item ID</div>
                            <div class="summary-value summary-value-mono">${truncateText(item.id, 40)}</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label">Metadata Fields</div>
                            <div class="summary-value">${metadataCount} field${metadataCount !== 1 ? 's' : ''}</div>
                        </div>
                        ${item.supported_actions ? `
                            <div class="summary-item">
                                <div class="summary-label">Actions Available</div>
                                <div class="summary-value">${item.supported_actions.length} action${item.supported_actions.length !== 1 ? 's' : ''}</div>
                            </div>
                        ` : ''}
                    </div>
                    
                    ${metadataCount > 0 ? `
                        <div class="metadata-preview">
                            <div class="preview-title">
                                <span>🏷️</span>
                                Metadata Preview
                            </div>
                            <div class="preview-content">
                                ${metadataPreview}
                            </div>
                        </div>
                    ` : ''}
                </div>
                
                <div class="item-details" style="display: ${isExpanded ? 'block' : 'none'}">
                    <div class="details-content">
                        ${this._createItemDetailsContent(item)}
                    </div>
                </div>
                
                <div class="card-footer">
                    <div class="footer-info">
                        <span class="text-muted">Click arrow to ${isExpanded ? 'hide' : 'view'} metadata</span>
                    </div>
                    <div class="footer-actions">
                        <span class="btn-icon">${isExpanded ? '▼' : '▶'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create item details content
     */
    _createItemDetailsContent(item) {
        const formattedMetadata = formatMetadata(item.metadata, {
            searchQuery: this.searchQuery,
            highlightMatches: !!this.searchQuery
        });
        
        // Debug: Check if any S3 links were detected
        const s3Links = formattedMetadata.entries.filter(entry => entry.isS3Link);
        if (s3Links.length > 0) {
            console.log('Found S3 links:', s3Links);
        }
        
        return `
            <div class="detail-section">
                <h4>Item Information</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <div class="detail-label">Item ID</div>
                        <div class="detail-value detail-value-mono">${escapeHtml(item.id)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Bucket</div>
                        <div class="detail-value detail-value-mono">${escapeHtml(this.bucketName)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Index</div>
                        <div class="detail-value detail-value-mono">${escapeHtml(this.indexName)}</div>
                    </div>
                    ${item.similarity_score ? `
                        <div class="detail-item">
                            <div class="detail-label">Similarity Score</div>
                            <div class="detail-value">${formatSimilarityScore(item.similarity_score)}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
            
            ${formattedMetadata.count > 0 ? `
                <div class="detail-section">
                    <h4>Metadata (${formattedMetadata.count} field${formattedMetadata.count !== 1 ? 's' : ''})</h4>
                    <div class="metadata-grid">
                        ${formattedMetadata.entries.map(entry => `
                            <div class="metadata-item">
                                <div class="metadata-key">${entry.highlightedKey || escapeHtml(entry.formattedKey)}</div>
                                <div class="metadata-value ${entry.type === 'object' ? 'metadata-value-code' : ''}" 
                                     title="${escapeHtml(entry.value)}">
                                    ${entry.isS3Link ? 
                                        `<a href="#" class="s3-link" onclick="event.stopPropagation(); window.itemListComponent.handleS3Link('${entry.value.replace(/'/g, "\\'")}'); return false;">
                                            ${escapeHtml(entry.formattedValue)}
                                        </a>` :
                                        (entry.highlightedValue || escapeHtml(entry.formattedValue))
                                    }
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : `
                <div class="detail-section">
                    <h4>Metadata</h4>
                    <p class="text-muted">No metadata available for this item.</p>
                </div>
            `}
            
            ${item.supported_actions && item.supported_actions.length > 0 ? `
                <div class="detail-section">
                    <h4>Supported Actions</h4>
                    <div class="supported-actions">
                        ${item.supported_actions.map(action => 
                            `<span class="action-tag">${escapeHtml(action)}</span>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
        `;
    }

    /**
     * Create skeleton loading cards
     */
    _createSkeletonCards(count) {
        return Array(count).fill(0).map(() => `
            <div class="card item-card">
                <div class="card-header">
                    <div class="item-header">
                        <div class="loading-skeleton skeleton-title"></div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="item-summary">
                        <div class="summary-item">
                            <div class="loading-skeleton skeleton-text"></div>
                        </div>
                        <div class="summary-item">
                            <div class="loading-skeleton skeleton-text"></div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Toggle item details expansion
     */
    toggleItemDetails(itemId) {
        const card = this.container.querySelector(`[data-item-id="${itemId}"]`);
        if (!card) return;
        
        const detailsSection = card.querySelector('.item-details');
        const toggleButton = card.querySelector('.item-actions .btn-secondary');
        const footerIcon = card.querySelector('.footer-actions .btn-icon');
        
        if (this.expandedItems.has(itemId)) {
            // Collapse
            this.expandedItems.delete(itemId);
            card.classList.remove('expanded');
            detailsSection.style.display = 'none';
            toggleButton.innerHTML = '<span class="btn-icon">▶</span>';
            toggleButton.title = 'Show details';
            footerIcon.textContent = '▶';
        } else {
            // Expand
            this.expandedItems.add(itemId);
            card.classList.add('expanded');
            detailsSection.style.display = 'block';
            toggleButton.innerHTML = '<span class="btn-icon">▼</span>';
            toggleButton.title = 'Hide details';
            footerIcon.textContent = '▼';
        }
    }

    /**
     * Show item details in modal
     */
    async showItemDetails(itemId) {
        try {
            showLoading('Loading item details...');
            const details = await this.apiClient.getItemDetails(this.bucketName, this.indexName, itemId);
            hideLoading();
            
            const modalContent = this._createItemDetailsModal(itemId, details);
            showModal('Item Details', modalContent, { size: 'large' });
            
        } catch (error) {
            hideLoading();
            showError('Failed to Load Details', formatError(error));
        }
    }

    /**
     * Create item details modal content
     */
    _createItemDetailsModal(itemId, details) {
        const formattedMetadata = formatMetadata(details.metadata);
        
        return `
            <div class="detail-modal">
                <div class="detail-section">
                    <h4>Item Information</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">Item ID</div>
                            <div class="detail-value detail-value-mono">${escapeHtml(itemId)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Bucket</div>
                            <div class="detail-value detail-value-mono">${escapeHtml(this.bucketName)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Index</div>
                            <div class="detail-value detail-value-mono">${escapeHtml(this.indexName)}</div>
                        </div>
                        ${details.creation_time ? `
                            <div class="detail-item">
                                <div class="detail-label">Created</div>
                                <div class="detail-value">${formatTimestamp(details.creation_time)}</div>
                            </div>
                        ` : ''}
                        ${details.vector_data ? `
                            <div class="detail-item">
                                <div class="detail-label">Vector Dimensions</div>
                                <div class="detail-value">${Array.isArray(details.vector_data) ? details.vector_data.length : 'N/A'}</div>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                ${formattedMetadata.count > 0 ? `
                    <div class="detail-section">
                        <h4>Metadata (${formattedMetadata.count} field${formattedMetadata.count !== 1 ? 's' : ''})</h4>
                        <div class="metadata-grid">
                            ${formattedMetadata.entries.map(entry => `
                                <div class="metadata-item">
                                    <div class="metadata-key">${entry.highlightedKey || escapeHtml(entry.formattedKey)}</div>
                                    <div class="metadata-value ${entry.type === 'object' ? 'metadata-value-code' : ''}" 
                                         title="${escapeHtml(entry.value)}">
                                        ${entry.isS3Link ? 
                                            `<a href="#" class="s3-link" onclick="event.stopPropagation(); window.itemListComponent.handleS3Link('${entry.value.replace(/'/g, "\\'")}'); return false;">
                                                ${escapeHtml(entry.formattedValue)}
                                            </a>` :
                                            (entry.highlightedValue || escapeHtml(entry.formattedValue))
                                        }
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${details.vector_data && Array.isArray(details.vector_data) ? `
                    <div class="detail-section">
                        <h4>Vector Data (${details.vector_data.length} dimensions)</h4>
                        <div class="vector-preview">
                            <div class="vector-stats">
                                <div class="stat-item">
                                    <div class="stat-label">Dimensions</div>
                                    <div class="stat-value">${details.vector_data.length}</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-label">Min Value</div>
                                    <div class="stat-value">${Math.min(...details.vector_data).toFixed(4)}</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-label">Max Value</div>
                                    <div class="stat-value">${Math.max(...details.vector_data).toFixed(4)}</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-label">Mean</div>
                                    <div class="stat-value">${(details.vector_data.reduce((a, b) => a + b, 0) / details.vector_data.length).toFixed(4)}</div>
                                </div>
                            </div>
                            <div class="vector-data">
                                <div class="vector-sample">
                                    <strong>First 10 values:</strong><br>
                                    <code>[${details.vector_data.slice(0, 10).map(v => v.toFixed(4)).join(', ')}${details.vector_data.length > 10 ? ', ...' : ''}]</code>
                                </div>
                            </div>
                        </div>
                    </div>
                ` : ''}
                
                ${Object.keys(details).length > 5 ? `
                    <div class="detail-section">
                        <h4>Raw Data</h4>
                        <pre class="detail-json">${formatJSON(details)}</pre>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Load more items
     */
    async loadMore() {
        const newOffset = this.currentOffset + this.currentLimit;
        await this.render(this.bucketName, this.indexName, {
            limit: this.currentLimit,
            offset: newOffset
        });
    }

    /**
     * Show load more options
     */
    showLoadMoreOptions() {
        const modalContent = `
            <div class="load-more-options">
                <div class="option-group">
                    <label for="load-limit">Items per page:</label>
                    <select id="load-limit" class="form-control">
                        <option value="25" ${this.currentLimit === 25 ? 'selected' : ''}>25</option>
                        <option value="50" ${this.currentLimit === 50 ? 'selected' : ''}>50</option>
                        <option value="100" ${this.currentLimit === 100 ? 'selected' : ''}>100</option>
                        <option value="200" ${this.currentLimit === 200 ? 'selected' : ''}>200</option>
                    </select>
                </div>
                <div class="option-group">
                    <label for="load-offset">Start from item:</label>
                    <input type="number" id="load-offset" class="form-control" 
                           value="${this.currentOffset}" min="0" step="1">
                </div>
                <div class="option-actions">
                    <button class="btn btn-primary" onclick="window.itemListComponent.applyLoadOptions()">
                        Apply
                    </button>
                </div>
            </div>
        `;
        
        showModal('Load Options', modalContent);
    }

    /**
     * Apply load options from modal
     */
    async applyLoadOptions() {
        const limitSelect = document.getElementById('load-limit');
        const offsetInput = document.getElementById('load-offset');
        
        if (limitSelect && offsetInput) {
            const newLimit = parseInt(limitSelect.value);
            const newOffset = parseInt(offsetInput.value);
            
            closeModal();
            
            await this.render(this.bucketName, this.indexName, {
                limit: newLimit,
                offset: newOffset
            });
        }
    }

    /**
     * Handle S3 link clicks
     */
    async handleS3Link(s3Uri) {
        try {
            showLoading('Loading S3 content...');
            
            // Fetch S3 content from backend
            const contentInfo = await this.apiClient.getS3Content(s3Uri);
            hideLoading();
            
            if (!contentInfo.success) {
                // Show error modal
                const modalContent = `
                    <div class="s3-content-modal">
                        <div class="s3-error">
                            <h4>❌ Unable to Load Content</h4>
                            <div class="s3-uri-display">
                                <code>${escapeHtml(s3Uri)}</code>
                            </div>
                            <div class="error-message">
                                ${escapeHtml(contentInfo.error || 'Unknown error occurred')}
                            </div>
                        </div>
                        
                        <div class="s3-actions">
                            <button class="btn btn-secondary" onclick="copyToClipboard('${escapeHtml(s3Uri)}')">
                                📋 Copy URI
                            </button>
                            <button class="btn btn-primary" onclick="window.open('https://console.aws.amazon.com/s3/object/${escapeHtml(s3Uri.replace('s3://', ''))}', '_blank')">
                                🌐 Open in AWS Console
                            </button>
                        </div>
                    </div>
                `;
                
                showModal('S3 Object Content', modalContent, { size: 'large' });
                return;
            }
            
            // Create content modal based on content type
            let contentDisplay = '';
            
            if (contentInfo.is_image) {
                // Display image
                contentDisplay = `
                    <div class="s3-image-content">
                        <img src="data:${contentInfo.content_type};base64,${contentInfo.content_base64}" 
                             alt="S3 Image" 
                             style="max-width: 100%; max-height: 500px; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    </div>
                `;
            } else if (contentInfo.is_text) {
                // Display text content
                contentDisplay = `
                    <div class="s3-text-content">
                        <div class="text-content-container">
                            <pre class="text-content">${escapeHtml(contentInfo.content)}</pre>
                        </div>
                    </div>
                `;
            } else {
                // Binary content - show info only
                contentDisplay = `
                    <div class="s3-binary-content">
                        <div class="binary-info">
                            <p>📄 Binary file content cannot be displayed directly.</p>
                            <p><strong>Content Type:</strong> ${escapeHtml(contentInfo.content_type)}</p>
                            <p><strong>Size:</strong> ${formatBytes(contentInfo.size)}</p>
                        </div>
                    </div>
                `;
            }
            
            const modalContent = `
                <div class="s3-content-modal">
                    <div class="s3-content-header">
                        <h4>📄 S3 Object Content</h4>
                        <div class="s3-uri-display">
                            <code>${escapeHtml(s3Uri)}</code>
                        </div>
                        <div class="s3-meta-info">
                            <span class="meta-item"><strong>Type:</strong> ${escapeHtml(contentInfo.content_type)}</span>
                            <span class="meta-item"><strong>Size:</strong> ${formatBytes(contentInfo.size)}</span>
                        </div>
                    </div>
                    
                    <div class="s3-content-body">
                        ${contentDisplay}
                    </div>
                    
                    <div class="s3-actions">
                        <button class="btn btn-secondary" onclick="copyToClipboard('${escapeHtml(s3Uri)}')">
                            📋 Copy URI
                        </button>
                        ${contentInfo.is_text ? `
                            <button class="btn btn-secondary" onclick="copyToClipboard('${escapeHtml(contentInfo.content)}')">
                                📋 Copy Content
                            </button>
                        ` : ''}
                        <button class="btn btn-primary" onclick="window.open('https://console.aws.amazon.com/s3/object/${escapeHtml(s3Uri.replace('s3://', ''))}', '_blank')">
                            🌐 Open in AWS Console
                        </button>
                    </div>
                </div>
            `;
            
            showModal('S3 Object Content', modalContent, { size: 'large' });
            
        } catch (error) {
            hideLoading();
            showError('Failed to Load S3 Content', formatError(error));
        }
    }

    /**
     * Delete item with confirmation
     */
    async deleteItem(itemId) {
        const confirmed = await showConfirm(
            'Delete Item',
            `Are you sure you want to delete the item "${itemId}"? This action cannot be undone.`,
            'Delete',
            'btn-danger'
        );
        
        if (!confirmed) return;
        
        try {
            showLoading('Deleting item...');
            await this.apiClient.deleteItem(this.bucketName, this.indexName, itemId);
            hideLoading();
            
            showToast('success', 'Item Deleted', `Item "${itemId}" has been deleted successfully.`);
            
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
        this.stateManager.removeAllListeners('refreshItems');
        this.expandedItems.clear();
        if (window.itemListComponent === this) {
            delete window.itemListComponent;
        }
    }
}

// Export for use in other modules
window.ItemListComponent = ItemListComponent;