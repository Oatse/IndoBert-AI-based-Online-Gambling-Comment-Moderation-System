# ✏️ Comment Updates & Deletions Real-Time Implementation

## 📋 Overview

Implementasi sistem real-time untuk mendeteksi dan menampilkan perubahan komentar (edit dan delete) secara langsung di UI tanpa perlu refresh halaman.

## ✨ Fitur Utama

### 1. **Real-Time Comment Edit Detection**
- Mendeteksi ketika komentar diedit di Facebook
- Menampilkan perubahan secara real-time di UI
- Visual indicator untuk komentar yang telah diedit
- Animasi smooth untuk perubahan content

### 2. **Real-Time Comment Deletion Detection**
- Mendeteksi ketika komentar dihapus dari Facebook
- Menghapus komentar dari UI secara real-time
- Animasi slide-out untuk komentar yang dihapus
- Update counter otomatis

### 3. **Comment Change Tracking**
- Sistem tracking untuk mendeteksi perubahan
- Comparison engine untuk detect edits
- Memory-efficient tracking dengan cleanup

## 🔧 Technical Implementation

### Backend Implementation

#### 1. **Comment Tracking System**
```javascript
// Track comments for change detection
this.commentsTracker = new Map();

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
```

#### 2. **Change Detection Engine**
```javascript
async checkCommentChanges(currentComments, postId) {
  const changes = { edited: [], deleted: [] };
  
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
    }
  }
  
  return changes;
}
```

#### 3. **Auto Monitor Integration**
```javascript
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
```

### Webhook Integration

#### 1. **Extended Webhook Handler**
```javascript
async processCommentChange(value) {
  switch (value.verb) {
    case 'add':
      await this.handleNewComment(value);
      break;
    case 'edited':
      await this.handleCommentEdit(value);
      break;
    case 'remove':
      await this.handleCommentDelete(value);
      break;
  }
}
```

#### 2. **Comment Edit Handler**
```javascript
async handleCommentEdit(commentData) {
  const commentId = commentData.comment_id;
  const postId = commentData.post_id;
  
  // Get updated comment details
  const comment = await this.getCommentDetails(commentId);
  
  if (comment && comment.message) {
    // Check if the edited comment is now spam
    const isSpam = await this.isSpamComment(comment.message);
    
    if (isSpam) {
      // Delete spam comment
      const deleted = await this.deleteComment(commentId);
    } else {
      // Broadcast comment edit event
      this.uiServer.broadcastToSSE({
        type: 'comment_edited',
        comment: comment,
        postId: postId,
        timestamp: new Date().toISOString()
      });
    }
  }
}
```

#### 3. **Comment Delete Handler**
```javascript
async handleCommentDelete(commentData) {
  const commentId = commentData.comment_id;
  const postId = commentData.post_id;
  
  // Broadcast comment deletion event
  this.uiServer.broadcastToSSE({
    type: 'comment_deleted_external',
    commentId: commentId,
    postId: postId,
    timestamp: new Date().toISOString()
  });
}
```

### Frontend Implementation

#### 1. **Event Handling**
```javascript
handleRealTimeEvent(data) {
  switch (data.type) {
    case 'comment_edited':
      this.handleCommentEdited(data);
      break;
    case 'comment_deleted_external':
      this.handleCommentDeletedExternal(data);
      break;
  }
}
```

#### 2. **Comment Edit Handler**
```javascript
handleCommentEdited(data) {
  const { comment, postId } = data;
  
  // Find the comment element by ID
  const commentElement = this.findCommentElementById(comment.id);
  if (!commentElement) return;
  
  // Update comment content
  const messageElement = commentElement.querySelector('.comment-message');
  if (messageElement) {
    messageElement.innerHTML = `
      <div class="edited-comment">
        <div class="new-message">${comment.newMessage || comment.message}</div>
        <small class="text-muted edited-indicator">
          <i class="fas fa-edit me-1"></i>Edited
          <span class="edited-time">${new Date().toLocaleTimeString()}</span>
        </small>
      </div>
    `;
    
    // Add edited styling and animation
    commentElement.classList.add('comment-edited');
    messageElement.style.animation = 'editPulse 1s ease-in-out';
    
    // Show notification
    this.showToast(`Comment edited by ${comment.from?.name || 'Unknown'}`, 'info');
  }
}
```

#### 3. **Comment Delete Handler**
```javascript
handleCommentDeletedExternal(data) {
  const { commentId, postId, author } = data;
  
  // Find and remove the comment from UI
  const commentElement = this.findCommentElementById(commentId);
  if (commentElement) {
    // Add deletion animation
    commentElement.style.animation = 'fadeOutSlide 0.5s ease-out forwards';
    
    setTimeout(() => {
      commentElement.remove();
      this.updateCommentCountsForPost(postId);
    }, 500);
    
    // Show notification
    this.showToast(`Comment by ${author} was deleted`, 'warning');
  }
}
```

#### 4. **Comment Element Finder**
```javascript
findCommentElementById(commentId) {
  // Try different selectors to find the comment element
  let commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
  
  if (!commentElement) {
    // Try finding by onclick attribute (fallback)
    commentElement = document.querySelector(`[onclick*="${commentId}"]`)?.closest('.comment-item');
  }
  
  if (!commentElement) {
    // Try finding by any element containing the comment ID
    const allComments = document.querySelectorAll('.comment-item');
    for (const comment of allComments) {
      if (comment.innerHTML.includes(commentId)) {
        commentElement = comment;
        break;
      }
    }
  }
  
  return commentElement;
}
```

## 🎨 UI/UX Features

### 1. **Edit Animations**
```css
.comment-item.comment-edited {
  border-left: 4px solid #17a2b8;
  background: linear-gradient(135deg, #e8f4f8 0%, #f0f9fa 100%);
}

@keyframes editPulse {
  0% {
    background: linear-gradient(135deg, #e8f4f8 0%, #f0f9fa 100%);
    transform: scale(1);
  }
  50% {
    background: linear-gradient(135deg, #bee5eb 0%, #d1ecf1 100%);
    transform: scale(1.01);
  }
  100% {
    background: linear-gradient(135deg, #e8f4f8 0%, #f0f9fa 100%);
    transform: scale(1);
  }
}
```

### 2. **Delete Animations**
```css
@keyframes fadeOutSlide {
  0% {
    opacity: 1;
    transform: translateX(0);
    max-height: 200px;
  }
  50% {
    opacity: 0.5;
    transform: translateX(-20px);
  }
  100% {
    opacity: 0;
    transform: translateX(-50px);
    max-height: 0;
    padding: 0;
    margin: 0;
  }
}
```

### 3. **Edit Indicators**
```css
.edited-indicator {
  display: block;
  margin-top: 5px;
  font-style: italic;
  color: #17a2b8 !important;
}

.edited-time {
  margin-left: 5px;
}
```

## 📊 Event Types

### 1. **comment_edited**
```json
{
  "type": "comment_edited",
  "comment": {
    "id": "comment_id",
    "oldMessage": "original text",
    "newMessage": "edited text",
    "from": { "name": "User Name" },
    "updated_time": "2025-06-24T09:00:00Z"
  },
  "postId": "post_id",
  "timestamp": "2025-06-24T09:00:00Z"
}
```

### 2. **comment_deleted_external**
```json
{
  "type": "comment_deleted_external",
  "commentId": "comment_id",
  "postId": "post_id",
  "message": "deleted comment text",
  "author": "User Name",
  "timestamp": "2025-06-24T09:00:00Z"
}
```

## 🔄 Change Detection Flow

### 1. **Auto Monitor Cycle**
```
1. Fetch current comments from Facebook
2. Compare with tracked comments
3. Detect changes (edits/deletions)
4. Broadcast changes via SSE
5. Update tracking data
6. Wait for next cycle (30s)
```

### 2. **Webhook Flow**
```
1. Facebook sends webhook notification
2. Parse comment change event
3. Determine change type (edit/delete)
4. Fetch updated comment details
5. Broadcast change via SSE
6. Update UI in real-time
```

## 🚀 Usage

### 1. **Start System**
```bash
node src/ui/server.js
```

### 2. **Test Comment Changes**
- Edit a comment on Facebook post
- Delete a comment on Facebook post
- Watch changes appear in real-time on dashboard

### 3. **Monitor Events**
- Check browser console for event logs
- Watch SSE connection status
- Observe animations and notifications

## 🎉 Benefits

1. **⚡ Instant Updates** - Changes appear immediately without refresh
2. **🎨 Visual Feedback** - Clear animations and indicators
3. **📊 Accurate Tracking** - Reliable change detection system
4. **🔄 Automatic Sync** - UI stays in sync with Facebook
5. **🛡️ Error Handling** - Graceful fallbacks and recovery
6. **📱 Responsive Design** - Works on all devices

## 🔮 Future Enhancements

1. **Comment History** - Track edit history
2. **Diff Visualization** - Show what changed in edits
3. **Bulk Operations** - Handle multiple changes efficiently
4. **User Notifications** - Browser notifications for changes
5. **Audit Trail** - Log all comment changes
