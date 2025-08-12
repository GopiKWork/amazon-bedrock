/**
 * S3 Vector Browser State Manager
 * Manages application state and data caching
 */

class StateManager {
    constructor() {
        this.state = new Map();
        this.cache = new Map();
        this.listeners = new Map();
        this.awsContext = {
            region: null,
            accountId: null,
            serviceType: null
        };
        
        // Default cache TTL values (in milliseconds)
        this.cacheTTL = {
            health: 30 * 1000,        // 30 seconds
            buckets: 5 * 60 * 1000,   // 5 minutes
            indexes: 5 * 60 * 1000,   // 5 minutes
            items: 3 * 60 * 1000,     // 3 minutes
            itemDetails: 10 * 60 * 1000, // 10 minutes
            bucketDetails: 10 * 60 * 1000, // 10 minutes
            indexDetails: 10 * 60 * 1000   // 10 minutes
        };
        
        this._setupPeriodicCleanup();
    }

    /**
     * Set state value and notify listeners
     */
    setState(key, value) {
        const oldValue = this.state.get(key);
        this.state.set(key, value);
        
        // Notify listeners if value changed
        if (oldValue !== value) {
            this._notifyListeners(key, value, oldValue);
        }
    }

    /**
     * Get state value
     */
    getState(key, defaultValue = null) {
        return this.state.has(key) ? this.state.get(key) : defaultValue;
    }

    /**
     * Check if state key exists
     */
    hasState(key) {
        return this.state.has(key);
    }

    /**
     * Delete state key
     */
    deleteState(key) {
        const oldValue = this.state.get(key);
        const deleted = this.state.delete(key);
        
        if (deleted) {
            this._notifyListeners(key, undefined, oldValue);
        }
        
        return deleted;
    }

    /**
     * Clear all state
     */
    clearState() {
        const keys = Array.from(this.state.keys());
        this.state.clear();
        
        // Notify listeners of cleared keys
        keys.forEach(key => {
            this._notifyListeners(key, undefined, this.state.get(key));
        });
    }

    /**
     * Cache data with TTL
     */
    cacheData(key, data, ttl = null) {
        const cacheEntry = {
            data: data,
            timestamp: Date.now(),
            ttl: ttl || this._getDefaultTTL(key)
        };
        
        this.cache.set(key, cacheEntry);
        
        // Also update state if it's a state key
        if (this._isStateKey(key)) {
            this.setState(key, data);
        }
    }

    /**
     * Get cached data if still valid
     */
    getCachedData(key) {
        const cacheEntry = this.cache.get(key);
        
        if (!cacheEntry) {
            return null;
        }
        
        // Check if cache is still valid
        const now = Date.now();
        if (now - cacheEntry.timestamp > cacheEntry.ttl) {
            this.cache.delete(key);
            return null;
        }
        
        return cacheEntry.data;
    }

    /**
     * Check if cached data exists and is valid
     */
    hasCachedData(key) {
        return this.getCachedData(key) !== null;
    }

    /**
     * Clear cache entries matching pattern
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

    /**
     * Get cache statistics
     */
    getCacheStats() {
        const now = Date.now();
        let validEntries = 0;
        let expiredEntries = 0;
        let totalSize = 0;
        
        for (const [key, entry] of this.cache) {
            totalSize += this._estimateSize(entry.data);
            
            if (now - entry.timestamp > entry.ttl) {
                expiredEntries++;
            } else {
                validEntries++;
            }
        }
        
        return {
            totalEntries: this.cache.size,
            validEntries,
            expiredEntries,
            estimatedSize: totalSize
        };
    }

    /**
     * Set AWS context information
     */
    setAWSContext(region, accountId, serviceType = null) {
        const oldContext = { ...this.awsContext };
        
        this.awsContext = {
            region: region || null,
            accountId: accountId || null,
            serviceType: serviceType || null
        };
        
        // Notify listeners of context change
        this._notifyListeners('awsContext', this.awsContext, oldContext);
        
        // Also set as state
        this.setState('awsContext', this.awsContext);
    }

    /**
     * Get AWS context information
     */
    getAWSContext() {
        return { ...this.awsContext };
    }

    /**
     * Extract AWS context from resource ARN
     */
    extractAWSContextFromARN(arn) {
        if (!arn || typeof arn !== 'string') {
            return null;
        }
        
        // ARN format: arn:partition:service:region:account-id:resource-type/resource-id
        const arnParts = arn.split(':');
        
        if (arnParts.length >= 5 && arnParts[0] === 'arn') {
            const region = arnParts[3] || null;
            const accountId = arnParts[4] || null;
            
            return { region, accountId };
        }
        
        return null;
    }

    /**
     * Update AWS context from resource data
     */
    updateAWSContextFromResource(resource) {
        if (!resource) return;
        
        let contextUpdated = false;
        
        // Try to extract from ARN
        if (resource.arn) {
            const arnContext = this.extractAWSContextFromARN(resource.arn);
            if (arnContext) {
                if (arnContext.region && !this.awsContext.region) {
                    this.awsContext.region = arnContext.region;
                    contextUpdated = true;
                }
                if (arnContext.accountId && !this.awsContext.accountId) {
                    this.awsContext.accountId = arnContext.accountId;
                    contextUpdated = true;
                }
            }
        }
        
        // Try to extract from region field
        if (resource.region && !this.awsContext.region) {
            this.awsContext.region = resource.region;
            contextUpdated = true;
        }
        
        if (contextUpdated) {
            this._notifyListeners('awsContext', this.awsContext);
            this.setState('awsContext', this.awsContext);
        }
    }

    /**
     * Set current navigation context
     */
    setCurrentView(view, params = {}) {
        const currentView = {
            view,
            params: { ...params },
            timestamp: Date.now()
        };
        
        this.setState('currentView', currentView);
    }

    /**
     * Get current navigation context
     */
    getCurrentView() {
        return this.getState('currentView', { view: 'buckets', params: {} });
    }

    /**
     * Add state change listener
     */
    addListener(key, listener) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        
        this.listeners.get(key).add(listener);
    }

    /**
     * Remove state change listener
     */
    removeListener(key, listener) {
        if (this.listeners.has(key)) {
            this.listeners.get(key).delete(listener);
            
            // Clean up empty listener sets
            if (this.listeners.get(key).size === 0) {
                this.listeners.delete(key);
            }
        }
    }

    /**
     * Remove all listeners for a key
     */
    removeAllListeners(key) {
        this.listeners.delete(key);
    }

    /**
     * Get loading state for a resource
     */
    isLoading(key) {
        return this.getState(`loading_${key}`, false);
    }

    /**
     * Set loading state for a resource
     */
    setLoading(key, loading = true) {
        this.setState(`loading_${key}`, loading);
    }

    /**
     * Get error state for a resource
     */
    getError(key) {
        return this.getState(`error_${key}`, null);
    }

    /**
     * Set error state for a resource
     */
    setError(key, error = null) {
        this.setState(`error_${key}`, error);
    }

    /**
     * Clear error state for a resource
     */
    clearError(key) {
        this.deleteState(`error_${key}`);
    }

    /**
     * Get resource data with loading and error states
     */
    getResourceState(key) {
        return {
            data: this.getCachedData(key),
            loading: this.isLoading(key),
            error: this.getError(key),
            hasData: this.hasCachedData(key)
        };
    }

    /**
     * Set resource data and clear loading/error states
     */
    setResourceData(key, data) {
        this.cacheData(key, data);
        this.setLoading(key, false);
        this.clearError(key);
    }

    /**
     * Set resource error and clear loading state
     */
    setResourceError(key, error) {
        this.setError(key, error);
        this.setLoading(key, false);
    }

    // ============ PRIVATE METHODS ============

    /**
     * Notify state change listeners
     */
    _notifyListeners(key, newValue, oldValue) {
        if (this.listeners.has(key)) {
            const keyListeners = this.listeners.get(key);
            
            keyListeners.forEach(listener => {
                try {
                    listener(newValue, oldValue, key);
                } catch (error) {
                    console.error(`State listener error for key "${key}":`, error);
                }
            });
        }
    }

    /**
     * Get default TTL for cache key
     */
    _getDefaultTTL(key) {
        // Check for specific patterns
        if (key.includes('health')) return this.cacheTTL.health;
        if (key.includes('buckets') && key.includes('details')) return this.cacheTTL.bucketDetails;
        if (key.includes('buckets')) return this.cacheTTL.buckets;
        if (key.includes('indexes') && key.includes('details')) return this.cacheTTL.indexDetails;
        if (key.includes('indexes')) return this.cacheTTL.indexes;
        if (key.includes('items') && key.includes('details')) return this.cacheTTL.itemDetails;
        if (key.includes('items')) return this.cacheTTL.items;
        
        // Default TTL
        return 5 * 60 * 1000; // 5 minutes
    }

    /**
     * Check if key should also be stored in state
     */
    _isStateKey(key) {
        const stateKeys = ['awsContext', 'currentView', 'buckets', 'health'];
        return stateKeys.some(stateKey => key.includes(stateKey));
    }

    /**
     * Estimate size of data for cache statistics
     */
    _estimateSize(data) {
        try {
            return JSON.stringify(data).length * 2; // Rough estimate in bytes
        } catch {
            return 0;
        }
    }

    /**
     * Setup periodic cache cleanup
     */
    _setupPeriodicCleanup() {
        // Clean up expired cache entries every 5 minutes
        setInterval(() => {
            this._cleanupExpiredCache();
        }, 5 * 60 * 1000);
    }

    /**
     * Clean up expired cache entries
     */
    _cleanupExpiredCache() {
        const now = Date.now();
        const keysToDelete = [];
        
        for (const [key, entry] of this.cache) {
            if (now - entry.timestamp > entry.ttl) {
                keysToDelete.push(key);
            }
        }
        
        keysToDelete.forEach(key => this.cache.delete(key));
        
        if (keysToDelete.length > 0) {
            console.log(`Cleaned up ${keysToDelete.length} expired cache entries`);
        }
    }

    /**
     * Destroy state manager and cleanup
     */
    destroy() {
        this.state.clear();
        this.cache.clear();
        this.listeners.clear();
    }
}

// Export for use in other modules
window.StateManager = StateManager;