// Comment Management Module
class CommentManager {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.uiHelpers = dashboard.uiHelpers;
    }

    renderComment(comment) {
        const prediction = comment.prediction;
        const isSpam = prediction?.is_spam || false;
        const confidence = prediction?.confidence || 0;
        const commentDate = new Date(comment.created_time).toLocaleString();

        return `
            <div class="comment-item ${isSpam ? 'spam' : 'normal'}" data-comment-id="${comment.id}">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="flex-grow-1">
                        <div class="d-flex align-items-center mb-1">
                            <strong class="me-2">${comment.from?.name || 'Unknown'}</strong>
                            <span class="badge bg-${isSpam ? 'danger' : 'success'} prediction-badge">
                                ${prediction?.label?.toUpperCase() || 'UNKNOWN'}
                            </span>
                            ${prediction?.fallback ? `
                                <span class="badge bg-warning ms-1" title="Regex fallback used">
                                    <i class="fas fa-exclamation-triangle"></i>
                                </span>
                            ` : ''}
                            ${prediction?.method === 'regex_fallback' ? `
                                <small class="text-muted ms-2">(Regex)</small>
                            ` : ''}
                        </div>
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>
                            ${commentDate}
                        </small>
                    </div>
                    <div class="dropdown">
                        <button class="btn btn-sm ${isSpam ? 'btn-outline-danger' : 'btn-outline-secondary'} dropdown-toggle" type="button" data-bs-toggle="dropdown">
                            <i class="fas ${isSpam ? 'fa-exclamation-triangle' : 'fa-ellipsis-v'}"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item text-danger" href="#" onclick="dashboard.commentManager.deleteCommentManual('${comment.id}', '${comment.from?.name || 'Unknown'}')">
                                <i class="fas fa-trash me-2"></i>Delete Comment
                            </a></li>
                            ${isSpam ? `
                            <li><a class="dropdown-item" href="#" onclick="dashboard.commentManager.markAsNotSpam('${comment.id}')">
                                <i class="fas fa-check me-2"></i>Mark as Not Spam
                            </a></li>
                            ` : ''}
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-muted" href="#" onclick="dashboard.commentManager.reportComment('${comment.id}')">
                                <i class="fas fa-flag me-2"></i>Report Comment
                            </a></li>
                        </ul>
                    </div>
                </div>
                <p class="mb-2 comment-message">${comment.message}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <div class="confidence-bar flex-grow-1 me-3">
                        <div class="confidence-fill ${this.uiHelpers.getConfidenceClass(confidence)}"
                             style="width: ${(confidence * 100).toFixed(1)}%"></div>
                    </div>
                    <small class="text-muted">
                        <i class="fas fa-brain me-1"></i>
                        ${(confidence * 100).toFixed(1)}%
                    </small>
                </div>
            </div>
        `;
    }

    async deleteCommentManual(commentId, authorName) {
        // Show confirmation modal with reason selection
        const modal = this.createModerationModal(commentId, authorName);
        document.body.appendChild(modal);

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Clean up modal when hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    createModerationModal(commentId, authorName) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-shield-alt me-2"></i>Manual Comment Moderation
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-3">
                            <strong>Delete comment by:</strong> ${authorName}<br>
                            <strong>Comment ID:</strong> <code>${commentId}</code>
                        </p>
                        <div class="mb-3">
                            <label for="moderationReason" class="form-label">Reason for deletion:</label>
                            <select class="form-select" id="moderationReason">
                                <option value="Spam">Spam content</option>
                                <option value="Inappropriate">Inappropriate content</option>
                                <option value="Harassment">Harassment or bullying</option>
                                <option value="Misinformation">Misinformation</option>
                                <option value="Off-topic">Off-topic discussion</option>
                                <option value="Violation">Community guidelines violation</option>
                                <option value="Other">Other (specify below)</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="moderatorName" class="form-label">Moderator name:</label>
                            <input type="text" class="form-control" id="moderatorName" value="Admin" placeholder="Enter moderator name">
                        </div>
                        <div class="mb-3">
                            <label for="additionalNotes" class="form-label">Additional notes (optional):</label>
                            <textarea class="form-control" id="additionalNotes" rows="2" placeholder="Any additional context..."></textarea>
                        </div>
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            This action cannot be undone. The comment will be permanently deleted from Facebook.
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" onclick="dashboard.commentManager.confirmManualDeletion('${commentId}')">
                            <i class="fas fa-trash me-2"></i>Delete Comment
                        </button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    async confirmManualDeletion(commentId) {
        const reason = document.getElementById('moderationReason').value;
        const moderator = document.getElementById('moderatorName').value || 'Admin';
        const notes = document.getElementById('additionalNotes').value;

        // Close modal
        const modal = document.querySelector('.modal.show');
        if (modal) {
            bootstrap.Modal.getInstance(modal).hide();
        }

        try {
            // Find post ID for this comment
            const commentElement = this.uiHelpers.findCommentElementById(commentId);
            const postElement = commentElement?.closest('[data-post-id]');
            const postId = postElement?.dataset.postId;

            const response = await fetch(`/api/comments/${commentId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    postId: postId,
                    reason: reason + (notes ? ` - ${notes}` : ''),
                    moderator: moderator
                })
            });

            const result = await response.json();

            if (result.success) {
                this.uiHelpers.showToast(`Comment deleted by ${moderator} - ${reason}`, 'success');
                // The real-time event will handle UI removal
            } else {
                this.uiHelpers.showToast(result.error || 'Failed to delete comment', 'error');
            }
        } catch (error) {
            this.uiHelpers.showToast('Error deleting comment: ' + error.message, 'error');
        }
    }

    async markAsNotSpam(commentId) {
        // This is a placeholder for future implementation
        // Could be used to retrain the model or add to whitelist
        this.uiHelpers.showToast('Feature coming soon: Mark as not spam', 'info');
    }

    async reportComment(commentId) {
        // This is a placeholder for future implementation
        // Could be used to report to Facebook or internal system
        this.uiHelpers.showToast('Feature coming soon: Report comment', 'info');
    }

    updateCommentCounts() {
        // Update comment counts after deletion
        document.querySelectorAll('[data-post-id]').forEach(postElement => {
            const postId = postElement.dataset.postId;
            const commentsContainer = document.getElementById(`comments-container-${postId}`);
            const commentCountBadge = document.getElementById(`comment-count-${postId}`);
            const spamCountBadge = document.getElementById(`spam-count-${postId}`);

            if (commentsContainer) {
                const totalComments = commentsContainer.querySelectorAll('.comment-item').length;
                const spamComments = commentsContainer.querySelectorAll('.comment-item.spam').length;

                commentCountBadge.innerHTML = `<i class="fas fa-comments me-1"></i>${totalComments} Comments`;

                if (spamComments > 0) {
                    spamCountBadge.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i>${spamComments} Spam`;
                    spamCountBadge.style.display = 'inline-block';
                } else {
                    spamCountBadge.style.display = 'none';
                }
            }
        });
    }
}

// Export for use in other modules
window.CommentManager = CommentManager;
