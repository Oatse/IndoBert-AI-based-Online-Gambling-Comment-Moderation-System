// Post Management Module
class PostManager {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.uiHelpers = dashboard.uiHelpers;
    }

    async loadPosts() {
        try {
            this.uiHelpers.showLoading('refresh-posts');
            console.log('📡 Loading posts with comments...');
            const startTime = Date.now();

            // Use the new endpoint that loads posts with comments
            const response = await fetch('/api/posts-with-comments');
            const posts = await response.json();

            if (response.ok) {
                const loadTime = Date.now() - startTime;
                console.log(`⚡ Posts with comments loaded in ${loadTime}ms`);
                await this.displayPostsWithComments(posts);
            } else {
                this.uiHelpers.showToast(posts.error || 'Failed to load posts', 'error');
                document.getElementById('posts-container').innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        ${posts.error || 'Failed to load posts'}
                    </div>
                `;
            }
        } catch (error) {
            console.error('❌ Error loading posts:', error);
            this.uiHelpers.showToast('Error loading posts: ' + error.message, 'error');
        } finally {
            this.uiHelpers.hideLoading('refresh-posts');
        }
    }

    async displayPostsWithComments(posts) {
        const container = document.getElementById('posts-container');

        if (posts.length === 0) {
            container.innerHTML = this.uiHelpers.createEmptyState('fa-inbox', 'No posts found');
            return;
        }

        let html = '';
        for (const post of posts) {
            html += this.renderPostWithComments(post);
        }

        container.innerHTML = html;

        // Bind click events to post headers for collapsible functionality
        this.bindPostClickEvents();

        // Show success message with stats
        const totalComments = posts.reduce((sum, post) => sum + (post.comments?.length || 0), 0);
        const postsWithComments = posts.filter(post => post.comments && post.comments.length > 0).length;

        if (totalComments > 0) {
            this.uiHelpers.showToast(`Loaded ${posts.length} posts with ${totalComments} comments (${postsWithComments} posts have comments)`, 'success');
        } else {
            this.uiHelpers.showToast(`Loaded ${posts.length} posts (no comments found)`, 'info');
        }
    }

    renderPostWithComments(post) {
        const postDate = new Date(post.created_time).toLocaleString();
        const postIdShort = post.id.split('_')[1];
        const comments = post.comments || [];
        const commentsLoaded = post.commentsLoaded || false;
        const hasError = post.error;

        // Calculate stats
        const totalComments = comments.length;
        const spamComments = comments.filter(c => c.prediction?.is_spam).length;

        return `
            <div class="post-item fade-in ${commentsLoaded ? 'comments-loaded' : ''}" data-post-id="${post.id}">
                <div class="post-header" onclick="dashboard.postManager.toggleComments('${post.id}')">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center mb-2">
                                <i class="fas fa-file-text me-2 text-primary"></i>
                                <h6 class="mb-0">Post ${postIdShort}</h6>
                                ${post.cacheHit ? '<span class="badge bg-info ms-2" title="Loaded from cache"><i class="fas fa-bolt"></i></span>' : ''}
                                <i class="fas fa-chevron-down ms-2 expand-icon" id="icon-${post.id}"></i>
                            </div>
                            <p class="text-muted mb-2">${post.message ? post.message.substring(0, 150) + (post.message.length > 150 ? '...' : '') : 'No message'}</p>
                            <div class="d-flex align-items-center">
                                <small class="text-muted me-3">
                                    <i class="fas fa-calendar me-1"></i>
                                    ${postDate}
                                </small>
                                <span class="badge bg-${totalComments > 0 ? 'primary' : 'secondary'} me-2" id="comment-count-${post.id}">
                                    <i class="fas fa-comments me-1"></i>
                                    ${totalComments} Comments
                                </span>
                                <span class="badge bg-${spamComments > 0 ? 'danger' : 'success'} me-2" id="spam-count-${post.id}" ${spamComments === 0 ? 'style="display: none;"' : ''}>
                                    <i class="fas fa-${spamComments > 0 ? 'exclamation-triangle' : 'shield-alt'} me-1"></i>
                                    ${spamComments} Spam
                                </span>
                                ${commentsLoaded && !hasError ? `
                                    <span class="badge bg-success me-2">
                                        <i class="fas fa-check me-1"></i>Ready
                                    </span>
                                ` : hasError ? `
                                    <span class="badge bg-warning me-2">
                                        <i class="fas fa-exclamation-triangle me-1"></i>Error
                                    </span>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="comments-section ${commentsLoaded ? 'preloaded' : ''}" id="comments-${post.id}">
                    <div class="comments-header">
                        <i class="fas fa-comments me-2"></i>
                        Comments
                        ${commentsLoaded && !hasError ? `
                            <span class="badge bg-success ms-2">
                                <i class="fas fa-check me-1"></i>Loaded
                            </span>
                        ` : hasError ? `
                            <span class="badge bg-warning ms-2">
                                <i class="fas fa-exclamation-triangle me-1"></i>Error
                            </span>
                        ` : ''}
                        <span class="float-end">
                            <button class="btn btn-sm btn-outline-primary" onclick="dashboard.postManager.refreshComments('${post.id}')">
                                <i class="fas fa-sync-alt"></i>
                            </button>
                        </span>
                    </div>
                    <div class="comments-container" id="comments-container-${post.id}">
                        ${this.renderCommentsContent(post)}
                    </div>
                </div>
            </div>
        `;
    }

    renderCommentsContent(post) {
        const comments = post.comments || [];
        const commentsLoaded = post.commentsLoaded || false;
        const hasError = post.error;

        if (hasError) {
            return this.uiHelpers.createErrorMessage(hasError, true, `dashboard.postManager.loadAndDisplayComments('${post.id}')`);
        }

        if (!commentsLoaded) {
            return this.uiHelpers.createLoadingSpinner('Loading comments...');
        }

        if (comments.length === 0) {
            return this.uiHelpers.createEmptyState('fa-comment-slash', 'No comments found');
        }

        return comments.map(comment => this.dashboard.commentManager.renderComment(comment)).join('');
    }

    bindPostClickEvents() {
        // Event listeners sudah di-handle oleh onclick di HTML
        // Method ini untuk future enhancements
    }

    async toggleComments(postId) {
        const commentsSection = document.getElementById(`comments-${postId}`);
        const expandIcon = document.getElementById(`icon-${postId}`);
        const postItem = document.querySelector(`[data-post-id="${postId}"]`);

        if (commentsSection.classList.contains('show')) {
            // Hide comments
            commentsSection.classList.remove('show');
            expandIcon.classList.remove('expanded');
            postItem.classList.remove('expanded');
        } else {
            // Show comments
            commentsSection.classList.add('show');
            expandIcon.classList.add('expanded');
            postItem.classList.add('expanded');

            // Only load comments if they're not already loaded (fallback for old posts)
            const container = document.getElementById(`comments-container-${postId}`);
            if (container.innerHTML.includes('Loading comments...')) {
                console.log(`📡 Loading comments on-demand for post ${postId} (fallback)`);
                await this.loadAndDisplayComments(postId);
            }
        }
    }

    async refreshComments(postId) {
        const container = document.getElementById(`comments-container-${postId}`);
        container.innerHTML = this.uiHelpers.createLoadingSpinner('Refreshing comments...');

        try {
            const response = await fetch(`/api/posts/${postId}/comments?refresh=true`);
            if (response.ok) {
                const comments = await response.json();
                this.displayCommentsInContainer(postId, comments);
                this.uiHelpers.showToast('Comments refreshed successfully!', 'success');
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Error refreshing comments:', error);
            container.innerHTML = this.uiHelpers.createErrorMessage('Failed to refresh comments. Please try again.');
            this.uiHelpers.showToast('Failed to refresh comments', 'error');
        }
    }

    displayCommentsInContainer(postId, comments) {
        const container = document.getElementById(`comments-container-${postId}`);
        const commentCountBadge = document.getElementById(`comment-count-${postId}`);
        const spamCountBadge = document.getElementById(`spam-count-${postId}`);

        if (comments.length === 0) {
            container.innerHTML = this.uiHelpers.createEmptyState('fa-comment-slash', 'No comments found');
            commentCountBadge.innerHTML = '<i class="fas fa-comments me-1"></i>0 Comments';
            return;
        }

        // Render comments
        container.innerHTML = comments.map(comment => this.dashboard.commentManager.renderComment(comment)).join('');

        // Update badges
        const spamCount = comments.filter(c => c.prediction?.is_spam).length;
        commentCountBadge.innerHTML = `<i class="fas fa-comments me-1"></i>${comments.length} Comments`;

        if (spamCount > 0) {
            spamCountBadge.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i>${spamCount} Spam`;
            spamCountBadge.style.display = 'inline-block';
        } else {
            spamCountBadge.style.display = 'none';
        }
    }

    // Real-time event handlers
    handleNewComment(data) {
        const { comment, postId } = data;
        console.log(`💬 New comment on post ${postId}:`, comment.message.substring(0, 50));

        // Find the post container
        const postElement = document.querySelector(`[data-post-id="${postId}"]`);
        if (!postElement) {
            console.warn(`Post ${postId} not found in UI`);
            return;
        }

        // Get comments container
        const commentsContainer = document.getElementById(`comments-container-${postId}`);
        if (!commentsContainer) {
            console.warn(`Comments container for post ${postId} not found`);
            return;
        }

        // Check if comments section exists and has comments
        let commentsList = commentsContainer.querySelector('.comments-list');
        if (!commentsList) {
            // If no comments list exists, create one
            if (commentsContainer.innerHTML.includes('No comments found')) {
                commentsContainer.innerHTML = '<div class="comments-list"></div>';
                commentsList = commentsContainer.querySelector('.comments-list');
            } else {
                // Find existing comments and wrap them in comments-list if needed
                const existingComments = commentsContainer.querySelectorAll('.comment-item');
                if (existingComments.length > 0) {
                    commentsContainer.innerHTML = '<div class="comments-list"></div>';
                    commentsList = commentsContainer.querySelector('.comments-list');
                    existingComments.forEach(comment => commentsList.appendChild(comment));
                } else {
                    commentsContainer.innerHTML = '<div class="comments-list"></div>';
                    commentsList = commentsContainer.querySelector('.comments-list');
                }
            }
        }

        // Create new comment element
        const commentElement = document.createElement('div');
        commentElement.innerHTML = this.dashboard.commentManager.renderComment(comment);
        const commentDiv = commentElement.firstElementChild;

        // Add new comment indicator
        commentDiv.classList.add('new-comment');

        // Insert at the top of comments list
        commentsList.insertBefore(commentDiv, commentsList.firstChild);

        // Animate the new comment
        commentDiv.style.opacity = '0';
        commentDiv.style.transform = 'translateY(-20px)';
        commentDiv.style.transition = 'all 0.5s ease';

        requestAnimationFrame(() => {
            commentDiv.style.opacity = '1';
            commentDiv.style.transform = 'translateY(0)';
        });

        // Update comment count
        this.updateCommentCount(postId, 1);

        // Show notification
        this.uiHelpers.showToast(`New comment from ${comment.from?.name || 'Unknown'}`, 'info');
    }

    handleSpamCommentRemoved(data) {
        const { commentId, postId } = data;
        console.log(`🗑️ Spam comment removed: ${commentId} on post ${postId}`);

        // Find and animate removal
        const commentElement = this.uiHelpers.findCommentElementById(commentId);
        if (commentElement) {
            commentElement.classList.add('spam-being-removed');
            commentElement.style.animation = 'spamRemovalSlide 1.5s ease-out forwards';

            setTimeout(() => {
                commentElement.remove();
                this.updateCommentCount(postId, -1);
                this.dashboard.commentManager.updateCommentCounts();
            }, 1500);
        }

        this.uiHelpers.showToast('Spam comment automatically removed', 'success');
    }

    updateCommentCount(postId, delta) {
        const commentCountBadge = document.getElementById(`comment-count-${postId}`);
        if (commentCountBadge) {
            const currentText = commentCountBadge.textContent;
            const currentCount = parseInt(currentText.match(/\d+/)?.[0] || '0');
            const newCount = Math.max(0, currentCount + delta);
            commentCountBadge.innerHTML = `<i class="fas fa-comments me-1"></i>${newCount} Comments`;
        }
    }

    async loadAndDisplayComments(postId) {
        const container = document.getElementById(`comments-container-${postId}`);
        const commentCountBadge = document.getElementById(`comment-count-${postId}`);
        const spamCountBadge = document.getElementById(`spam-count-${postId}`);

        try {
            console.log(`🔄 Loading comments for post ${postId}...`);
            const startTime = Date.now();

            // Show enhanced loading state with progress
            container.innerHTML = `
                <div class="text-center p-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2 mb-1">Loading comments...</p>
                    <small class="text-muted" id="loading-status-${postId}">Fetching from Facebook...</small>
                    <div class="progress mt-2" style="height: 4px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated"
                             role="progressbar" style="width: 30%"></div>
                    </div>
                </div>
            `;

            // Update loading status periodically
            this.updateLoadingStatus(postId);

            const comments = await this.loadCommentsForPost(postId);
            const loadTime = Date.now() - startTime;
            console.log(`⚡ Comments loaded in ${loadTime}ms`);

            if (comments.length === 0) {
                container.innerHTML = this.uiHelpers.createEmptyState('fa-comment-slash', 'No comments found');
                commentCountBadge.innerHTML = '<i class="fas fa-comments me-1"></i>0 Comments';
                return;
            }

            // Progressive rendering - show comments as they're processed
            container.innerHTML = '<div class="comments-list"></div>';
            const commentsList = container.querySelector('.comments-list');

            // Render comments progressively
            comments.forEach((comment, index) => {
                setTimeout(() => {
                    const commentElement = document.createElement('div');
                    commentElement.innerHTML = this.dashboard.commentManager.renderComment(comment);
                    commentElement.style.opacity = '0';
                    commentElement.style.transform = 'translateY(10px)';

                    commentsList.appendChild(commentElement.firstElementChild);

                    // Animate in
                    requestAnimationFrame(() => {
                        commentElement.firstElementChild.style.transition = 'all 0.3s ease';
                        commentElement.firstElementChild.style.opacity = '1';
                        commentElement.firstElementChild.style.transform = 'translateY(0)';
                    });
                }, index * 50); // Stagger animation
            });

            // Update badges
            const spamCount = comments.filter(c => c.prediction?.is_spam).length;
            commentCountBadge.innerHTML = `<i class="fas fa-comments me-1"></i>${comments.length} Comments`;

            if (spamCount > 0) {
                spamCountBadge.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i>${spamCount} Spam`;
                spamCountBadge.style.display = 'inline-block';
            } else {
                spamCountBadge.style.display = 'none';
            }

        } catch (error) {
            console.error(`❌ Error loading comments:`, error);
            container.innerHTML = this.uiHelpers.createErrorMessage(
                error.message.includes('timeout') ?
                'AI processing is taking longer than expected. This might be due to high server load.' :
                error.message,
                true,
                `dashboard.postManager.loadAndDisplayComments('${postId}')`
            );
            commentCountBadge.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>Error';
        }
    }

    async loadCommentsForPost(postId, retries = 2) {
        const startTime = Date.now();
        let controller = null;
        let timeoutId = null;

        try {
            console.log(`📡 Fetching comments for post ${postId}...`);

            controller = new AbortController();

            // Increase timeout for AI processing
            const timeoutMs = 30000; // 30 seconds for AI processing
            timeoutId = setTimeout(() => {
                console.log(`⏰ Request timeout after ${timeoutMs}ms`);
                controller.abort();
            }, timeoutMs);

            const response = await fetch(`/api/posts/${postId}/comments`, {
                signal: controller.signal,
                headers: {
                    'Cache-Control': 'no-cache'
                }
            });

            if (timeoutId) {
                clearTimeout(timeoutId);
                timeoutId = null;
            }

            if (response.ok) {
                const comments = await response.json();
                const totalTime = Date.now() - startTime;

                console.log(`✅ Received ${comments.length} comments in ${totalTime}ms`);

                // Extract performance metrics from response headers
                const cacheStatus = response.headers.get('X-Cache-Status') || 'unknown';
                const fbTime = response.headers.get('X-FB-Time');
                const aiTime = response.headers.get('X-AI-Time');
                const serverTotalTime = response.headers.get('X-Total-Time');

                // Update performance monitor
                this.dashboard.uiHelpers.updatePerformanceMonitor({
                    totalTime: totalTime,
                    cached: cacheStatus === 'HIT',
                    apiTime: fbTime ? parseInt(fbTime) : null,
                    aiTime: aiTime ? parseInt(aiTime) : null,
                    serverTime: serverTotalTime ? parseInt(serverTotalTime) : null
                });

                return comments;
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            // Clean up timeout
            if (timeoutId) {
                clearTimeout(timeoutId);
            }

            const totalTime = Date.now() - startTime;

            // Handle different error types
            if (error.name === 'AbortError') {
                console.warn(`⏰ Request aborted after ${totalTime}ms (timeout or user action)`);
                if (retries > 0) {
                    console.log(`🔄 Retrying due to timeout... (${retries} attempts left)`);
                    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
                    return this.loadCommentsForPost(postId, retries - 1);
                } else {
                    throw new Error('Request timeout - AI processing is taking too long. Please try again.');
                }
            } else {
                console.error(`❌ Error loading comments (attempt ${3 - retries}) after ${totalTime}ms:`, error.message);

                if (retries > 0) {
                    console.log(`🔄 Retrying... (${retries} attempts left)`);
                    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
                    return this.loadCommentsForPost(postId, retries - 1);
                }
            }

            throw error;
        }
    }

    updateLoadingStatus(postId) {
        const statusElement = document.getElementById(`loading-status-${postId}`);
        if (!statusElement) return;

        const messages = [
            'Fetching from Facebook...',
            'Processing with AI...',
            'Analyzing comments...',
            'Almost done...'
        ];

        let messageIndex = 0;
        const interval = setInterval(() => {
            if (!statusElement || !statusElement.isConnected) {
                clearInterval(interval);
                return;
            }

            messageIndex = (messageIndex + 1) % messages.length;
            statusElement.textContent = messages[messageIndex];

            // Update progress bar
            const progressBar = statusElement.parentElement.querySelector('.progress-bar');
            if (progressBar) {
                const progress = Math.min(30 + (messageIndex * 20), 90);
                progressBar.style.width = `${progress}%`;
            }
        }, 3000);

        // Clear interval after 30 seconds
        setTimeout(() => clearInterval(interval), 30000);
    }

    // Additional real-time event handlers
    handleCommentDeleted(data) {
        const { commentId, postId } = data;
        console.log(`🗑️ Comment deleted: ${commentId} on post ${postId}`);

        const commentElement = this.uiHelpers.findCommentElementById(commentId);
        if (commentElement) {
            commentElement.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => {
                commentElement.remove();
                this.updateCommentCount(postId, -1);
                this.dashboard.commentManager.updateCommentCounts();
            }, 300);
        }
    }

    handleCommentEdited(data) {
        const { comment, postId } = data;
        console.log(`✏️ Comment edited: ${comment.id} on post ${postId}`);

        const commentElement = this.uiHelpers.findCommentElementById(comment.id);
        if (commentElement) {
            // Add edit animation
            commentElement.classList.add('comment-edited');
            commentElement.style.animation = 'editPulse 1s ease-in-out';

            // Update comment content
            const messageElement = commentElement.querySelector('.comment-message');
            if (messageElement) {
                messageElement.innerHTML = `
                    <div class="edited-comment">
                        <div class="new-message">${comment.newMessage || comment.message}</div>
                        <small class="edited-indicator text-info">
                            <i class="fas fa-edit me-1"></i>Edited
                            <span class="edited-time">${new Date(comment.updated_time || Date.now()).toLocaleString()}</span>
                        </small>
                    </div>
                `;
            }

            this.uiHelpers.showToast(`Comment edited by ${comment.from?.name || 'Unknown'}`, 'info');
        }
    }

    handleCommentDeletedExternal(data) {
        const { commentId, postId } = data;
        console.log(`🗑️ Comment deleted externally: ${commentId} on post ${postId}`);

        // Find and remove the comment from UI
        const commentElement = this.uiHelpers.findCommentElementById(commentId);
        if (commentElement) {
            // Show placeholder for external deletion
            const placeholder = document.createElement('div');
            placeholder.className = 'comment-deleted-placeholder';
            placeholder.innerHTML = `
                <i class="fas fa-info-circle me-2"></i>
                Comment was deleted externally
                <small class="text-muted ms-2">${new Date().toLocaleString()}</small>
            `;

            commentElement.parentNode.insertBefore(placeholder, commentElement);
            commentElement.remove();

            // Remove placeholder after 5 seconds
            setTimeout(() => {
                if (placeholder.parentNode) {
                    placeholder.remove();
                }
            }, 5000);

            this.updateCommentCount(postId, -1);
            this.dashboard.commentManager.updateCommentCounts();
        }

        this.uiHelpers.showToast('Comment was deleted externally', 'warning');
    }

    handleCommentDeletedManual(data) {
        const { commentId, postId, moderator, reason } = data;
        console.log(`🛡️ Comment deleted by moderation: ${commentId} on post ${postId}`);

        const commentElement = this.uiHelpers.findCommentElementById(commentId);
        if (commentElement) {
            commentElement.classList.add('moderation-deleted');
            commentElement.style.animation = 'moderationRemoval 2s ease-out forwards';

            setTimeout(() => {
                commentElement.remove();
                this.updateCommentCount(postId, -1);
                this.dashboard.commentManager.updateCommentCounts();
            }, 2000);
        }

        this.uiHelpers.showToast(`Comment removed by ${moderator}: ${reason}`, 'warning');
    }
}

// Export for use in other modules
window.PostManager = PostManager;
