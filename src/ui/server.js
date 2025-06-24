const express = require('express');
const path = require('path');
const SpamDetectorBridge = require('../bridges/spamDetectorBridge');
const AutoSpamMonitor = require('../monitors/auto_monitor');
const FB = require('fb');
require('dotenv').config();

class UIServer {
  constructor(options = {}) {
    this.app = express();
    this.port = options.port || 3001;
    this.spamDetector = null;
    this.autoMonitor = null;
    this.commentsCache = new Map(); // Simple cache for comments
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes cache
    this.postsWithCommentsCache = new Map(); // Cache for posts with comments
    this.postsWithCommentsCacheTimeout = 2 * 60 * 1000; // 2 minutes for posts with comments
    this.sseClients = new Set(); // Store SSE connections for real-time updates
    this.commentsTracker = new Map(); // Track comments for change detection
    this.monitorStatus = {
      isRunning: false,
      startTime: null,
      commentsProcessed: 0,
      spamRemoved: 0,
      lastCheck: null
    };

    this.setupMiddleware();
    this.setupRoutes();
    this.initializeServices();
  }

  setupMiddleware() {
    // Serve static files
    this.app.use(express.static(path.join(__dirname, 'assets')));
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));
    
    // Set view engine
    this.app.set('view engine', 'ejs');
    this.app.set('views', path.join(__dirname, 'pages'));
  }

  initializeServices() {
    // Initialize spam detector
    this.spamDetector = new SpamDetectorBridge({
      mode: 'child_process',
      useOptimized: true,
      timeout: 30000
    });

    // Setup Facebook API
    if (process.env.PAGE_ACCESS_TOKEN) {
      FB.setAccessToken(process.env.PAGE_ACCESS_TOKEN);
    }
  }

  setupRoutes() {
    // Main dashboard
    this.app.get('/', (req, res) => {
      res.render('dashboard', {
        title: 'Judol Remover Dashboard',
        monitorStatus: this.monitorStatus,
        pageId: process.env.PAGE_ID,
        hasToken: !!process.env.PAGE_ACCESS_TOKEN
      });
    });

    // API Routes
    this.app.get('/api/status', (req, res) => {
      res.json({
        monitor: this.monitorStatus,
        detector: {
          ready: this.spamDetector ? true : false,
          mode: this.spamDetector?.mode || 'unknown'
        },
        facebook: {
          pageId: process.env.PAGE_ID,
          hasToken: !!process.env.PAGE_ACCESS_TOKEN
        }
      });
    });

    // Test spam detection
    this.app.post('/api/test-detection', async (req, res) => {
      try {
        const { text } = req.body;
        if (!text) {
          return res.status(400).json({ error: 'Text is required' });
        }

        const result = await this.spamDetector.predict(text);
        res.json(result);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Start/Stop auto monitor
    this.app.post('/api/monitor/start', async (req, res) => {
      try {
        if (this.monitorStatus.isRunning) {
          return res.status(400).json({ error: 'Monitor already running' });
        }

        this.autoMonitor = new AutoSpamMonitor({
          pollInterval: 30000,
          debugMode: false
        });

        // Override some methods to track statistics and broadcast updates
        const originalProcessComment = this.autoMonitor.processComment.bind(this.autoMonitor);
        this.autoMonitor.processComment = async (comment, postId) => {
          this.monitorStatus.commentsProcessed++;

          // Get prediction before processing
          let prediction = null;
          try {
            prediction = await this.spamDetector.predict(comment.message);
          } catch (error) {
            prediction = this.getFallbackPrediction(comment.message);
          }

          // Always broadcast new comment first (so it appears in UI)
          this.broadcastToSSE({
            type: 'new_comment',
            comment: {
              id: comment.id,
              message: comment.message,
              created_time: comment.created_time,
              from: comment.from,
              prediction: prediction
            },
            postId: postId,
            timestamp: new Date().toISOString()
          });

          // If spam, process deletion and broadcast removal
          const result = await originalProcessComment(comment, postId);

          if (result) {
            this.monitorStatus.spamRemoved++;
            // Broadcast spam comment removal (so it gets removed from UI)
            this.broadcastToSSE({
              type: 'spam_comment_removed',
              commentId: comment.id,
              postId: postId,
              message: comment.message.substring(0, 100),
              author: comment.from?.name || 'Unknown',
              timestamp: new Date().toISOString()
            });
          }
          this.monitorStatus.lastCheck = new Date();
          return result;
        };

        await this.autoMonitor.start();
        
        this.monitorStatus.isRunning = true;
        this.monitorStatus.startTime = new Date();
        this.monitorStatus.commentsProcessed = 0;
        this.monitorStatus.spamRemoved = 0;

        res.json({ success: true, message: 'Auto monitor started' });
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    this.app.post('/api/monitor/stop', async (req, res) => {
      try {
        if (!this.monitorStatus.isRunning) {
          return res.status(400).json({ error: 'Monitor not running' });
        }

        if (this.autoMonitor) {
          await this.autoMonitor.stop();
          this.autoMonitor = null;
        }

        this.monitorStatus.isRunning = false;
        this.monitorStatus.startTime = null;

        res.json({ success: true, message: 'Auto monitor stopped' });
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Get recent posts
    this.app.get('/api/posts', async (req, res) => {
      try {
        if (!process.env.PAGE_ACCESS_TOKEN) {
          return res.status(400).json({ error: 'No access token configured' });
        }

        const posts = await new Promise((resolve, reject) => {
          FB.api(`${process.env.PAGE_ID}/posts`, {
            fields: ['id', 'message', 'created_time'],
            limit: 5
          }, (response) => {
            if (response && !response.error) {
              resolve(response.data || []);
            } else {
              reject(new Error(response.error?.message || 'Failed to get posts'));
            }
          });
        });

        res.json(posts);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Get recent posts with comments (eager loading)
    this.app.get('/api/posts-with-comments', async (req, res) => {
      try {
        if (!process.env.PAGE_ACCESS_TOKEN) {
          return res.status(400).json({ error: 'No access token configured' });
        }

        console.log('📥 Loading posts with comments (eager loading)...');
        const startTime = Date.now();

        // Check if we have cached posts with comments
        const cacheKey = 'posts-with-comments';
        if (this.postsWithCommentsCache.has(cacheKey)) {
          const cached = this.postsWithCommentsCache.get(cacheKey);
          if (Date.now() - cached.timestamp < this.postsWithCommentsCacheTimeout) {
            console.log(`💾 Serving posts with comments from cache`);
            res.set('X-Cache-Status', 'HIT');
            res.set('X-Cache-Age', Math.floor((Date.now() - cached.timestamp) / 1000));
            return res.json(cached.data);
          } else {
            this.postsWithCommentsCache.delete(cacheKey);
          }
        }

        // Get posts first
        const posts = await new Promise((resolve, reject) => {
          FB.api(`${process.env.PAGE_ID}/posts`, {
            fields: ['id', 'message', 'created_time'],
            limit: 5
          }, (response) => {
            if (response && !response.error) {
              resolve(response.data || []);
            } else {
              reject(new Error(response.error?.message || 'Failed to get posts'));
            }
          });
        });

        console.log(`📘 Found ${posts.length} posts`);

        // Load comments for each post in parallel with controlled concurrency
        const postsWithComments = await this.loadCommentsWithConcurrencyControl(posts);

        // Track all loaded comments for change detection
        postsWithComments.forEach(post => {
          if (post.comments && post.comments.length > 0) {
            this.trackComments(post.comments, post.id);
          }
        });



        const totalTime = Date.now() - startTime;
        console.log(`⚡ Total posts with comments loaded in ${totalTime}ms`);

        // Cache the result
        this.postsWithCommentsCache.set(cacheKey, {
          data: postsWithComments,
          timestamp: Date.now()
        });

        res.set('X-Cache-Status', 'MISS');
        res.json(postsWithComments);
      } catch (error) {
        console.error('❌ Error loading posts with comments:', error.message);
        res.status(500).json({ error: error.message });
      }
    });

    // Get comments for a post
    this.app.get('/api/posts/:postId/comments', async (req, res) => {
      try {
        const { postId } = req.params;
        const forceRefresh = req.query.refresh === 'true';

        console.log(`📥 Loading comments for post ${postId}${forceRefresh ? ' (force refresh)' : ''}...`);
        const startTime = Date.now();

        // Check cache first (unless force refresh)
        if (!forceRefresh && this.commentsCache.has(postId)) {
          const cached = this.commentsCache.get(postId);
          if (Date.now() - cached.timestamp < this.cacheTimeout) {
            console.log(`💾 Serving from cache (${cached.data.length} comments)`);
            res.set('X-Cache-Status', 'HIT');
            res.set('X-Cache-Age', Math.floor((Date.now() - cached.timestamp) / 1000));
            return res.json(cached.data);
          } else {
            this.commentsCache.delete(postId); // Remove expired cache
          }
        }

        // Get comments from Facebook
        const comments = await new Promise((resolve, reject) => {
          FB.api(`${postId}/comments`, {
            fields: ['id', 'message', 'created_time', 'from'],
            limit: 20
          }, (response) => {
            if (response && !response.error) {
              resolve(response.data || []);
            } else {
              reject(new Error(response.error?.message || 'Failed to get comments'));
            }
          });
        });

        const fbTime = Date.now() - startTime;
        console.log(`📘 Facebook API took ${fbTime}ms for ${comments.length} comments`);

        if (comments.length === 0) {
          console.log(`📭 No comments found for post ${postId}`);
          const emptyResult = [];
          // Cache empty result for shorter time
          this.commentsCache.set(postId, {
            data: emptyResult,
            timestamp: Date.now()
          });
          return res.json(emptyResult);
        }

        // Process predictions in parallel with limited concurrency
        const predictionStartTime = Date.now();
        const commentsWithPrediction = await this.processPredictionsInBatches(comments, 5); // Increased batch size
        const predictionTime = Date.now() - predictionStartTime;

        const totalTime = Date.now() - startTime;
        console.log(`🤖 AI predictions took ${predictionTime}ms`);
        console.log(`⚡ Total request time: ${totalTime}ms`);

        // Cache the result
        this.commentsCache.set(postId, {
          data: commentsWithPrediction,
          timestamp: Date.now()
        });

        // Add performance headers
        res.set('X-Cache-Status', 'MISS');
        res.set('X-FB-Time', fbTime);
        res.set('X-AI-Time', predictionTime);
        res.set('X-Total-Time', totalTime);

        res.json(commentsWithPrediction);
      } catch (error) {
        console.error(`❌ Error loading comments:`, error.message);
        res.status(500).json({ error: error.message });
      }
    });

    // Manual delete comment (moderation)
    this.app.delete('/api/comments/:commentId', async (req, res) => {
      try {
        const { commentId } = req.params;
        const { postId, reason = 'Manual moderation', moderator = 'Admin' } = req.body;

        console.log(`🗑️ Manual moderation: Deleting comment ${commentId} (Reason: ${reason})`);

        // Enhanced delete response handling
        const result = await new Promise((resolve) => {
          FB.api(`/${commentId}`, 'DELETE', (response) => {
            // Handle different response formats
            if (response === true || (response && response.success === true)) {
              resolve(true);
            } else {
              console.warn(`⚠️ Unexpected delete response:`, JSON.stringify(response));
              // If response contains success indicator, treat as success
              if (response && (response.success || JSON.stringify(response).includes('success'))) {
                resolve(true);
              } else {
                resolve(false);
              }
            }
          });
        });

        if (result) {
          console.log(`✅ Comment ${commentId} deleted successfully via manual moderation`);

          // Broadcast manual deletion to SSE clients
          this.broadcastToSSE({
            type: 'comment_deleted_manual',
            commentId: commentId,
            postId: postId,
            reason: reason,
            moderator: moderator,
            timestamp: new Date().toISOString()
          });

          res.json({
            success: true,
            message: 'Comment deleted successfully',
            commentId: commentId,
            reason: reason,
            moderator: moderator
          });
        } else {
          console.log(`❌ Failed to delete comment ${commentId}`);
          res.status(400).json({ error: 'Failed to delete comment' });
        }
      } catch (error) {
        console.error('Error in manual comment deletion:', error);
        res.status(500).json({ error: error.message });
      }
    });

    // Server-Sent Events endpoint for real-time updates
    this.app.get('/api/events', (req, res) => {
      // Set headers for SSE with improved settings
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control',
        'X-Accel-Buffering': 'no', // Disable nginx buffering
        'Keep-Alive': 'timeout=30, max=100'
      });

      // Send initial connection message
      res.write(`data: ${JSON.stringify({
        type: 'connected',
        message: 'Real-time updates connected',
        timestamp: new Date().toISOString(),
        clientId: Date.now()
      })}\n\n`);

      // Add client to SSE clients set with metadata
      const clientInfo = {
        response: res,
        connectedAt: new Date(),
        lastPing: new Date(),
        clientId: Date.now()
      };

      this.sseClients.add(clientInfo);
      console.log(`📡 SSE client connected (ID: ${clientInfo.clientId}). Total clients: ${this.sseClients.size}`);

      // Send periodic heartbeat to keep connection alive
      const heartbeatInterval = setInterval(() => {
        if (!res.destroyed && !res.finished) {
          try {
            res.write(`data: ${JSON.stringify({
              type: 'heartbeat',
              timestamp: new Date().toISOString()
            })}\n\n`);
            clientInfo.lastPing = new Date();
          } catch (error) {
            // Connection is dead, clean up
            clearInterval(heartbeatInterval);
            this.sseClients.delete(clientInfo);
          }
        } else {
          clearInterval(heartbeatInterval);
          this.sseClients.delete(clientInfo);
        }
      }, 30000); // Send heartbeat every 30 seconds

      // Handle client disconnect
      req.on('close', () => {
        clearInterval(heartbeatInterval);
        this.sseClients.delete(clientInfo);
        console.log(`📡 SSE client disconnected (ID: ${clientInfo.clientId}). Total clients: ${this.sseClients.size}`);
      });

      req.on('error', (error) => {
        // Only log non-ECONNRESET errors to reduce noise
        if (error.code !== 'ECONNRESET' && error.code !== 'EPIPE') {
          console.error(`SSE client error (ID: ${clientInfo.clientId}):`, error.message);
        }
        clearInterval(heartbeatInterval);
        this.sseClients.delete(clientInfo);
      });

      // Handle response errors
      res.on('error', (error) => {
        if (error.code !== 'ECONNRESET' && error.code !== 'EPIPE') {
          console.error(`SSE response error (ID: ${clientInfo.clientId}):`, error.message);
        }
        clearInterval(heartbeatInterval);
        this.sseClients.delete(clientInfo);
      });
    });
  }

  start() {
    this.server = this.app.listen(this.port, () => {
      console.log(`🎨 UI Server running on http://localhost:${this.port}`);
      console.log(`📊 Dashboard: http://localhost:${this.port}`);
    });
  }

  async loadCommentsWithConcurrencyControl(posts) {
    const maxConcurrency = 3; // Limit concurrent Facebook API calls
    const results = [];

    // Process posts in batches to control concurrency
    for (let i = 0; i < posts.length; i += maxConcurrency) {
      const batch = posts.slice(i, i + maxConcurrency);

      const batchPromises = batch.map(async (post) => {
        try {
          // Check cache first
          if (this.commentsCache.has(post.id)) {
            const cached = this.commentsCache.get(post.id);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
              console.log(`💾 Using cached comments for post ${post.id}`);
              return {
                ...post,
                comments: cached.data,
                commentsLoaded: true,
                cacheHit: true
              };
            } else {
              this.commentsCache.delete(post.id);
            }
          }

          // Get comments from Facebook
          const comments = await new Promise((resolve, reject) => {
            FB.api(`${post.id}/comments`, {
              fields: ['id', 'message', 'created_time', 'from'],
              limit: 20
            }, (response) => {
              if (response && !response.error) {
                resolve(response.data || []);
              } else {
                reject(new Error(response.error?.message || 'Failed to get comments'));
              }
            });
          });

          console.log(`📘 Found ${comments.length} comments for post ${post.id}`);

          // Process predictions if there are comments
          let commentsWithPrediction = [];
          if (comments.length > 0) {
            // Check for comment changes before processing
            const changes = await this.checkCommentChanges(comments, post.id);

            // Broadcast comment changes
            if (changes.edited.length > 0) {
              changes.edited.forEach(editedComment => {
                this.broadcastToSSE({
                  type: 'comment_edited',
                  comment: editedComment,
                  postId: post.id,
                  timestamp: new Date().toISOString()
                });
              });
            }

            if (changes.deleted.length > 0) {
              changes.deleted.forEach(deletedComment => {
                this.broadcastToSSE({
                  type: 'comment_deleted_external',
                  commentId: deletedComment.id,
                  postId: post.id,
                  message: deletedComment.message,
                  author: deletedComment.from?.name || 'Unknown',
                  timestamp: new Date().toISOString()
                });
              });
            }

            commentsWithPrediction = await this.processPredictionsInBatches(comments, 5);

            // Track comments for future change detection
            this.trackComments(commentsWithPrediction, post.id);

            // Cache the result
            this.commentsCache.set(post.id, {
              data: commentsWithPrediction,
              timestamp: Date.now()
            });
          }

          return {
            ...post,
            comments: commentsWithPrediction,
            commentsLoaded: true,
            cacheHit: false
          };

        } catch (error) {
          console.error(`❌ Error loading comments for post ${post.id}:`, error.message);
          return {
            ...post,
            comments: [],
            commentsLoaded: false,
            error: error.message
          };
        }
      });

      // Wait for current batch to complete
      const batchResults = await Promise.all(batchPromises);
      results.push(...batchResults);

      // Small delay between batches to prevent overwhelming Facebook API
      if (i + maxConcurrency < posts.length) {
        await new Promise(resolve => setTimeout(resolve, 200));
      }
    }

    return results;
  }

  async processPredictionsInBatches(comments, batchSize = 3) {
    const results = [];

    for (let i = 0; i < comments.length; i += batchSize) {
      const batch = comments.slice(i, i + batchSize);

      const batchPromises = batch.map(async (comment) => {
        try {
          // Add timeout wrapper for individual predictions
          const predictionPromise = this.spamDetector.predict(comment.message);
          const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Individual prediction timeout')), 20000); // 20 second per comment
          });

          const prediction = await Promise.race([predictionPromise, timeoutPromise]);

          return {
            ...comment,
            prediction
          };
        } catch (error) {
          console.error(`❌ Prediction error for comment ${comment.id}:`, error.message);

          // Fallback to regex-based detection for timeout/error
          const fallbackPrediction = this.getFallbackPrediction(comment.message);

          return {
            ...comment,
            prediction: {
              ...fallbackPrediction,
              error: error.message,
              fallback: true
            }
          };
        }
      });

      try {
        const batchResults = await Promise.all(batchPromises);
        results.push(...batchResults);
      } catch (error) {
        console.error(`❌ Batch processing error:`, error.message);
        // Add fallback results for entire batch
        const fallbackResults = batch.map(comment => ({
          ...comment,
          prediction: {
            ...this.getFallbackPrediction(comment.message),
            error: 'Batch processing failed',
            fallback: true
          }
        }));
        results.push(...fallbackResults);
      }

      // Small delay between batches to prevent overwhelming
      if (i + batchSize < comments.length) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }

    return results;
  }

  getFallbackPrediction(message) {
    // Simple regex-based spam detection as fallback
    const spamPatterns = [
      /\b(judi|slot|casino|poker|togel)\b/i,
      /\b(obat|viagra|cialis)\b/i,
      /\b(pinjaman|kredit|hutang)\b/i,
      /\b(promo|diskon|gratis|bonus)\b.*\b(klik|link|wa|whatsapp)\b/i,
      /\b(investasi|profit|untung)\b.*\b(pasti|dijamin)\b/i
    ];

    const isSpam = spamPatterns.some(pattern => pattern.test(message));

    return {
      is_spam: isSpam,
      confidence: isSpam ? 0.7 : 0.3, // Lower confidence for regex
      label: isSpam ? 'spam' : 'normal',
      method: 'regex_fallback'
    };
  }

  // Broadcast message to all SSE clients
  broadcastToSSE(data) {
    const message = `data: ${JSON.stringify(data)}\n\n`;

    // Remove disconnected clients
    const disconnectedClients = [];

    for (const clientInfo of this.sseClients) {
      try {
        const client = clientInfo.response || clientInfo; // Support both old and new format

        // Check if client is still alive
        if (client.destroyed || client.finished) {
          disconnectedClients.push(clientInfo);
          continue;
        }

        client.write(message);

        // Update last ping time if using new format
        if (clientInfo.lastPing) {
          clientInfo.lastPing = new Date();
        }

      } catch (error) {
        // Only log non-connection errors
        if (error.code !== 'ECONNRESET' && error.code !== 'EPIPE') {
          console.error('Error sending SSE message:', error.message);
        }
        disconnectedClients.push(clientInfo);
      }
    }

    // Clean up disconnected clients
    disconnectedClients.forEach(clientInfo => {
      this.sseClients.delete(clientInfo);
    });

    if (this.sseClients.size > 0) {
      console.log(`📡 Broadcasted to ${this.sseClients.size} SSE clients:`, data.type);
    }
  }

  // Track comments for change detection
  trackComments(comments, postId) {
    comments.forEach(comment => {
      const commentKey = `${postId}_${comment.id}`;
      this.commentsTracker.set(commentKey, {
        id: comment.id,
        postId: postId,
        message: comment.message,
        created_time: comment.created_time,
        from: comment.from,
        lastUpdated: new Date().toISOString()
      });
    });
  }

  // Check for comment changes (edits or deletions)
  async checkCommentChanges(currentComments, postId) {
    const changes = {
      edited: [],
      deleted: []
    };

    // Get all tracked comments for this post
    const trackedComments = new Map();
    for (const [key, comment] of this.commentsTracker.entries()) {
      if (comment.postId === postId) {
        trackedComments.set(comment.id, comment);
      }
    }

    // Check for edits
    currentComments.forEach(currentComment => {
      const tracked = trackedComments.get(currentComment.id);
      if (tracked && tracked.message !== currentComment.message) {
        changes.edited.push({
          id: currentComment.id,
          postId: postId,
          oldMessage: tracked.message,
          newMessage: currentComment.message,
          from: currentComment.from,
          updated_time: new Date().toISOString()
        });

        // Update tracker
        const commentKey = `${postId}_${currentComment.id}`;
        this.commentsTracker.set(commentKey, {
          ...tracked,
          message: currentComment.message,
          lastUpdated: new Date().toISOString()
        });
      }
    });

    // Check for deletions
    const currentCommentIds = new Set(currentComments.map(c => c.id));
    for (const [commentId, tracked] of trackedComments.entries()) {
      if (!currentCommentIds.has(commentId)) {
        changes.deleted.push({
          id: commentId,
          postId: postId,
          message: tracked.message,
          from: tracked.from,
          deleted_time: new Date().toISOString()
        });

        // Remove from tracker
        const commentKey = `${postId}_${commentId}`;
        this.commentsTracker.delete(commentKey);
      }
    }

    return changes;
  }

  stop() {
    if (this.server) {
      this.server.close();
    }

    if (this.autoMonitor) {
      this.autoMonitor.stop();
    }

    if (this.spamDetector) {
      this.spamDetector.cleanup();
    }
  }
}

module.exports = UIServer;

// Jika dijalankan langsung
if (require.main === module) {
  const uiServer = new UIServer({
    port: process.env.UI_PORT || 3001
  });

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down UI server...');
    uiServer.stop();
    process.exit(0);
  });

  process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down UI server...');
    uiServer.stop();
    process.exit(0);
  });

  uiServer.start();
}
