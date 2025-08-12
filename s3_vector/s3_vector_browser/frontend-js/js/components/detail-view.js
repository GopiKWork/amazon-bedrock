/**
 * S3 Vector Browser Detail View Component
 * Displays comprehensive resource information in modal dialogs
 */

class DetailViewComponent {
    constructor(apiClient, stateManager) {
        this.apiClient = apiClient;
        this.stateManager = stateManager;
    }

    /**
     * Show bucket details modal
     */
    async showBucketDetails(bucketName) {
        try {
            showLoading('Loading bucket details...');
            const details = await this.apiClient.getBucketDetails(bucketName);
            hideLoading();
            
            const modalContent = this._createBucketDetailsContent(bucketName, details);
            showModal('Bucket Details', modalContent, { size: 'large' });
            
        } catch (error) {
            hideLoading();
            showError('Failed to Load Bucket Details', formatError(error));
        }
    }

    /**
     * Show index details modal
     */
    async showIndexDetails(bucketName, indexName) {
        try {
            showLoading('Loading index details...');
            const details = await this.apiClient.getIndexDetails(bucketName, indexName);
            hideLoading();
            
            const modalContent = this._createIndexDetailsContent(bucketName, indexName, details);
            showModal('Index Details', modalContent, { size: 'large' });
            
        } catch (error) {
            hideLoading();
            showError('Failed to Load Index Details', formatError(error));
        }
    }

    /**
     * Show item details modal
     */
    async showItemDetails(bucketName, indexName, itemId) {
        try {
            showLoading('Loading item details...');
            const details = await this.apiClient.getItemDetails(bucketName, indexName, itemId);
            hideLoading();
            
            const modalContent = this._createItemDetailsContent(bucketName, indexName, itemId, details);
            showModal('Item Details', modalContent, { size: 'large' });
            
        } catch (error) {
            hideLoading();
            showError('Failed to Load Item Details', formatError(error));
        }
    }

    /**
     * Create bucket details modal content
     */
    _createBucketDetailsContent(bucketName, details) {
        const arnInfo = formatARN(details.arn || '');
        const accountId = extractAccountFromARN(details.arn) || 'Unknown';
        const region = extractRegionFromARN(details.arn) || details.region || 'Unknown';
        
        return `
            <div class="detail-modal">
                <div class="detail-section">
                    <h4>📦 Basic Information</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">Bucket Name</div>
                            <div class="detail-value detail-value-mono">${escapeHtml(bucketName)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">ARN</div>
                            <div class="detail-value detail-value-mono" title="${escapeHtml(details.arn || '')}">
                                ${escapeHtml(details.arn || 'N/A')}
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Region</div>
                            <div class="detail-value">
                                <span class="region-badge">${region}</span>
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Account ID</div>
                            <div class="detail-value detail-value-mono">${accountId}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Created</div>
                            <div class="detail-value">${formatTimestamp(details.creation_time)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Relative Time</div>
                            <div class="detail-value">${formatRelativeTime(details.creation_time)}</div>
                        </div>
                    </div>
                </div>
                
                ${details.supported_actions && details.supported_actions.length > 0 ? `
                    <div class="detail-section">
                        <h4>⚙️ Supported Actions</h4>
                        <div class="supported-actions">
                            ${details.supported_actions.map(action => 
                                `<span class="action-tag">${escapeHtml(action)}</span>`
                            ).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${this._createARNAnalysisSection(details.arn)}
                
                ${Object.keys(details).length > 6 ? `
                    <div class="detail-section">
                        <h4>🔍 Raw Data</h4>
                        <div class="json-viewer">
                            <pre class="detail-json">${formatJSON(details)}</pre>
                        </div>
                        <div class="json-actions">
                            <button class="btn btn-sm btn-secondary" onclick="copyToClipboard('${escapeHtml(JSON.stringify(details, null, 2))}')">
                                📋 Copy JSON
                            </button>
                            <button class="btn btn-sm btn-secondary" onclick="downloadAsFile('${escapeHtml(JSON.stringify(details, null, 2))}', 'bucket-${escapeHtml(bucketName)}-details.json')">
                                💾 Download
                            </button>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Create index details modal content
     */
    _createIndexDetailsContent(bucketName, indexName, details) {
        const index = details.index || details;
        const arnInfo = formatARN(index.arn || '');
        const accountId = extractAccountFromARN(index.arn) || 'Unknown';
        const region = extractRegionFromARN(index.arn) || 'Unknown';
        
        return `
            <div class="detail-modal">
                <div class="detail-section">
                    <h4>📊 Basic Information</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">Index Name</div>
                            <div class="detail-value detail-value-mono">${escapeHtml(indexName)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">ARN</div>
                            <div class="detail-value detail-value-mono" title="${escapeHtml(index.arn || '')}">
                                ${escapeHtml(index.arn || 'N/A')}
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Bucket</div>
                            <div class="detail-value detail-value-mono">${escapeHtml(bucketName)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Region</div>
                            <div class="detail-value">
                                <span class="region-badge">${region}</span>
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Account ID</div>
                            <div class="detail-value detail-value-mono">${accountId}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Created</div>
                            <div class="detail-value">${formatTimestamp(index.creation_time)}</div>
                        </div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>🔧 Technical Specifications</h4>
                    <div class="tech-specs-detailed">
                        <div class="spec-card">
                            <div class="spec-header">
                                <span class="spec-icon">📐</span>
                                <h5>Vector Dimensions</h5>
                            </div>
                            <div class="spec-content">
                                <div class="spec-main-value">${formatNumber(index.dimension)}</div>
                                <div class="spec-description">
                                    Each vector in this index has ${formatNumber(index.dimension)} dimensions.
                                    ${this._getDimensionInsight(index.dimension)}
                                </div>
                            </div>
                        </div>
                        
                        <div class="spec-card">
                            <div class="spec-header">
                                <span class="spec-icon">📏</span>
                                <h5>Distance Metric</h5>
                            </div>
                            <div class="spec-content">
                                <div class="spec-main-value">${formatDistanceMetric(index.distance_metric)}</div>
                                <div class="spec-description">
                                    ${this._getDistanceMetricDescription(index.distance_metric)}
                                </div>
                            </div>
                        </div>
                        
                        <div class="spec-card">
                            <div class="spec-header">
                                <span class="spec-icon">🔢</span>
                                <h5>Data Type</h5>
                            </div>
                            <div class="spec-content">
                                <div class="spec-main-value">${formatDataType(index.data_type)}</div>
                                <div class="spec-description">
                                    ${this._getDataTypeDescription(index.data_type)}
                                </div>
                            </div>
                        </div>
                        
                        <div class="spec-card">
                            <div class="spec-header">
                                <span class="spec-icon">📊</span>
                                <h5>Item Count</h5>
                            </div>
                            <div class="spec-content">
                                <div class="spec-main-value">${formatItemCount(index.item_count)}</div>
                                <div class="spec-description">
                                    ${this._getStorageInsight(index.item_count, index.dimension)}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                ${this._createARNAnalysisSection(index.arn)}
                
                ${Object.keys(details).length > 8 ? `
                    <div class="detail-section">
                        <h4>🔍 Raw Data</h4>
                        <div class="json-viewer">
                            <pre class="detail-json">${formatJSON(details)}</pre>
                        </div>
                        <div class="json-actions">
                            <button class="btn btn-sm btn-secondary" onclick="copyToClipboard('${escapeHtml(JSON.stringify(details, null, 2))}')">
                                📋 Copy JSON
                            </button>
                            <button class="btn btn-sm btn-secondary" onclick="downloadAsFile('${escapeHtml(JSON.stringify(details, null, 2))}', 'index-${escapeHtml(indexName)}-details.json')">
                                💾 Download
                            </button>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Create item details modal content
     */
    _createItemDetailsContent(bucketName, indexName, itemId, details) {
        const formattedMetadata = formatMetadata(details.metadata);
        
        return `
            <div class="detail-modal">
                <div class="detail-section">
                    <h4>📄 Item Information</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">Item ID</div>
                            <div class="detail-value detail-value-mono">${escapeHtml(itemId)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Bucket</div>
                            <div class="detail-value detail-value-mono">${escapeHtml(bucketName)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Index</div>
                            <div class="detail-value detail-value-mono">${escapeHtml(indexName)}</div>
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
                                <div class="detail-value">${Array.isArray(details.vector_data) ? formatNumber(details.vector_data.length) : 'N/A'}</div>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                ${formattedMetadata.count > 0 ? `
                    <div class="detail-section">
                        <h4>🏷️ Metadata (${formattedMetadata.count} field${formattedMetadata.count !== 1 ? 's' : ''})</h4>
                        <div class="metadata-detailed">
                            ${formattedMetadata.entries.map(entry => `
                                <div class="metadata-card">
                                    <div class="metadata-card-header">
                                        <span class="metadata-key-detailed">${escapeHtml(entry.formattedKey)}</span>
                                        <span class="metadata-type-badge">${entry.type}</span>
                                    </div>
                                    <div class="metadata-card-content">
                                        <div class="metadata-value-detailed ${entry.type === 'object' ? 'metadata-value-code' : ''}" 
                                             title="${escapeHtml(entry.value)}">
                                            ${entry.type === 'object' ? 
                                                `<pre>${escapeHtml(JSON.stringify(entry.value, null, 2))}</pre>` :
                                                entry.isS3Link ? 
                                                    `<a href="#" class="s3-link" onclick="handleS3LinkFromModal('${escapeHtml(entry.value)}'); return false;">
                                                        ${escapeHtml(entry.formattedValue)}
                                                    </a>` :
                                                    escapeHtml(entry.formattedValue)
                                            }
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : `
                    <div class="detail-section">
                        <h4>🏷️ Metadata</h4>
                        <div class="empty-metadata">
                            <p class="text-muted">No metadata available for this item.</p>
                        </div>
                    </div>
                `}
                
                ${details.vector_data && Array.isArray(details.vector_data) ? `
                    <div class="detail-section">
                        <h4>🔢 Vector Data Analysis</h4>
                        ${this._createVectorAnalysis(details.vector_data)}
                    </div>
                ` : ''}
                
                <div class="detail-section">
                    <h4>🔍 Raw Data</h4>
                    <div class="json-viewer">
                        <pre class="detail-json">${formatJSON(details)}</pre>
                    </div>
                    <div class="json-actions">
                        <button class="btn btn-sm btn-secondary" onclick="copyToClipboard('${escapeHtml(JSON.stringify(details, null, 2))}')">
                            📋 Copy JSON
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="downloadAsFile('${escapeHtml(JSON.stringify(details, null, 2))}', 'item-${escapeHtml(itemId)}-details.json')">
                            💾 Download
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create ARN analysis section
     */
    _createARNAnalysisSection(arn) {
        if (!arn) return '';
        
        const arnInfo = formatARN(arn);
        if (!arnInfo.parts) return '';
        
        return `
            <div class="detail-section">
                <h4>🔗 ARN Analysis</h4>
                <div class="arn-breakdown">
                    <div class="arn-part">
                        <div class="arn-part-label">Partition</div>
                        <div class="arn-part-value">${escapeHtml(arnInfo.parts.partition)}</div>
                    </div>
                    <div class="arn-part">
                        <div class="arn-part-label">Service</div>
                        <div class="arn-part-value">${escapeHtml(arnInfo.parts.service)}</div>
                    </div>
                    <div class="arn-part">
                        <div class="arn-part-label">Region</div>
                        <div class="arn-part-value">${escapeHtml(arnInfo.parts.region || 'Global')}</div>
                    </div>
                    <div class="arn-part">
                        <div class="arn-part-label">Account</div>
                        <div class="arn-part-value">${escapeHtml(arnInfo.parts.accountId || 'N/A')}</div>
                    </div>
                    <div class="arn-part">
                        <div class="arn-part-label">Resource</div>
                        <div class="arn-part-value">${escapeHtml(arnInfo.parts.resource)}</div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create vector data analysis
     */
    _createVectorAnalysis(vectorData) {
        const stats = this._calculateVectorStats(vectorData);
        
        return `
            <div class="vector-analysis">
                <div class="vector-stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Dimensions</div>
                        <div class="stat-value">${formatNumber(vectorData.length)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Min Value</div>
                        <div class="stat-value">${stats.min.toFixed(6)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Max Value</div>
                        <div class="stat-value">${stats.max.toFixed(6)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Mean</div>
                        <div class="stat-value">${stats.mean.toFixed(6)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Std Dev</div>
                        <div class="stat-value">${stats.stdDev.toFixed(6)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">L2 Norm</div>
                        <div class="stat-value">${stats.l2Norm.toFixed(6)}</div>
                    </div>
                </div>
                
                <div class="vector-preview">
                    <h5>Vector Preview</h5>
                    <div class="vector-sample">
                        <strong>First 20 values:</strong><br>
                        <code class="vector-values">
                            [${vectorData.slice(0, 20).map(v => v.toFixed(4)).join(', ')}${vectorData.length > 20 ? ', ...' : ''}]
                        </code>
                    </div>
                    ${vectorData.length > 20 ? `
                        <div class="vector-sample">
                            <strong>Last 10 values:</strong><br>
                            <code class="vector-values">
                                [..., ${vectorData.slice(-10).map(v => v.toFixed(4)).join(', ')}]
                            </code>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Calculate vector statistics
     */
    _calculateVectorStats(vectorData) {
        const n = vectorData.length;
        const min = Math.min(...vectorData);
        const max = Math.max(...vectorData);
        const sum = vectorData.reduce((a, b) => a + b, 0);
        const mean = sum / n;
        
        const variance = vectorData.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / n;
        const stdDev = Math.sqrt(variance);
        
        const l2Norm = Math.sqrt(vectorData.reduce((acc, val) => acc + val * val, 0));
        
        return { min, max, mean, stdDev, l2Norm };
    }

    /**
     * Get dimension insight
     */
    _getDimensionInsight(dimension) {
        if (dimension <= 100) {
            return 'Low-dimensional space, suitable for simple embeddings.';
        } else if (dimension <= 512) {
            return 'Medium-dimensional space, common for text embeddings.';
        } else if (dimension <= 1536) {
            return 'High-dimensional space, typical for advanced language models.';
        } else {
            return 'Very high-dimensional space, used for complex multimodal embeddings.';
        }
    }

    /**
     * Get distance metric description
     */
    _getDistanceMetricDescription(metric) {
        const descriptions = {
            'cosine': 'Measures the cosine of the angle between vectors. Good for normalized data and text similarity.',
            'euclidean': 'Measures straight-line distance between points. Sensitive to magnitude differences.',
            'dot_product': 'Measures the dot product similarity. Efficient for normalized vectors.',
            'manhattan': 'Measures city-block distance. Less sensitive to outliers than Euclidean.',
            'l1': 'L1 norm distance, same as Manhattan distance.',
            'l2': 'L2 norm distance, same as Euclidean distance.'
        };
        return descriptions[metric?.toLowerCase()] || 'Custom distance metric for specialized similarity calculations.';
    }

    /**
     * Get data type description
     */
    _getDataTypeDescription(dataType) {
        const descriptions = {
            'float32': '32-bit floating point. Good balance of precision and storage efficiency.',
            'float64': '64-bit floating point. Maximum precision but uses more storage.',
            'int8': '8-bit integer. Very compact but limited range (-128 to 127).',
            'int16': '16-bit integer. Compact with moderate range (-32,768 to 32,767).',
            'int32': '32-bit integer. Standard integer with large range.',
            'uint8': '8-bit unsigned integer. Range 0 to 255, often used for normalized data.',
            'uint16': '16-bit unsigned integer. Range 0 to 65,535.',
            'uint32': '32-bit unsigned integer. Large positive range.'
        };
        return descriptions[dataType?.toLowerCase()] || 'Custom data type for specialized vector storage.';
    }

    /**
     * Get storage insight
     */
    _getStorageInsight(itemCount, dimension) {
        if (!itemCount || !dimension) return 'Storage information not available.';
        
        const bytesPerItem = (dimension * 4) + 100; // Rough estimate
        const totalBytes = itemCount * bytesPerItem;
        const formattedSize = formatBytes(totalBytes);
        
        return `Estimated storage: ${formattedSize} (${formatNumber(itemCount)} items × ${formatNumber(dimension)} dimensions)`;
    }
}

// Export for use in other modules
window.DetailViewComponent = DetailViewComponent;