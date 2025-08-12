/**
 * S3 Vector Browser API Client
 * Handles all communication with the FastAPI backend
 */

class APIClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.cache = new Map();
        this.requestQueue = new Map();
        this.defaultCacheTTL = 5 * 60 * 1000; // 5 minutes
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1 second
    }

    /**
     * Make HTTP request with caching, deduplication, and error handling
     */
    async _makeRequest(method, endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const cacheKey = `${method}:${endpoint}:${JSON.stringify(options.params || {})}`;
        
        // Check cache first for GET requests
        if (method === 'GET' && this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < (options.cacheTTL || this.defaultCacheTTL)) {
                return cached.data;
            }
            this.cache.delete(cacheKey);
        }

        // Deduplicate identical requests
        if (this.requestQueue.has(cacheKey)) {
            return this.requestQueue.get(cacheKey);
        }

        // Create the request promise
        const requestPromise = this._executeRequest(method, url, options);
        
        // Store in queue for deduplication
        this.requestQueue.set(cacheKey, requestPromise);

        try {
            const result = await requestPromise;
            
            // Cache successful GET requests
            if (method === 'GET' && result) {
                this.cache.set(cacheKey, {
                    data: result,
                    timestamp: Date.now()
                });
            }

            return result;
        } finally {
            // Remove from queue when done
            this.requestQueue.delete(cacheKey);
        }
    }

    /**
     * Execute HTTP request with retry logic
     */
    async _executeRequest(method, url, options = {}) {
        const requestOptions = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...options.headers
            }
        };

        // Add query parameters for GET requests
        if (method === 'GET' && options.params) {
            const searchParams = new URLSearchParams();
            Object.entries(options.params).forEach(([key, value]) => {
                if (value !== null && value !== undefined) {
                    searchParams.append(key, value.toString());
                }
            });
            if (searchParams.toString()) {
                url += `?${searchParams.toString()}`;
            }
        }

        // Add body for non-GET requests
        if (method !== 'GET' && options.data) {
            requestOptions.body = JSON.stringify(options.data);
        }

        let lastError;
        
        // Retry logic
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const response = await fetch(url, requestOptions);
                
                if (!response.ok) {
                    const errorData = await this._parseErrorResponse(response);
                    throw new APIError(
                        errorData.message || `HTTP ${response.status}: ${response.statusText}`,
                        response.status,
                        errorData.details,
                        url
                    );
                }

                // Handle empty responses
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    return null;
                }

                const data = await response.json();
                return data;

            } catch (error) {
                lastError = error;
                
                // Don't retry on client errors (4xx) except 429 (rate limit)
                if (error instanceof APIError && 
                    error.status >= 400 && 
                    error.status < 500 && 
                    error.status !== 429) {
                    throw error;
                }

                // Don't retry on the last attempt
                if (attempt === this.retryAttempts) {
                    break;
                }

                // Wait before retrying with exponential backoff
                const delay = this.retryDelay * Math.pow(2, attempt - 1);
                await this._sleep(delay);
            }
        }

        // If we get here, all retries failed
        if (lastError instanceof APIError) {
            throw lastError;
        } else {
            throw new APIError(
                'Network error: Unable to connect to the API server',
                0,
                { originalError: lastError.message },
                url
            );
        }
    }

    /**
     * Parse error response from API
     */
    async _parseErrorResponse(response) {
        try {
            const errorData = await response.json();
            return {
                message: errorData.detail || errorData.message || 'Unknown error',
                details: errorData
            };
        } catch {
            return {
                message: `HTTP ${response.status}: ${response.statusText}`,
                details: { status: response.status, statusText: response.statusText }
            };
        }
    }

    /**
     * Sleep utility for retry delays
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Clear cache entries matching a pattern
     */
    clearCache(pattern = null) {
        if (!pattern) {
            this.cache.clear();
            return;
        }

        const keysToDelete = [];
        for (const key of this.cache.keys()) {
            if (key.includes(pattern)) {
                keysToDelete.push(key);
            }
        }
        keysToDelete.forEach(key => this.cache.delete(key));
    }

    // ============ API ENDPOINTS ============

    /**
     * Check API health and get service information
     */
    async checkHealth() {
        return this._makeRequest('GET', '/health', { cacheTTL: 30000 }); // 30 seconds cache
    }

    /**
     * Get list of vector buckets
     */
    async getBuckets() {
        return this._makeRequest('GET', '/api/buckets');
    }

    /**
     * Get list of indexes in a bucket
     */
    async getIndexes(bucketName) {
        if (!bucketName) {
            throw new APIError('Bucket name is required', 400);
        }
        return this._makeRequest('GET', `/api/buckets/${encodeURIComponent(bucketName)}/indexes`);
    }

    /**
     * Get list of items in an index
     */
    async getItems(bucketName, indexName, options = {}) {
        if (!bucketName || !indexName) {
            throw new APIError('Bucket name and index name are required', 400);
        }
        
        const params = {
            limit: options.limit || 50,
            offset: options.offset || 0
        };

        return this._makeRequest(
            'GET', 
            `/api/buckets/${encodeURIComponent(bucketName)}/indexes/${encodeURIComponent(indexName)}/items`,
            { params }
        );
    }

    /**
     * Get detailed information about a bucket
     */
    async getBucketDetails(bucketName) {
        if (!bucketName) {
            throw new APIError('Bucket name is required', 400);
        }
        return this._makeRequest('GET', `/api/buckets/${encodeURIComponent(bucketName)}/details`);
    }

    /**
     * Get detailed information about an index
     */
    async getIndexDetails(bucketName, indexName) {
        if (!bucketName || !indexName) {
            throw new APIError('Bucket name and index name are required', 400);
        }
        return this._makeRequest(
            'GET', 
            `/api/buckets/${encodeURIComponent(bucketName)}/indexes/${encodeURIComponent(indexName)}/details`
        );
    }

    /**
     * Get detailed information about an item
     */
    async getItemDetails(bucketName, indexName, itemId) {
        if (!bucketName || !indexName || !itemId) {
            throw new APIError('Bucket name, index name, and item ID are required', 400);
        }
        return this._makeRequest(
            'GET', 
            `/api/buckets/${encodeURIComponent(bucketName)}/indexes/${encodeURIComponent(indexName)}/items/${encodeURIComponent(itemId)}/details`
        );
    }

    /**
     * Query vectors in an index
     */
    async queryVectors(bucketName, indexName, queryData) {
        if (!bucketName || !indexName || !queryData) {
            throw new APIError('Bucket name, index name, and query data are required', 400);
        }
        return this._makeRequest(
            'POST', 
            `/api/buckets/${encodeURIComponent(bucketName)}/indexes/${encodeURIComponent(indexName)}/query`,
            { data: queryData, cacheTTL: 0 } // Don't cache query results
        );
    }

    /**
     * Delete a vector bucket
     */
    async deleteBucket(bucketName) {
        if (!bucketName) {
            throw new APIError('Bucket name is required', 400);
        }
        
        const result = await this._makeRequest(
            'DELETE', 
            `/api/buckets/${encodeURIComponent(bucketName)}`,
            { cacheTTL: 0 }
        );
        
        // Clear related cache entries
        this.clearCache(`/api/buckets`);
        
        return result;
    }

    /**
     * Delete a vector index
     */
    async deleteIndex(bucketName, indexName) {
        if (!bucketName || !indexName) {
            throw new APIError('Bucket name and index name are required', 400);
        }
        
        const result = await this._makeRequest(
            'DELETE', 
            `/api/buckets/${encodeURIComponent(bucketName)}/indexes/${encodeURIComponent(indexName)}`,
            { cacheTTL: 0 }
        );
        
        // Clear related cache entries
        this.clearCache(`/api/buckets/${bucketName}/indexes`);
        
        return result;
    }

    /**
     * Delete a vector item
     */
    async deleteItem(bucketName, indexName, itemId) {
        if (!bucketName || !indexName || !itemId) {
            throw new APIError('Bucket name, index name, and item ID are required', 400);
        }
        
        const result = await this._makeRequest(
            'DELETE', 
            `/api/buckets/${encodeURIComponent(bucketName)}/indexes/${encodeURIComponent(indexName)}/items/${encodeURIComponent(itemId)}`,
            { cacheTTL: 0 }
        );
        
        // Clear related cache entries
        this.clearCache(`/api/buckets/${bucketName}/indexes/${indexName}/items`);
        
        return result;
    }

    /**
     * Get S3 object content
     */
    async getS3Content(s3Uri) {
        if (!s3Uri) {
            throw new APIError('S3 URI is required', 400);
        }
        
        return this._makeRequest(
            'GET', 
            '/api/s3-content',
            { 
                params: { s3_uri: s3Uri },
                cacheTTL: 2 * 60 * 1000 // Cache for 2 minutes
            }
        );
    }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
    constructor(message, status = 0, details = null, url = null) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.details = details;
        this.url = url;
        this.timestamp = new Date();
    }

    /**
     * Check if error is recoverable (can be retried)
     */
    isRecoverable() {
        // Network errors (status 0) are recoverable
        if (this.status === 0) return true;
        
        // Server errors (5xx) are recoverable
        if (this.status >= 500) return true;
        
        // Rate limiting (429) is recoverable
        if (this.status === 429) return true;
        
        // Timeout errors are recoverable
        if (this.message.includes('timeout')) return true;
        
        return false;
    }

    /**
     * Get user-friendly error message
     */
    getUserMessage() {
        switch (this.status) {
            case 0:
                return 'Unable to connect to the server. Please check your internet connection and try again.';
            case 400:
                return 'Invalid request. Please check your input and try again.';
            case 401:
                return 'Authentication required. Please check your credentials.';
            case 403:
                return 'Access denied. You don\'t have permission to perform this action.';
            case 404:
                return 'The requested resource was not found.';
            case 429:
                return 'Too many requests. Please wait a moment and try again.';
            case 500:
                return 'Server error. Please try again later.';
            case 503:
                return 'Service temporarily unavailable. Please try again later.';
            default:
                return this.message || 'An unexpected error occurred.';
        }
    }

    /**
     * Get suggested recovery actions
     */
    getRecoveryActions() {
        const actions = [];
        
        if (this.isRecoverable()) {
            actions.push('Try again');
        }
        
        switch (this.status) {
            case 0:
                actions.push('Check internet connection');
                actions.push('Verify API server is running');
                break;
            case 403:
                actions.push('Check AWS credentials');
                actions.push('Verify IAM permissions');
                break;
            case 404:
                actions.push('Verify resource exists');
                actions.push('Check resource name spelling');
                break;
            case 503:
                actions.push('Check API server status');
                actions.push('Verify S3 Vectors service availability');
                break;
        }
        
        return actions;
    }
}

// Export for use in other modules
window.APIClient = APIClient;
window.APIError = APIError;