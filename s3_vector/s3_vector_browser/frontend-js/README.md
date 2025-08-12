# S3 Vector Browser - JavaScript Frontend

A modern, beautiful JavaScript frontend for browsing AWS S3 Vector buckets, indexes, and items. Built with vanilla JavaScript, HTML5, and CSS3 for maximum performance and compatibility.

## 🌟 Features

### 🎨 **Beautiful Modern Design**
- Clean, professional interface with consistent styling
- Responsive design that works on mobile, tablet, and desktop
- Smooth animations and transitions
- Dark/light theme support ready

### 📊 **Comprehensive AWS Context**
- Displays region, account ID, and service type prominently
- Extracts account information from resource ARNs
- Shows technical specifications for all resources
- Real-time service status indicators

### 🗂️ **Hierarchical Navigation**
- Intuitive breadcrumb navigation
- Deep linking support with browser history
- Hash-based routing for SPA experience
- Keyboard navigation support

### 📦 **Detailed Resource Views**
- **Buckets**: ARN, region, account, creation time, supported actions
- **Indexes**: Dimensions, distance metrics, data types, item counts, technical specs
- **Items**: Metadata preview, expandable details, vector data analysis

### ⚡ **Advanced Performance**
- Intelligent caching with configurable TTL
- Request deduplication and debouncing
- Lazy loading and virtual scrolling ready
- Optimized for large datasets

### 🛡️ **Robust Error Handling**
- User-friendly error messages
- Automatic retry with exponential backoff
- Recovery suggestions for common issues
- Comprehensive logging and debugging

## 🏗️ Architecture

### Component Structure
```
frontend-js/
├── index.html              # Main HTML entry point
├── css/
│   ├── main.css           # Core styles and design system
│   ├── components.css     # Component-specific styles
│   └── responsive.css     # Responsive design rules
├── js/
│   ├── app.js            # Main application controller
│   ├── api-client.js     # API communication layer
│   ├── router.js         # Client-side routing
│   ├── state-manager.js  # Application state management
│   ├── components/       # UI components
│   │   ├── bucket-list.js
│   │   ├── index-list.js
│   │   ├── item-list.js
│   │   ├── breadcrumb.js
│   │   └── loading.js
│   └── utils/
│       ├── formatters.js # Data formatting utilities
│       ├── validators.js # Input validation
│       └── helpers.js    # General helper functions
└── assets/
    ├── icons/           # SVG icons and graphics
    └── images/          # Images and logos
```

### Key Components

#### 🔌 **API Client**
- Full-featured HTTP client with caching and retry logic
- Request deduplication to prevent duplicate calls
- Comprehensive error handling with user-friendly messages
- Automatic cache invalidation on data changes

#### 🧭 **Router**
- Hash-based SPA routing with parameter support
- Browser history integration
- Deep linking and bookmarkable URLs
- Breadcrumb generation from routes

#### 🗄️ **State Manager**
- Centralized application state management
- Intelligent caching with TTL and invalidation
- AWS context tracking and extraction
- Event-driven state updates

#### 🎨 **UI Components**
- Modular, reusable component architecture
- Consistent styling and behavior patterns
- Accessibility-compliant implementations
- Mobile-first responsive design

## 🚀 Quick Start

### Prerequisites
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- S3 Vector Browser backend API running on `http://localhost:8000`

### Installation
1. **Ensure backend is running:**
   ```bash
   cd ../backend
   python run_api.py
   ```

2. **Serve the frontend:**
   ```bash
   # Option 1: Simple HTTP server (Python)
   python -m http.server 8080
   
   # Option 2: Node.js http-server
   npx http-server -p 8080
   
   # Option 3: Any other static file server
   ```

3. **Open in browser:**
   ```
   http://localhost:8080
   ```

### Development Setup
For development with live reload:
```bash
# Using live-server (recommended)
npx live-server --port=8080 --host=localhost

# Using browser-sync
npx browser-sync start --server --files="**/*" --port=8080
```

## 🎯 Usage Guide

### Navigation
- **Buckets View**: Click on bucket cards to explore indexes
- **Indexes View**: Click on index cards to view items
- **Items View**: Click on items to expand details or view in modal
- **Breadcrumbs**: Click any breadcrumb level to navigate back

### Features

#### 📦 **Bucket Management**
- View comprehensive bucket information
- See account ID, region, and creation details
- Access supported actions and operations
- Delete buckets with confirmation

#### 📊 **Index Exploration**
- View technical specifications (dimensions, metrics, data types)
- See item counts and estimated storage size
- Analyze distance metrics and vector configurations
- Manage indexes with detailed confirmations

#### 📄 **Item Browsing**
- Browse items with metadata previews
- Expand items inline for detailed views
- View full item details in modal dialogs
- Analyze vector data with statistics
- Pagination and load-more functionality

#### 🔍 **Advanced Features**
- **Search and Filter**: Coming soon
- **Vector Similarity**: View similarity scores
- **Bulk Operations**: Coming soon
- **Export Data**: Coming soon

## 🎨 Customization

### Theming
The application uses CSS custom properties for easy theming:

```css
:root {
    --primary-color: #1f77b4;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    /* ... more variables */
}
```

### Component Styling
Each component has its own CSS class namespace:
- `.bucket-*` for bucket-related styles
- `.index-*` for index-related styles
- `.item-*` for item-related styles
- `.modal-*` for modal dialogs
- `.toast-*` for notifications

### Responsive Breakpoints
```css
/* Mobile First Approach */
@media (min-width: 576px) { /* Small devices */ }
@media (min-width: 768px) { /* Medium devices */ }
@media (min-width: 992px) { /* Large devices */ }
@media (min-width: 1200px) { /* Extra large devices */ }
```

## 🔧 Configuration

### API Configuration
Update the API base URL in `js/api-client.js`:
```javascript
const API_BASE_URL = "http://localhost:8000"; // Change as needed
```

### Cache Configuration
Adjust cache TTL values in `js/state-manager.js`:
```javascript
this.cacheTTL = {
    health: 30 * 1000,        // 30 seconds
    buckets: 5 * 60 * 1000,   // 5 minutes
    indexes: 5 * 60 * 1000,   // 5 minutes
    items: 3 * 60 * 1000,     // 3 minutes
    // ... more settings
};
```

### UI Configuration
Customize pagination and display limits:
```javascript
// In item-list.js
this.currentLimit = 50; // Items per page
this.maxPreviewKeys = 3; // Metadata keys to preview
```

## 🛠️ Development

### Adding New Features

#### 1. **New API Endpoints**
Add methods to `APIClient` class:
```javascript
async getNewResource(id) {
    return this._makeRequest('GET', `/api/new-resource/${id}`);
}
```

#### 2. **New UI Components**
Create component files following the pattern:
```javascript
class NewComponent {
    constructor(container, apiClient, stateManager, router) {
        // Initialize component
    }
    
    async render(params) {
        // Render component
    }
    
    destroy() {
        // Cleanup
    }
}
```

#### 3. **New Routes**
Add routes in `router.js`:
```javascript
this.routes.set('new-route', {
    pattern: /^new-route\/([^\/]+)$/,
    handler: 'new-route',
    params: ['param1'],
    breadcrumb: (params) => [/* breadcrumb items */]
});
```

### Code Style Guidelines
- Use ES6+ features (classes, arrow functions, async/await)
- Follow consistent naming conventions (camelCase for variables, PascalCase for classes)
- Add comprehensive error handling
- Include JSDoc comments for public methods
- Use semantic HTML and ARIA attributes for accessibility

### Performance Best Practices
- Implement lazy loading for large datasets
- Use request deduplication to prevent duplicate API calls
- Cache frequently accessed data with appropriate TTL
- Optimize DOM manipulations and minimize reflows
- Use CSS transforms for animations instead of layout properties

## 🔍 Debugging

### Debug Mode
Enable debug logging by setting:
```javascript
window.DEBUG = true;
```

### Browser Developer Tools
- **Console**: View application logs and errors
- **Network**: Monitor API requests and responses
- **Application**: Inspect cache and state data
- **Performance**: Analyze rendering and JavaScript performance

### Common Issues

#### **API Connection Errors**
- Verify backend is running on correct port
- Check CORS configuration
- Ensure network connectivity

#### **Caching Issues**
- Clear browser cache and reload
- Check cache TTL settings
- Verify cache invalidation logic

#### **Performance Issues**
- Monitor network requests for duplicates
- Check for memory leaks in components
- Optimize large dataset rendering

## 📱 Browser Support

### Supported Browsers
- **Chrome**: 90+ ✅
- **Firefox**: 88+ ✅
- **Safari**: 14+ ✅
- **Edge**: 90+ ✅

### Required Features
- ES6 Classes and Modules
- Fetch API
- CSS Grid and Flexbox
- CSS Custom Properties
- History API

### Polyfills
For older browser support, include:
```html
<script src="https://polyfill.io/v3/polyfill.min.js?features=fetch,es6"></script>
```

## 🚀 Deployment

### Production Build
1. **Minify CSS and JavaScript:**
   ```bash
   # Using terser for JS
   npx terser js/app.js -o js/app.min.js
   
   # Using cssnano for CSS
   npx cssnano css/main.css css/main.min.css
   ```

2. **Update HTML references:**
   ```html
   <link rel="stylesheet" href="css/main.min.css">
   <script src="js/app.min.js"></script>
   ```

3. **Configure web server:**
   - Enable gzip compression
   - Set appropriate cache headers
   - Configure HTTPS
   - Set up reverse proxy for API

### Docker Deployment
```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

### CDN Integration
For production, consider using a CDN for static assets:
```html
<link rel="preload" href="https://cdn.example.com/css/main.css" as="style">
<link rel="preload" href="https://cdn.example.com/js/app.js" as="script">
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes following code style guidelines
4. Test thoroughly across browsers
5. Submit a pull request

### Testing
- Test on multiple browsers and devices
- Verify accessibility with screen readers
- Check performance with large datasets
- Validate with different API responses

## 📄 License

This project is part of the S3 Vector Browser suite. See the main project license for details.

## 🆘 Support

### Troubleshooting
1. Check browser console for errors
2. Verify API server is running and accessible
3. Clear browser cache and cookies
4. Try in incognito/private browsing mode

### Getting Help
- Check the main project documentation
- Review API documentation at `/docs`
- Check browser compatibility requirements
- Verify AWS credentials and permissions

---

**Happy browsing with the beautiful JavaScript frontend!** 🗂️✨