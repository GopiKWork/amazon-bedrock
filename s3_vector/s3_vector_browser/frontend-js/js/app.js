/**
 * S3 Vector Browser Main Application
 * Initializes and coordinates all components
 */

class S3VectorBrowserApp {
    constructor() {
        this.apiClient = null;
        this.stateManager = null;
        this.router = null;
        this.breadcrumbComponent = null;
        this.bucketListComponent = null;
        this.indexListComponent = null;
        this.itemListComponent = null;
        this.isInitialized = false;
        
        // DOM elements
        this.contentContainer = null;
        this.breadcrumbContainer = null;
        this.loadingScreen = null;
        this.appContainer = null;
    }

    /**
     * Initialize the application
     */
    async init() {
        if (this.isInitialized) return;
        
        try {
            console.log('🚀 Initializing S3 Vector Browser...');
            
            // Get DOM elements
            this._getDOMElements();
            
            // Initialize core services
            this._initializeServices();
            
            // Initialize components
            this._initializeComponents();
            
            // Setup global event handlers
            this._setupGlobalEventHandlers();
            
            // Check API health and initialize AWS context
            await this._initializeAWSContext();
            
            // Start router
            this.router.init();
            
            // Hide loading screen and show app
            this._showApp();
            
            this.isInitialized = true;
            console.log('✅ S3 Vector Browser initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize S3 Vector Browser:', error);
            this._showInitializationError(error);
        }
    }

    /**
     * Get DOM elements
     */
    _getDOMElements() {
        this.contentContainer = document.getElementById('content');
        this.breadcrumbContainer = document.getElementById('breadcrumb');
        this.loadingScreen = document.getElementById('loading-screen');
        this.appContainer = document.getElementById('app');
        
        if (!this.contentContainer || !this.breadcrumbContainer) {
            throw new Error('Required DOM elements not found');
        }
    }

    /**
     * Initialize core services
     */
    _initializeServices() {
        // Initialize API client
        this.apiClient = new APIClient();
        
        // Initialize state manager
        this.stateManager = new StateManager();
        
        // Initialize router
        this.router = new Router();
        
        // Add route listener
        this.router.addListener(this._handleRouteChange.bind(this));
    }

    /**
     * Initialize UI components
     */
    _initializeComponents() {
        // Initialize breadcrumb component
        this.breadcrumbComponent = new BreadcrumbComponent(
            this.breadcrumbContainer,
            this.router,
            this.stateManager
        );
        
        // Initialize list components
        this.bucketListComponent = new BucketListComponent(
            this.contentContainer,
            this.apiClient,
            this.stateManager,
            this.router
        );
        
        this.indexListComponent = new IndexListComponent(
            this.contentContainer,
            this.apiClient,
            this.stateManager,
            this.router
        );
        
        this.itemListComponent = new ItemListComponent(
            this.contentContainer,
            this.apiClient,
            this.stateManager,
            this.router
        );
    }

    /**
     * Setup global event handlers
     */
    _setupGlobalEventHandlers() {
        // Handle refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this._handleRefresh();
            });
        }
        
        // Handle AWS context updates
        this.stateManager.addListener('awsContext', (context) => {
            this._updateAWSContextDisplay(context);
        });
        
        // Handle global errors
        window.addEventListener('error', (event) => {
            handleGlobalError(event.error, 'Global');
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            handleGlobalError(event.reason, 'Promise');
        });
        
        // Handle online/offline status
        window.addEventListener('online', () => {
            showToast('success', 'Connection Restored', 'You are back online.');
        });
        
        window.addEventListener('offline', () => {
            showToast('warning', 'Connection Lost', 'You are currently offline.');
        });
    }

    /**
     * Initialize AWS context from API
     */
    async _initializeAWSContext() {
        try {
            const health = await this.apiClient.checkHealth();
            
            if (health) {
                // Update AWS context
                this.stateManager.setAWSContext(
                    health.region,
                    null, // Account ID will be extracted from resource ARNs
                    health.service_type
                );
                
                // Update display
                this._updateAWSContextDisplay({
                    region: health.region,
                    serviceType: health.service_type
                });
                
                // Show service type info
                if (health.service_type === 'mock') {
                    showToast('info', 'Development Mode', 'Using mock data for demonstration.');
                }
            }
        } catch (error) {
            console.warn('Could not initialize AWS context:', error);
            // Don't fail initialization for this
        }
    }

    /**
     * Handle route changes
     */
    async _handleRouteChange(routeData) {
        const { handler, params } = routeData;
        
        try {
            // Update current view in state
            this.stateManager.setCurrentView(handler, params);
            
            // Route to appropriate component
            switch (handler) {
                case 'buckets':
                    await this.bucketListComponent.render();
                    break;
                    
                case 'indexes':
                    if (params.bucketName) {
                        await this.indexListComponent.render(params.bucketName);
                    } else {
                        throw new Error('Bucket name is required for indexes view');
                    }
                    break;
                    
                case 'items':
                    if (params.bucketName && params.indexName) {
                        await this.itemListComponent.render(params.bucketName, params.indexName);
                    } else {
                        throw new Error('Bucket name and index name are required for items view');
                    }
                    break;
                    
                case 'item-details':
                    if (params.bucketName && params.indexName && params.itemId) {
                        // For now, redirect to items view and show item details modal
                        await this.itemListComponent.render(params.bucketName, params.indexName);
                        setTimeout(() => {
                            this.itemListComponent.showItemDetails(params.itemId);
                        }, 500);
                    } else {
                        throw new Error('Bucket name, index name, and item ID are required for item details view');
                    }
                    break;
                    
                default:
                    console.warn(`Unknown route handler: ${handler}`);
                    this.router.navigate('#/buckets', true);
            }
            
        } catch (error) {
            console.error('Route handling error:', error);
            showError('Navigation Error', formatError(error));
            
            // Fallback to buckets view
            if (handler !== 'buckets') {
                this.router.navigate('#/buckets', true);
            }
        }
    }

    /**
     * Handle refresh action
     */
    _handleRefresh() {
        const currentView = this.stateManager.getCurrentView();
        
        switch (currentView.view) {
            case 'buckets':
                this.bucketListComponent.refresh();
                break;
            case 'indexes':
                this.indexListComponent.refresh();
                break;
            case 'items':
                this.itemListComponent.refresh();
                break;
        }
        
        showToast('info', 'Refreshing', 'Updating data...');
    }

    /**
     * Update AWS context display
     */
    _updateAWSContextDisplay(context) {
        const regionElement = document.getElementById('current-region');
        const accountElement = document.getElementById('current-account');
        const serviceElement = document.getElementById('service-type');
        
        if (regionElement) {
            regionElement.textContent = context.region || 'Unknown';
        }
        
        if (accountElement) {
            accountElement.textContent = context.accountId || 'Loading...';
        }
        
        if (serviceElement) {
            const serviceType = context.serviceType || 'Unknown';
            serviceElement.textContent = serviceType === 'mock' ? 'Mock Data' : 'S3 Vectors';
            serviceElement.className = `context-value ${serviceType === 'mock' ? 'mock-service' : 'real-service'}`;
        }
    }

    /**
     * Show the main application
     */
    _showApp() {
        if (this.loadingScreen) {
            this.loadingScreen.style.display = 'none';
        }
        
        if (this.appContainer) {
            this.appContainer.style.display = 'flex';
        }
    }

    /**
     * Show initialization error
     */
    _showInitializationError(error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        
        if (this.loadingScreen) {
            this.loadingScreen.innerHTML = `
                <div class="loading-spinner">
                    <div class="error-icon">❌</div>
                    <h3>Failed to Initialize</h3>
                    <p>${escapeHtml(errorMessage)}</p>
                    <button class="btn btn-primary" onclick="location.reload()">
                        Reload Application
                    </button>
                </div>
            `;
        }
    }

    /**
     * Destroy the application
     */
    destroy() {
        if (this.bucketListComponent) {
            this.bucketListComponent.destroy();
        }
        
        if (this.indexListComponent) {
            this.indexListComponent.destroy();
        }
        
        if (this.itemListComponent) {
            this.itemListComponent.destroy();
        }
        
        if (this.breadcrumbComponent) {
            this.breadcrumbComponent.destroy();
        }
        
        if (this.router) {
            this.router.destroy();
        }
        
        if (this.stateManager) {
            this.stateManager.destroy();
        }
        
        this.isInitialized = false;
    }

    /**
     * Get application status
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            currentRoute: this.router?.getCurrentRoute(),
            awsContext: this.stateManager?.getAWSContext(),
            cacheStats: this.stateManager?.getCacheStats()
        };
    }
}

// Global application instance
let app = null;

/**
 * Initialize application when DOM is ready
 */
function initializeApp() {
    if (app) {
        console.warn('Application already initialized');
        return;
    }
    
    app = new S3VectorBrowserApp();
    app.init().catch(error => {
        console.error('Failed to initialize application:', error);
    });
    
    // Make app globally accessible for debugging
    window.s3VectorBrowserApp = app;
}

/**
 * Application entry point
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (app) {
        app.destroy();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = S3VectorBrowserApp;
}