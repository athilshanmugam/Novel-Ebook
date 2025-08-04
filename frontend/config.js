// Frontend Configuration
class FrontendConfig {
    constructor() {
        this.init();
    }

    init() {
        // Detect environment based on current URL
        const currentUrl = window.location.href;
        const isProduction = currentUrl.includes('novel-ebook.onrender.com') || 
                           currentUrl.includes('render.com') ||
                           currentUrl.includes('herokuapp.com') ||
                           currentUrl.includes('vercel.app') ||
                           currentUrl.includes('netlify.app');
        
        // Set API base URL
        this.API_BASE_URL = isProduction 
            ? 'https://novel-ebook.onrender.com' 
            : 'http://localhost:5000';
        
        // Log configuration for debugging
        console.log(`Frontend Config: Environment detected as ${isProduction ? 'production' : 'development'}`);
        console.log(`Frontend Config: API Base URL set to ${this.API_BASE_URL}`);
    }

    // Get full API URL for a specific endpoint
    getApiUrl(endpoint) {
        // Remove leading slash if present to avoid double slashes
        const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
        return `${this.API_BASE_URL}/${cleanEndpoint}`;
    }

    // Get API URLs for common endpoints
    get createUserUrl() {
        return this.getApiUrl('api/create-user');
    }

    get loginUrl() {
        return this.getApiUrl('api/login');
    }

    get userStatsUrl() {
        return this.getApiUrl('api/user-stats');
    }

    get saveNamesUrl() {
        return this.getApiUrl('api/save-names');
    }

    get updateSessionUrl() {
        return this.getApiUrl('api/update-session');
    }

    get endSessionUrl() {
        return this.getApiUrl('api/end-session');
    }

    get adminStatsUrl() {
        return this.getApiUrl('api/admin/stats');
    }

    get backupUrl() {
        return this.getApiUrl('api/backup');
    }
}

// Create global configuration instance
window.frontendConfig = new FrontendConfig(); 