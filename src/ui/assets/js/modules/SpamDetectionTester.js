// Spam Detection Testing Module
class SpamDetectionTester {
    constructor(dashboard) {
        this.dashboard = dashboard;
    }

    async testDetection() {
        const textArea = document.getElementById('test-text');
        const text = textArea.value.trim();
        
        if (!text) {
            this.dashboard.showToast('Please enter text to test', 'warning');
            return;
        }

        try {
            this.dashboard.showLoading('test-detection');
            const response = await fetch('/api/test-detection', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            
            const result = await response.json();
            this.displayTestResult(result);
        } catch (error) {
            this.dashboard.showToast('Error testing detection: ' + error.message, 'error');
        } finally {
            this.dashboard.hideLoading('test-detection');
        }
    }

    displayTestResult(result) {
        const container = document.getElementById('test-result');
        const isSpam = result.is_spam;
        const confidence = (result.confidence * 100).toFixed(1);
        
        container.innerHTML = `
            <div class="test-result ${isSpam ? 'spam' : 'normal'} fade-in">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="badge bg-${isSpam ? 'danger' : 'success'} prediction-badge">
                        ${result.label.toUpperCase()}
                    </span>
                    <small class="text-muted">Confidence: ${confidence}%</small>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill ${this.getConfidenceClass(result.confidence)}" 
                         style="width: ${confidence}%"></div>
                </div>
                ${result.error ? `<div class="text-danger mt-2"><small>Error: ${result.error}</small></div>` : ''}
            </div>
        `;
    }

    getConfidenceClass(confidence) {
        if (confidence >= 0.8) return 'high';
        if (confidence >= 0.5) return 'medium';
        return 'low';
    }
}

// Export for use in other modules
window.SpamDetectionTester = SpamDetectionTester;
