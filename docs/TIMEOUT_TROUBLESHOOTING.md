# 🔧 Timeout Issues Troubleshooting Guide

Panduan untuk mengatasi masalah timeout saat loading comments di web interface.

## 🔍 Common Timeout Errors

### 1. **AbortError: signal is aborted without reason**
```
Error loading comments (attempt 1) after 15003ms: AbortError: signal is aborted without reason
```

**Penyebab:**
- AI model membutuhkan waktu lama untuk processing
- Auto monitor sedang menggunakan AI model
- Server overload atau memory issues
- Python model loading ulang

### 2. **Request Timeout**
```
Request timeout after 30000ms
```

**Penyebab:**
- AI prediction timeout (>15 detik per comment)
- Facebook API response lambat
- Network connectivity issues

## 🚀 Solutions Implemented

### 1. **Increased Timeout Values**
```javascript
// Frontend: 30 seconds for AI processing
const timeoutMs = 30000;

// Backend: 15 seconds per prediction
this.timeout = 15000;

// Individual prediction: 20 seconds
setTimeout(() => reject(new Error('Individual prediction timeout')), 20000);
```

### 2. **Fallback Mechanism**
```javascript
// Regex-based spam detection as fallback
getFallbackPrediction(message) {
    const spamPatterns = [
        /\b(judi|slot|casino|poker|togel)\b/i,
        /\b(obat|viagra|cialis)\b/i,
        /\b(pinjaman|kredit|hutang)\b/i
    ];
    
    const isSpam = spamPatterns.some(pattern => pattern.test(message));
    return {
        is_spam: isSpam,
        confidence: isSpam ? 0.7 : 0.3,
        label: isSpam ? 'spam' : 'normal',
        method: 'regex_fallback'
    };
}
```

### 3. **Retry Mechanism**
```javascript
// Automatic retry with exponential backoff
if (retries > 0) {
    await new Promise(resolve => setTimeout(resolve, 2000));
    return this.loadCommentsForPost(postId, retries - 1);
}
```

### 4. **Enhanced Loading States**
```javascript
// Progressive loading messages
const messages = [
    'Fetching from Facebook...',
    'Processing with AI...',
    'Analyzing comments...',
    'Almost done...'
];
```

## 🛠️ Troubleshooting Steps

### Step 1: Check Auto Monitor Status
```bash
# Stop auto monitor if running
# Auto monitor uses the same AI model
```

**In Dashboard:**
1. Check if "Monitor Status" shows "Running"
2. If yes, click "Stop Auto Monitor"
3. Try loading comments again

### Step 2: Check Server Resources
```bash
# Check memory usage
tasklist /fi "imagename eq node.exe"

# Check Python processes
tasklist /fi "imagename eq python.exe"
```

**Signs of Issues:**
- High memory usage (>1GB)
- Multiple Python processes
- CPU usage >80%

### Step 3: Restart Services
```bash
# Restart UI server
npm run ui

# Or restart with fresh Python process
# Kill all Python processes first
taskkill /f /im python.exe
npm run ui
```

### Step 4: Use Performance Monitor
1. Click the ⚡ button in dashboard
2. Monitor timing breakdown:
   - **API Time**: Facebook response time
   - **AI Time**: AI processing time
   - **Cache Status**: HIT/MISS
   - **Total Time**: End-to-end time

### Step 5: Check Browser Console
```javascript
// Look for these patterns:
📡 Fetching comments for post...
⏰ Request timeout after 30000ms
❌ Error loading comments...
🔄 Retrying due to timeout...
```

## 🎯 Prevention Strategies

### 1. **Use Caching**
- First load: Slow (AI processing)
- Subsequent loads: Fast (cached)
- Cache expires after 5 minutes

### 2. **Avoid Concurrent Requests**
- Don't click multiple posts simultaneously
- Wait for one to finish before clicking another
- Auto monitor competes for AI resources

### 3. **Monitor Resource Usage**
- Keep task manager open
- Watch for memory leaks
- Restart if memory >2GB

### 4. **Optimize Timing**
- Use during low server load
- Avoid peak hours if shared server
- Consider batch processing times

## 🔧 Configuration Tuning

### Increase Timeouts (if needed)
```javascript
// In dashboard.js
const timeoutMs = 45000; // 45 seconds

// In spamDetectorBridge.js
this.timeout = 20000; // 20 seconds

// In server.js
setTimeout(() => reject(new Error('timeout')), 30000); // 30 seconds
```

### Reduce Batch Size
```javascript
// In server.js - process fewer comments at once
const batchSize = 2; // Reduce from 3 to 2
```

### Adjust Cache Timeout
```javascript
// In server.js - cache longer to reduce AI calls
this.cacheTimeout = 10 * 60 * 1000; // 10 minutes
```

## 📊 Performance Expectations

### Normal Performance:
- **Facebook API**: 500-1500ms
- **AI Processing**: 2-8 seconds (batch of 5-8 comments)
- **Total Time**: 3-10 seconds
- **Cache Hit**: <100ms

### Slow Performance (Warning):
- **Facebook API**: >2000ms
- **AI Processing**: >15 seconds
- **Total Time**: >20 seconds
- **Multiple Timeouts**: System overload

### Critical Issues:
- **Consistent Timeouts**: AI model issues
- **Memory Growth**: Memory leak
- **No Response**: Server crash

## 🚨 Emergency Procedures

### If UI Becomes Unresponsive:
1. **Refresh Browser**: Clear any stuck requests
2. **Restart Server**: `Ctrl+C` then `npm run ui`
3. **Kill Python**: `taskkill /f /im python.exe`
4. **Clear Cache**: Force refresh with `Ctrl+F5`

### If Auto Monitor Interferes:
1. **Stop Monitor**: Click "Stop Auto Monitor"
2. **Wait 30 seconds**: Let current processing finish
3. **Try Comments**: Load comments again
4. **Restart if needed**: Full server restart

### If Memory Issues:
1. **Check Task Manager**: Look for high memory usage
2. **Kill Processes**: End Python and Node processes
3. **Restart Clean**: Fresh start with `npm run ui`
4. **Monitor Usage**: Watch memory growth

## 📈 Monitoring & Alerts

### Browser Console Monitoring:
```javascript
// Set up console monitoring
console.log('Monitoring timeout issues...');

// Track request times
const startTime = Date.now();
// ... after request
const duration = Date.now() - startTime;
if (duration > 15000) {
    console.warn(`Slow request: ${duration}ms`);
}
```

### Server Log Monitoring:
```bash
# Watch for these patterns:
📥 Loading comments for post...
📘 Facebook API took XXXms
🤖 AI predictions took XXXms
⚡ Total request time: XXXms
❌ Prediction error...
```

## 🎯 Best Practices

### For Users:
1. **One at a time**: Don't click multiple posts
2. **Wait patiently**: AI processing takes time
3. **Use cache**: Reload same post for instant results
4. **Monitor resources**: Watch task manager
5. **Restart regularly**: Fresh start prevents issues

### For Developers:
1. **Implement timeouts**: Always have fallbacks
2. **Use caching**: Reduce AI load
3. **Monitor performance**: Track timing metrics
4. **Graceful degradation**: Fallback to regex
5. **Resource cleanup**: Prevent memory leaks

---

**🔧 Timeout issues are now handled gracefully with fallback mechanisms, better error messages, and retry logic. The system should be much more resilient to AI processing delays.**
