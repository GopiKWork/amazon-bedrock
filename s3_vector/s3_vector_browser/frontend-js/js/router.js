/**
 * S3 Vector Browser Router
 * Handles client-side navigation and URL management
 */

class Router {
    constructor() {
        this.routes = new Map();
        this.currentRoute = null;
        this.currentParams = {};
        this.listeners = new Set();
        this.isNavigating = false;
        
        // Initialize router
        this._setupEventListeners();
        this._defineRoutes();
    }

    /**
     * Define application routes
     */
    _defineRoutes() {
        this.routes.set('', {
            pattern: /^$/,
            handler: 'buckets',
            title: 'S3 Vector Browser',
            breadcrumb: []
        });
        
        this.routes.set('buckets', {
            pattern: /^buckets$/,
            handler: 'buckets',
            title: 'Vector Buckets',
            breadcrumb: [
                { label: 'Buckets', path: '#/buckets', current: true }
            ]
        });
        
        this.routes.set('indexes', {
            pattern: /^buckets\/([^\/]+)$/,
            handler: 'indexes',
            title: 'Vector Indexes',
            params: ['bucketName'],
            breadcrumb: (params) => [
                { label: 'Buckets', path: '#/buckets' },
                { label: params.bucketName, path: `#/buckets/${params.bucketName}`, current: true }
            ]
        });
        
        this.routes.set('items', {
            pattern: /^buckets\/([^\/]+)\/indexes\/([^\/]+)$/,
            handler: 'items',
            title: 'Vector Items',
            params: ['bucketName', 'indexName'],
            breadcrumb: (params) => [
                { label: 'Buckets', path: '#/buckets' },
                { label: params.bucketName, path: `#/buckets/${params.bucketName}` },
                { label: params.indexName, path: `#/buckets/${params.bucketName}/indexes/${params.indexName}`, current: true }
            ]
        });
        
        this.routes.set('item-details', {
            pattern: /^buckets\/([^\/]+)\/indexes\/([^\/]+)\/items\/([^\/]+)$/,
            handler: 'item-details',
            title: 'Item Details',
            params: ['bucketName', 'indexName', 'itemId'],
            breadcrumb: (params) => [
                { label: 'Buckets', path: '#/buckets' },
                { label: params.bucketName, path: `#/buckets/${params.bucketName}` },
                { label: params.indexName, path: `#/buckets/${params.bucketName}/indexes/${params.indexName}` },
                { label: params.itemId, path: `#/buckets/${params.bucketName}/indexes/${params.indexName}/items/${params.itemId}`, current: true }
            ]
        });
    }

    /**
     * Setup event listeners for navigation
     */
    _setupEventListeners() {
        // Listen for hash changes
        window.addEventListener('hashchange', () => {
            this._handleNavigation();
        });

        // Listen for page load
        window.addEventListener('load', () => {
            this._handleNavigation();
        });

        // Listen for popstate (back/forward buttons)
        window.addEventListener('popstate', (event) => {
            if (event.state && event.state.route) {
                this._handleNavigation();
            }
        });

        // Intercept clicks on navigation links
        document.addEventListener('click', (event) => {
            const link = event.target.closest('a[href^="#/"]');
            if (link) {
                event.preventDefault();
                this.navigate(link.getAttribute('href'));
            }
        });
    }

    /**
     * Handle navigation events
     */
    async _handleNavigation() {
        if (this.isNavigating) return;
        
        this.isNavigating = true;
        
        try {
            const hash = window.location.hash.slice(1); // Remove #
            const path = hash.startsWith('/') ? hash.slice(1) : hash; // Remove leading /
            
            const route = this._matchRoute(path);
            
            if (!route) {
                console.warn(`No route found for path: ${path}`);
                this.navigate('#/buckets', true);
                return;
            }

            // Extract parameters
            const params = this._extractParams(route, path);
            
            // Update current route info
            this.currentRoute = route;
            this.currentParams = params;
            
            // Update document title
            this._updateTitle(route, params);
            
            // Update browser history
            this._updateHistory(path, route, params);
            
            // Notify listeners
            await this._notifyListeners(route.handler, params);
            
        } catch (error) {
            console.error('Navigation error:', error);
            this._handleNavigationError(error);
        } finally {
            this.isNavigating = false;
        }
    }

    /**
     * Match current path to a route
     */
    _matchRoute(path) {
        for (const [name, route] of this.routes) {
            if (route.pattern.test(path)) {
                return { ...route, name };
            }
        }
        return null;
    }

    /**
     * Extract parameters from path using route pattern
     */
    _extractParams(route, path) {
        const params = {};
        
        if (route.params) {
            const matches = path.match(route.pattern);
            if (matches) {
                route.params.forEach((paramName, index) => {
                    params[paramName] = decodeURIComponent(matches[index + 1]);
                });
            }
        }
        
        return params;
    }

    /**
     * Update document title
     */
    _updateTitle(route, params) {
        let title = route.title;
        
        if (params && Object.keys(params).length > 0) {
            // Add context to title
            if (params.bucketName) {
                title += ` - ${params.bucketName}`;
            }
            if (params.indexName) {
                title += ` / ${params.indexName}`;
            }
            if (params.itemId) {
                title += ` / ${params.itemId}`;
            }
        }
        
        document.title = title;
    }

    /**
     * Update browser history
     */
    _updateHistory(path, route, params) {
        const state = {
            route: route.name,
            params: params,
            timestamp: Date.now()
        };
        
        const url = `#/${path}`;
        
        // Only push state if it's different from current
        if (window.location.hash !== url) {
            history.pushState(state, document.title, url);
        } else {
            history.replaceState(state, document.title, url);
        }
    }

    /**
     * Notify route change listeners
     */
    async _notifyListeners(handler, params) {
        const routeData = {
            handler,
            params,
            breadcrumb: this.getBreadcrumb()
        };
        
        for (const listener of this.listeners) {
            try {
                await listener(routeData);
            } catch (error) {
                console.error('Route listener error:', error);
            }
        }
    }

    /**
     * Handle navigation errors
     */
    _handleNavigationError(error) {
        console.error('Navigation failed:', error);
        
        // Show error to user
        if (window.showError) {
            window.showError('Navigation Error', 'Failed to navigate to the requested page.');
        }
        
        // Fallback to buckets view
        setTimeout(() => {
            this.navigate('#/buckets', true);
        }, 1000);
    }

    /**
     * Navigate to a specific path
     */
    navigate(path, replace = false) {
        if (this.isNavigating) return;
        
        // Normalize path
        if (!path.startsWith('#/')) {
            path = '#/' + path.replace(/^\/+/, '');
        }
        
        if (replace) {
            window.location.replace(path);
        } else {
            window.location.hash = path;
        }
    }

    /**
     * Navigate back in history
     */
    back() {
        if (window.history.length > 1) {
            window.history.back();
        } else {
            this.navigate('#/buckets');
        }
    }

    /**
     * Navigate forward in history
     */
    forward() {
        window.history.forward();
    }

    /**
     * Get current breadcrumb trail
     */
    getBreadcrumb() {
        if (!this.currentRoute || !this.currentRoute.breadcrumb) {
            return [];
        }
        
        if (typeof this.currentRoute.breadcrumb === 'function') {
            return this.currentRoute.breadcrumb(this.currentParams);
        }
        
        return this.currentRoute.breadcrumb;
    }

    /**
     * Get current route information
     */
    getCurrentRoute() {
        return {
            name: this.currentRoute?.name,
            handler: this.currentRoute?.handler,
            params: { ...this.currentParams },
            breadcrumb: this.getBreadcrumb()
        };
    }

    /**
     * Check if currently on a specific route
     */
    isCurrentRoute(routeName) {
        return this.currentRoute?.name === routeName;
    }

    /**
     * Generate URL for a route with parameters
     */
    generateUrl(routeName, params = {}) {
        const route = this.routes.get(routeName);
        if (!route) {
            console.warn(`Route not found: ${routeName}`);
            return '#/buckets';
        }
        
        let path = '';
        
        switch (routeName) {
            case 'buckets':
                path = 'buckets';
                break;
            case 'indexes':
                if (params.bucketName) {
                    path = `buckets/${encodeURIComponent(params.bucketName)}`;
                }
                break;
            case 'items':
                if (params.bucketName && params.indexName) {
                    path = `buckets/${encodeURIComponent(params.bucketName)}/indexes/${encodeURIComponent(params.indexName)}`;
                }
                break;
            case 'item-details':
                if (params.bucketName && params.indexName && params.itemId) {
                    path = `buckets/${encodeURIComponent(params.bucketName)}/indexes/${encodeURIComponent(params.indexName)}/items/${encodeURIComponent(params.itemId)}`;
                }
                break;
            default:
                path = 'buckets';
        }
        
        return `#/${path}`;
    }

    /**
     * Add route change listener
     */
    addListener(listener) {
        if (typeof listener === 'function') {
            this.listeners.add(listener);
        }
    }

    /**
     * Remove route change listener
     */
    removeListener(listener) {
        this.listeners.delete(listener);
    }

    /**
     * Initialize router (call after DOM is ready)
     */
    init() {
        // Handle initial navigation
        this._handleNavigation();
    }

    /**
     * Destroy router and cleanup
     */
    destroy() {
        this.listeners.clear();
        // Event listeners are automatically cleaned up when page unloads
    }
}

// Export for use in other modules
window.Router = Router;