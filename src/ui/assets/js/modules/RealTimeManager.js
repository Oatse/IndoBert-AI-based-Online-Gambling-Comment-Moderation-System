// Real-time Updates Management Module
class RealTimeManager {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.eventSource = null;
        this.lastHeartbeat = null;
    }

    initRealTimeUpdates() {
        // Initialize Server-Sent Events for real-time updates
        if (typeof EventSource !== 'undefined') {
            console.log('🔄 Initializing real-time updates...');
            this.updateRealTimeIndicator('connecting', 'Connecting...');

            this.eventSource = new EventSource('/api/events');

            this.eventSource.onopen = () => {
                console.log('📡 Real-time connection established');
                this.updateRealTimeIndicator('connected', 'Live Updates');
                this.dashboard.showToast('Real-time updates connected', 'success');
            };

            this.eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleRealTimeEvent(data);
                } catch (error) {
                    console.error('Error parsing SSE data:', error);
                }
            };

            this.eventSource.onerror = (error) => {
                console.error('SSE connection error:', error);
                this.updateRealTimeIndicator('disconnected', 'Disconnected');
                this.dashboard.showToast('Real-time connection lost. Retrying...', 'warning');

                // Retry connection after 5 seconds
                setTimeout(() => {
                    if (this.eventSource.readyState === EventSource.CLOSED) {
                        this.updateRealTimeIndicator('connecting', 'Reconnecting...');
                        this.initRealTimeUpdates();
                    }
                }, 5000);
            };
        } else {
            console.warn('EventSource not supported by this browser');
            this.dashboard.showToast('Real-time updates not supported in this browser', 'warning');
        }
    }

    updateRealTimeIndicator(status, text) {
        const indicator = document.getElementById('realtime-indicator');
        const statusText = document.getElementById('realtime-status');

        if (indicator && statusText) {
            indicator.style.display = 'block';
            indicator.className = `realtime-indicator ${status}`;
            statusText.textContent = text;

            // Auto-hide after 3 seconds if connected
            if (status === 'connected') {
                setTimeout(() => {
                    if (indicator.classList.contains('connected')) {
                        indicator.style.display = 'none';
                    }
                }, 3000);
            }
        }
    }

    handleRealTimeEvent(data) {
        // Only log non-heartbeat events to reduce console noise
        if (data.type !== 'heartbeat') {
            console.log('📨 Real-time event received:', data.type, data);
        }

        switch (data.type) {
            case 'connected':
                console.log('✅ Real-time updates ready');
                this.lastHeartbeat = Date.now();
                break;

            case 'heartbeat':
                // Update last heartbeat time
                this.lastHeartbeat = Date.now();
                break;

            case 'new_comment':
                this.handleNewComment(data);
                break;

            case 'spam_comment_removed':
                this.handleSpamCommentRemoved(data);
                break;

            case 'comment_deleted':
                this.handleCommentDeleted(data);
                break;

            case 'comment_edited':
                this.handleCommentEdited(data);
                break;

            case 'comment_deleted_external':
                this.handleCommentDeletedExternal(data);
                break;

            case 'comment_deleted_manual':
                this.handleCommentDeletedManual(data);
                break;

            default:
                console.log('Unknown event type:', data.type);
        }
    }

    startHeartbeatMonitoring() {
        // Monitor heartbeat and show warning if connection seems dead
        setInterval(() => {
            if (this.lastHeartbeat && Date.now() - this.lastHeartbeat > 60000) { // 1 minute
                console.warn('⚠️ No heartbeat received for over 1 minute');
                this.updateRealTimeIndicator('disconnected', 'Connection Lost');
            }
        }, 30000); // Check every 30 seconds
    }

    // Event handlers will be implemented in PostManager
    handleNewComment(data) {
        if (this.dashboard.postManager) {
            this.dashboard.postManager.handleNewComment(data);
        }
    }

    handleSpamCommentRemoved(data) {
        if (this.dashboard.postManager) {
            this.dashboard.postManager.handleSpamCommentRemoved(data);
        }
    }

    handleCommentDeleted(data) {
        if (this.dashboard.postManager) {
            this.dashboard.postManager.handleCommentDeleted(data);
        }
    }

    handleCommentEdited(data) {
        if (this.dashboard.postManager) {
            this.dashboard.postManager.handleCommentEdited(data);
        }
    }

    handleCommentDeletedExternal(data) {
        if (this.dashboard.postManager) {
            this.dashboard.postManager.handleCommentDeletedExternal(data);
        }
    }

    handleCommentDeletedManual(data) {
        if (this.dashboard.postManager) {
            this.dashboard.postManager.handleCommentDeletedManual(data);
        }
    }

    cleanup() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
    }
}

// Export for use in other modules
window.RealTimeManager = RealTimeManager;
