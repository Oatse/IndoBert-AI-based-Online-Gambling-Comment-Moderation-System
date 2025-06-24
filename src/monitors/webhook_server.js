const express = require('express');
const crypto = require('crypto');
const SpamDetectorBridge = require('../bridges/spamDetectorBridge');
const FB = require('fb');
require('dotenv').config();

class WebhookSpamMonitor {
  constructor(options = {}) {
    this.app = express();
    this.port = options.port || 3000;
    this.verifyToken = process.env.WEBHOOK_VERIFY_TOKEN || 'your_verify_token_here';
    this.appSecret = process.env.FB_APP_SECRET;
    
    // Inisialisasi spam detector
    this.spamDetector = new SpamDetectorBridge({
      mode: 'child_process',
      useOptimized: true,
      timeout: 30000
    });
    
    // Setup Facebook API
    FB.setAccessToken(process.env.PAGE_ACCESS_TOKEN);
    
    this.setupMiddleware();
    this.setupRoutes();
    this.uiServer = null; // Reference to UI server for broadcasting

    console.log('🎣 Webhook Spam Monitor initialized');
  }

  setupMiddleware() {
    // Parse JSON dengan raw body untuk signature verification
    this.app.use('/webhook', express.raw({ type: 'application/json' }));
    this.app.use(express.json());
  }

  setupRoutes() {
    // Webhook verification (GET)
    this.app.get('/webhook', (req, res) => {
      const mode = req.query['hub.mode'];
      const token = req.query['hub.verify_token'];
      const challenge = req.query['hub.challenge'];

      if (mode && token) {
        if (mode === 'subscribe' && token === this.verifyToken) {
          console.log('✅ Webhook verified');
          res.status(200).send(challenge);
        } else {
          console.log('❌ Webhook verification failed');
          res.sendStatus(403);
        }
      } else {
        res.sendStatus(400);
      }
    });

    // Webhook events (POST)
    this.app.post('/webhook', async (req, res) => {
      try {
        // Verify signature jika app secret tersedia
        if (this.appSecret && !this.verifySignature(req.body, req.get('X-Hub-Signature-256'))) {
          console.log('❌ Invalid signature');
          return res.sendStatus(403);
        }

        const body = JSON.parse(req.body);
        
        if (body.object === 'page') {
          // Process each entry
          for (const entry of body.entry) {
            await this.processEntry(entry);
          }
          
          res.status(200).send('EVENT_RECEIVED');
        } else {
          res.sendStatus(404);
        }
      } catch (error) {
        console.error('❌ Webhook error:', error.message);
        res.sendStatus(500);
      }
    });

    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        detector_ready: this.spamDetector.isReady
      });
    });

    // Status endpoint
    this.app.get('/status', (req, res) => {
      res.json({
        webhook_active: true,
        verify_token_set: !!this.verifyToken,
        app_secret_set: !!this.appSecret,
        detector_mode: this.spamDetector.mode,
        detector_optimized: this.spamDetector.useOptimized
      });
    });
  }

  verifySignature(payload, signature) {
    if (!signature) return false;
    
    const expectedSignature = 'sha256=' + crypto
      .createHmac('sha256', this.appSecret)
      .update(payload)
      .digest('hex');
    
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  }

  async processEntry(entry) {
    try {
      // Process changes in the entry
      if (entry.changes) {
        for (const change of entry.changes) {
          await this.processChange(change, entry.id);
        }
      }
    } catch (error) {
      console.error('Error processing entry:', error.message);
    }
  }

  async processChange(change, pageId) {
    try {
      console.log(`📨 Received change: ${change.field} for page ${pageId}`);
      
      // Handle different types of changes
      switch (change.field) {
        case 'feed':
          await this.processFeedChange(change.value);
          break;
        case 'comments':
          await this.processCommentChange(change.value);
          break;
        default:
          console.log(`ℹ️  Unhandled change type: ${change.field}`);
      }
    } catch (error) {
      console.error('Error processing change:', error.message);
    }
  }

  async processFeedChange(value) {
    // Handle post changes (new posts, etc.)
    console.log('📝 Feed change detected:', value);
    
    if (value.item === 'comment' && value.verb === 'add') {
      // New comment added
      await this.handleNewComment(value);
    }
  }

  async processCommentChange(value) {
    // Handle comment changes
    console.log('💬 Comment change detected:', value);

    switch (value.verb) {
      case 'add':
        // New comment added
        await this.handleNewComment(value);
        break;
      case 'edited':
        // Comment edited
        await this.handleCommentEdit(value);
        break;
      case 'remove':
        // Comment deleted
        await this.handleCommentDelete(value);
        break;
      default:
        console.log(`ℹ️  Unhandled comment verb: ${value.verb}`);
    }
  }

  async handleNewComment(commentData) {
    try {
      const commentId = commentData.comment_id;
      const postId = commentData.post_id;
      
      console.log(`🆕 New comment detected: ${commentId} on post ${postId}`);
      
      // Get comment details
      const comment = await this.getCommentDetails(commentId);
      
      if (comment && comment.message) {
        // Check if spam
        const isSpam = await this.isSpamComment(comment.message);
        
        if (isSpam) {
          console.log(`🚨 SPAM DETECTED: "${comment.message.substring(0, 100)}..."`);
          
          // Delete spam comment
          const deleted = await this.deleteComment(commentId);
          if (deleted) {
            console.log(`🗑️  Spam comment deleted: ${commentId}`);
          }
        } else {
          console.log(`✅ Normal comment: "${comment.message.substring(0, 50)}..."`);
        }
      }
      
    } catch (error) {
      console.error('Error handling new comment:', error.message);
    }
  }

  async handleCommentEdit(commentData) {
    try {
      const commentId = commentData.comment_id;
      const postId = commentData.post_id;

      console.log(`✏️ Comment edited: ${commentId} on post ${postId}`);

      // Get updated comment details
      const comment = await this.getCommentDetails(commentId);

      if (comment && comment.message) {
        // Check if the edited comment is now spam
        const isSpam = await this.isSpamComment(comment.message);

        if (isSpam) {
          console.log(`🚨 EDITED COMMENT IS SPAM: "${comment.message.substring(0, 100)}..."`);

          // Delete spam comment
          const deleted = await this.deleteComment(commentId);
          if (deleted) {
            console.log(`🗑️  Edited spam comment deleted: ${commentId}`);
          }
        } else {
          console.log(`✅ Edited comment is normal: "${comment.message.substring(0, 50)}..."`);

          // Broadcast comment edit event if UI server is available
          if (this.uiServer) {
            this.uiServer.broadcastToSSE({
              type: 'comment_edited',
              comment: comment,
              postId: postId,
              timestamp: new Date().toISOString()
            });
          }
        }
      }

    } catch (error) {
      console.error('Error handling comment edit:', error.message);
    }
  }

  async handleCommentDelete(commentData) {
    try {
      const commentId = commentData.comment_id;
      const postId = commentData.post_id;

      console.log(`🗑️ Comment deleted: ${commentId} on post ${postId}`);

      // Broadcast comment deletion event if UI server is available
      if (this.uiServer) {
        this.uiServer.broadcastToSSE({
          type: 'comment_deleted_external',
          commentId: commentId,
          postId: postId,
          timestamp: new Date().toISOString()
        });
      }

    } catch (error) {
      console.error('Error handling comment delete:', error.message);
    }
  }

  async getCommentDetails(commentId) {
    return new Promise((resolve, reject) => {
      FB.api(commentId, {
        fields: ['id', 'message', 'created_time', 'from']
      }, (response) => {
        if (response && !response.error) {
          resolve(response);
        } else {
          reject(new Error(response.error?.message || 'Failed to get comment'));
        }
      });
    });
  }

  async isSpamComment(commentText) {
    if (!commentText) return false;

    try {
      const prediction = await this.spamDetector.predict(commentText);
      
      console.log(`🤖 Prediction: ${prediction.label} (confidence: ${prediction.confidence.toFixed(3)})`);
      
      return prediction.is_spam && prediction.confidence > 0.8;
      
    } catch (error) {
      console.error('Error dalam prediksi spam:', error.message);
      
      // Fallback ke regex pattern
      const spamPatterns = [
        /\b(jual|promo|diskon|gratis)\b/i,
        /http(s)?:\/\/\S+/,
        /\b(wa|whatsapp|telegram)\b/i,
        /\d{10,}/
      ];

      return spamPatterns.some(pattern => pattern.test(commentText));
    }
  }

  async deleteComment(commentId) {
    return new Promise((resolve) => {
      FB.api(`/${commentId}`, 'DELETE', (response) => {
        // Handle different success response formats
        if (response === true || (response && response.success === true)) {
          resolve(true);
        } else if (response && response.error) {
          // Handle error response
          console.error(`Failed to delete comment ${commentId}:`, response.error.message);
          resolve(false);
        } else {
          // Handle unexpected response format
          console.error(`Unexpected delete response for ${commentId}:`, JSON.stringify(response));
          resolve(false);
        }
      });
    });
  }

  setUIServer(uiServer) {
    this.uiServer = uiServer;
    console.log('🔗 UI Server reference set for webhook broadcasting');
  }

  start() {
    this.server = this.app.listen(this.port, () => {
      console.log(`🎣 Webhook server listening on port ${this.port}`);
      console.log(`📍 Webhook URL: http://localhost:${this.port}/webhook`);
      console.log(`🔑 Verify token: ${this.verifyToken}`);
    });
  }

  stop() {
    if (this.server) {
      this.server.close();
      console.log('🛑 Webhook server stopped');
    }
    
    this.spamDetector.cleanup();
  }
}

// Export class
module.exports = WebhookSpamMonitor;

// Jika dijalankan langsung
if (require.main === module) {
  const webhookMonitor = new WebhookSpamMonitor({
    port: process.env.WEBHOOK_PORT || 3000
  });

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down webhook server...');
    webhookMonitor.stop();
    process.exit(0);
  });

  process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down webhook server...');
    webhookMonitor.stop();
    process.exit(0);
  });

  // Start webhook server
  webhookMonitor.start();
}
