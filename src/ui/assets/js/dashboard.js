// Main Dashboard Class - Refactored to use modular components
class Dashboard {
    constructor() {
        // Initialize UI helpers first
        this.uiHelpers = new UIHelpers();
        
        // Initialize managers
        this.statusManager = new StatusManager(this);
        this.spamDetectionTester = new SpamDetectionTester(this);
        this.realTimeManager = new RealTimeManager(this);
        this.postManager = new PostManager(this);
        this.commentManager = new CommentManager(this);
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.postManager.loadPosts();
        this.statusManager.startStatusUpdates();
        this.realTimeManager.initRealTimeUpdates();
        this.realTimeManager.startHeartbeatMonitoring();
    }

    bindEvents() {
        // Monitor controls
        document.getElementById('start-monitor').addEventListener('click', () => this.statusManager.startMonitor());
        document.getElementById('stop-monitor').addEventListener('click', () => this.statusManager.stopMonitor());
        
        // Test detection
        document.getElementById('test-detection').addEventListener('click', () => this.spamDetectionTester.testDetection());
        
        // Refresh posts
        document.getElementById('refresh-posts').addEventListener('click', () => this.postManager.loadPosts());

        // Toggle performance monitor
        document.getElementById('toggle-performance').addEventListener('click', () => this.uiHelpers.togglePerformanceMonitor());
        
        // Enter key for test detection
        document.getElementById('test-text').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.spamDetectionTester.testDetection();
            }
        });
    }

    // Delegate methods to UI helpers for backward compatibility
    showLoading(elementId) {
        this.uiHelpers.showLoading(elementId);
    }

    hideLoading(elementId) {
        this.uiHelpers.hideLoading(elementId);
    }

    showToast(message, type) {
        this.uiHelpers.showToast(message, type);
    }

    getConfidenceClass(confidence) {
        return this.uiHelpers.getConfidenceClass(confidence);
    }

    cleanup() {
        this.statusManager.stopStatusUpdates();
        this.realTimeManager.cleanup();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        // Check if all required classes are available
        if (typeof UIHelpers === 'undefined') {
            throw new Error('UIHelpers module not loaded');
        }
        if (typeof StatusManager === 'undefined') {
            throw new Error('StatusManager module not loaded');
        }
        if (typeof PostManager === 'undefined') {
            throw new Error('PostManager module not loaded');
        }
        if (typeof CommentManager === 'undefined') {
            throw new Error('CommentManager module not loaded');
        }

        window.dashboard = new Dashboard();
        console.log('✅ Dashboard initialized successfully');
    } catch (error) {
        console.error('❌ Failed to initialize dashboard:', error);
        // Show error message to user
        document.body.innerHTML = `
            <div class="container mt-5">
                <div class="alert alert-danger">
                    <h4>Dashboard Initialization Error</h4>
                    <p>Failed to load dashboard components: ${error.message}</p>
                    <p>Please refresh the page or contact support.</p>
                </div>
            </div>
        `;
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.cleanup();
    }
});
