const FB = require('fb');
const SpamDetectorBridge = require('../bridges/spamDetectorBridge');
require('dotenv').config();

class AutoSpamMonitor {
  constructor(options = {}) {
    this.pageId = process.env.PAGE_ID;
    this.pollInterval = options.pollInterval || 30000; // 30 detik default
    this.isRunning = false;
    this.processedComments = new Set(); // Track komentar yang sudah diproses
    this.debugMode = options.debugMode || false;

    // Untuk debug mode, cek komentar dalam 24 jam terakhir
    // Untuk normal mode, cek komentar dalam 5 menit terakhir
    this.lookbackMinutes = this.debugMode ? 1440 : 5; // 24 jam atau 5 menit
    this.lastCheckTime = new Date(Date.now() - (this.lookbackMinutes * 60 * 1000));

    // Inisialisasi spam detector
    this.spamDetector = new SpamDetectorBridge({
      mode: 'child_process',
      useOptimized: true,
      timeout: 30000
    });

    // Setup Facebook API
    FB.setAccessToken(process.env.PAGE_ACCESS_TOKEN);

    console.log(`Auto Monitor initialized for Page ID: ${this.pageId}`);
    console.log(`Poll interval: ${this.pollInterval / 1000} seconds`);
    console.log(`Debug mode: ${this.debugMode ? 'ON' : 'OFF'}`);
    console.log(`Looking back: ${this.lookbackMinutes} minutes`);
  }

  async start() {
    if (this.isRunning) {
      console.log('Monitor already running');
      return;
    }

    this.isRunning = true;
    console.log('🚀 Starting auto spam monitor...');
    
    // Initial check
    await this.checkForNewComments();
    
    // Set up polling
    this.pollTimer = setInterval(async () => {
      try {
        await this.checkForNewComments();
      } catch (error) {
        console.error('Error during polling:', error.message);
      }
    }, this.pollInterval);
    
    console.log('✅ Auto monitor started successfully');
  }

  async stop() {
    if (!this.isRunning) {
      console.log('Monitor not running');
      return;
    }

    this.isRunning = false;
    
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
    
    this.spamDetector.cleanup();
    console.log('🛑 Auto monitor stopped');
  }

  async checkForNewComments() {
    try {
      console.log(`🔍 Checking for new comments... (${new Date().toLocaleTimeString()})`);
      
      // Ambil postingan terbaru
      const postsResponse = await this.getRecentPosts();
      
      if (!postsResponse || !postsResponse.data) {
        console.log('No posts found');
        return;
      }

      let newCommentsFound = 0;
      let spamCommentsRemoved = 0;

      // Cek setiap postingan
      for (const post of postsResponse.data) {
        const newComments = await this.getNewCommentsForPost(post.id);
        
        if (newComments.length > 0) {
          console.log(`📝 Found ${newComments.length} new comments on post ${post.id}`);
          newCommentsFound += newComments.length;
          
          // Proses setiap komentar baru
          for (const comment of newComments) {
            const removed = await this.processComment(comment, post.id);
            if (removed) spamCommentsRemoved++;
          }
        }
      }

      if (newCommentsFound > 0) {
        console.log(`✨ Processed ${newCommentsFound} new comments, removed ${spamCommentsRemoved} spam comments`);
      } else {
        console.log('📭 No new comments found');
      }
      
      this.lastCheckTime = new Date();
      
    } catch (error) {
      console.error('❌ Error checking for new comments:', error.message);
    }
  }

  async getRecentPosts() {
    console.log(`   📅 Getting recent posts (checking comments since ${new Date(this.lastCheckTime).toLocaleString()})`);

    return new Promise((resolve, reject) => {
      FB.api(`${this.pageId}/posts`, {
        fields: ['id', 'message', 'created_time'],
        limit: 10 // Ambil 10 postingan terbaru (tanpa filter since untuk posts)
      }, (response) => {
        if (response && !response.error) {
          console.log(`   📊 Found ${response.data?.length || 0} posts`);
          if (response.data && response.data.length > 0) {
            response.data.forEach((post, index) => {
              console.log(`      ${index + 1}. ${post.id} (${post.created_time})`);
            });
          }
          resolve(response);
        } else {
          console.error(`   ❌ Error getting posts:`, response.error);
          reject(new Error(response.error?.message || 'Failed to get posts'));
        }
      });
    });
  }

  async getNewCommentsForPost(postId) {
    try {
      const sinceTimestamp = Math.floor(this.lastCheckTime.getTime() / 1000);

      console.log(`   🔍 Checking comments since ${new Date(this.lastCheckTime).toLocaleString()}`);

      const commentsResponse = await new Promise((resolve, reject) => {
        FB.api(`${postId}/comments`, {
          fields: ['id', 'message', 'created_time', 'from'],
          limit: 50,
          since: sinceTimestamp
        }, (response) => {
          if (response && !response.error) {
            resolve(response);
          } else {
            reject(new Error(response.error?.message || 'Failed to get comments'));
          }
        });
      });

      console.log(`   📊 API returned ${commentsResponse.data?.length || 0} comments`);

      if (!commentsResponse.data) {
        return [];
      }

      // Filter komentar yang belum diproses
      const newComments = commentsResponse.data.filter(comment => {
        const notProcessed = !this.processedComments.has(comment.id);
        if (!notProcessed) {
          console.log(`   ⏭️  Skipping already processed comment: ${comment.id}`);
        }
        return notProcessed;
      });

      console.log(`   ✨ Found ${newComments.length} new comments to process`);
      return newComments;

    } catch (error) {
      console.error(`❌ Error getting comments for post ${postId}:`, error.message);
      return [];
    }
  }

  async processComment(comment, postId) {
    try {
      // Tandai sebagai sudah diproses
      this.processedComments.add(comment.id);
      
      // Cek apakah spam
      const isSpam = await this.isSpamComment(comment.message);
      
      if (isSpam) {
        console.log(`🚨 SPAM DETECTED: "${comment.message.substring(0, 100)}..." by ${comment.from?.name || 'Unknown'}`);
        
        // Hapus komentar spam
        const deleted = await this.deleteComment(comment.id);
        if (deleted) {
          console.log(`🗑️  Spam comment deleted: ${comment.id}`);
          return true;
        }
      } else {
        console.log(`✅ Normal comment: "${comment.message.substring(0, 50)}..." by ${comment.from?.name || 'Unknown'}`);
      }
      
      return false;
      
    } catch (error) {
      console.error(`Error processing comment ${comment.id}:`, error.message);
      return false;
    }
  }

  async isSpamComment(commentText) {
    if (!commentText) return false;

    try {
      const prediction = await this.spamDetector.predict(commentText);
      
      console.log(`🤖 Prediction: ${prediction.label} (confidence: ${prediction.confidence.toFixed(3)})`);
      
      // Return true jika diprediksi sebagai spam dengan confidence > 0.8
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
        console.log(`🔍 Delete response for ${commentId}:`, response);

        // Handle different success response formats
        if (response === true || (response && response.success === true)) {
          console.log(`✅ Comment ${commentId} successfully deleted`);
          resolve(true);
        } else if (response && response.error) {
          // Handle error response
          console.error(`❌ Failed to delete comment ${commentId}:`, response.error.message);
          resolve(false);
        } else {
          // Handle unexpected response format - but don't treat as error if it looks successful
          console.warn(`⚠️ Unexpected delete response format for ${commentId}:`, JSON.stringify(response));
          // If response contains success indicator, treat as success
          if (response && (response.success || JSON.stringify(response).includes('success'))) {
            console.log(`✅ Comment ${commentId} likely deleted successfully (non-standard response)`);
            resolve(true);
          } else {
            resolve(false);
          }
        }
      });
    });
  }

  // Cleanup processed comments cache (jalankan setiap jam)
  cleanupCache() {
    if (this.processedComments.size > 1000) {
      console.log('🧹 Cleaning up processed comments cache...');
      this.processedComments.clear();
    }
  }
}

// Export class
module.exports = AutoSpamMonitor;

// Jika dijalankan langsung
if (require.main === module) {
  const monitor = new AutoSpamMonitor({
    pollInterval: 30000 // 30 detik
  });

  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\n🛑 Shutting down monitor...');
    await monitor.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\n🛑 Shutting down monitor...');
    await monitor.stop();
    process.exit(0);
  });

  // Start monitoring
  monitor.start().catch(console.error);
  
  // Cleanup cache setiap jam
  setInterval(() => {
    monitor.cleanupCache();
  }, 3600000); // 1 jam
}
