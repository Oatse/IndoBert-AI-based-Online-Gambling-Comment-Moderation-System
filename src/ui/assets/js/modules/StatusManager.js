// Status Management Module
class StatusManager {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.statusUpdateInterval = null;
    }

    startStatusUpdates() {
        this.statusUpdateInterval = setInterval(() => {
            this.updateStatus();
        }, 5000); // Update every 5 seconds
    }

    async updateStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            // Update monitor status
            const monitorStatusElement = document.getElementById('monitor-status');
            if (monitorStatusElement) {
                monitorStatusElement.className = `badge bg-${status.monitor.isRunning ? 'success' : 'secondary'}`;
                monitorStatusElement.textContent = status.monitor.isRunning ? 'Running' : 'Stopped';
            }

            // Update statistics
            const commentsProcessedElement = document.getElementById('comments-processed');
            if (commentsProcessedElement) {
                commentsProcessedElement.textContent = status.monitor.commentsProcessed || 0;
            }

            const spamRemovedElement = document.getElementById('spam-removed');
            if (spamRemovedElement) {
                spamRemovedElement.textContent = status.monitor.spamRemoved || 0;
            }

            // Update monitor buttons
            this.updateMonitorButtons(status.monitor.isRunning);
        } catch (error) {
            console.error('Error updating status:', error);
        }
    }

    updateMonitorButtons(isRunning) {
        const startButton = document.getElementById('start-monitor');
        const stopButton = document.getElementById('stop-monitor');
        
        if (startButton) {
            startButton.disabled = isRunning;
        }
        
        if (stopButton) {
            stopButton.disabled = !isRunning;
        }
    }

    async startMonitor() {
        try {
            this.dashboard.showLoading('start-monitor');
            const response = await fetch('/api/monitor/start', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                this.dashboard.showToast('Auto monitor started successfully!', 'success');
                this.updateMonitorButtons(true);
            } else {
                this.dashboard.showToast(result.error || 'Failed to start monitor', 'error');
            }
        } catch (error) {
            this.dashboard.showToast('Error starting monitor: ' + error.message, 'error');
        } finally {
            this.dashboard.hideLoading('start-monitor');
        }
    }

    async stopMonitor() {
        try {
            this.dashboard.showLoading('stop-monitor');
            const response = await fetch('/api/monitor/stop', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                this.dashboard.showToast('Auto monitor stopped successfully!', 'success');
                this.updateMonitorButtons(false);
            } else {
                this.dashboard.showToast(result.error || 'Failed to stop monitor', 'error');
            }
        } catch (error) {
            this.dashboard.showToast('Error stopping monitor: ' + error.message, 'error');
        } finally {
            this.dashboard.hideLoading('stop-monitor');
        }
    }

    stopStatusUpdates() {
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
            this.statusUpdateInterval = null;
        }
    }
}

// Export for use in other modules
window.StatusManager = StatusManager;
