#!/usr/bin/env python3
"""
Auto monitoring module for Streamlit application
Handles automatic spam detection and removal
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import streamlit as st
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoMonitor:
    def __init__(self, facebook_api, spam_detector, poll_interval: int = 30):
        """
        Initialize auto monitor

        Args:
            facebook_api: Facebook API instance
            spam_detector: Spam detector instance
            poll_interval (int): Polling interval in seconds
        """
        self.facebook_api = facebook_api
        self.spam_detector = spam_detector
        self.poll_interval = poll_interval
        self.is_running = False
        self.monitor_thread = None
        self.last_check = None

        # Configuration that can be updated from main thread
        self.auto_delete_enabled = True
        self.confidence_threshold = 0.5

        # Internal storage for pending spam (thread-safe)
        self.pending_spam = []

        self.statistics = {
            'comments_processed': 0,
            'spam_removed': 0,
            'errors': 0,
            'start_time': None
        }
        self.processed_comments = set()  # Track processed comment IDs
        self.internal_logs = []  # Internal log storage for thread safety
        self.callbacks = {
            'on_spam_detected': [],
            'on_comment_deleted': [],
            'on_error': [],
            'on_stats_update': []
        }
    
    def add_callback(self, event: str, callback: Callable):
        """
        Add callback function for events
        
        Args:
            event (str): Event name
            callback (Callable): Callback function
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def trigger_callback(self, event: str, data: Dict):
        """
        Trigger callbacks for an event

        Args:
            event (str): Event name
            data (Dict): Event data
        """
        for callback in self.callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Callback error for {event}: {str(e)}")

    def update_config(self, auto_delete_enabled: bool = None, confidence_threshold: float = None):
        """
        Update monitor configuration from main thread

        Args:
            auto_delete_enabled (bool): Whether to auto delete spam
            confidence_threshold (float): Confidence threshold for spam detection
        """
        if auto_delete_enabled is not None:
            old_setting = self.auto_delete_enabled
            self.auto_delete_enabled = auto_delete_enabled
            logger.info(f"CONFIG UPDATE: Auto delete changed from {old_setting} to {auto_delete_enabled}")

        if confidence_threshold is not None:
            old_threshold = self.confidence_threshold
            self.confidence_threshold = confidence_threshold
            logger.info(f"CONFIG UPDATE: Confidence threshold changed from {old_threshold} to {confidence_threshold}")

    def get_config(self) -> Dict:
        """Get current configuration"""
        return {
            'auto_delete_enabled': self.auto_delete_enabled,
            'confidence_threshold': self.confidence_threshold,
            'poll_interval': self.poll_interval,
            'is_running': self.is_running,
            'internal_logs_count': len(self.internal_logs)
        }

    def sync_pending_spam_to_session_state(self):
        """
        Sync internal pending spam to session state
        This should be called from the main thread
        """
        try:
            if hasattr(st, 'session_state'):
                # Initialize session state if needed
                if 'pending_spam' not in st.session_state:
                    st.session_state.pending_spam = []

                # Add any new pending spam from internal storage
                session_ids = {item['comment_id'] for item in st.session_state.pending_spam}

                for spam_item in self.pending_spam:
                    if spam_item['comment_id'] not in session_ids:
                        st.session_state.pending_spam.append(spam_item)
                        logger.debug(f"Synced pending spam to session state: {spam_item['comment_id']}")

                return len(st.session_state.pending_spam)
            else:
                logger.warning("Session state not available for sync")
                return len(self.pending_spam)
        except Exception as e:
            logger.error(f"Error syncing pending spam to session state: {str(e)}")
            return len(self.pending_spam)

    def get_pending_spam_count(self) -> int:
        """Get count of pending spam comments"""
        return len(self.pending_spam)

    def _add_log_entry(self, action: str, comment_id: str, author: str, message: str, post_id: str, reason: str):
        """
        Add log entry to both internal storage and session state
        Thread-safe logging function
        """
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': action,
            'comment_id': comment_id,
            'author': author,
            'message': message[:100],
            'post_id': post_id,
            'reason': reason
        }

        # Add to internal storage (thread-safe)
        self.internal_logs.append(log_entry)

        # Keep only last 100 entries in internal storage
        if len(self.internal_logs) > 100:
            self.internal_logs = self.internal_logs[-100:]

        logger.info(f"LOG ADDED: {action} by {author} - Internal total: {len(self.internal_logs)}")

        # Session state access is problematic from threads, so we'll rely on sync function
        # The sync_logs_to_session_state() will handle moving logs to UI

        return log_entry

    def sync_logs_to_session_state(self):
        """
        Sync internal logs to session state
        This should be called from the main thread
        """
        try:
            if not hasattr(st, 'session_state'):
                logger.warning("Session state not available")
                return len(self.internal_logs)

            # Initialize session state if needed
            if 'monitor_logs' not in st.session_state:
                st.session_state.monitor_logs = []

            if not self.internal_logs:
                logger.debug("No internal logs to sync")
                return len(st.session_state.monitor_logs)

            # Get current session logs count for comparison
            old_session_count = len(st.session_state.monitor_logs)

            # Simple approach: replace session logs with internal logs
            # This ensures all logs are visible in UI
            st.session_state.monitor_logs = self.internal_logs.copy()

            # Keep only last 100 entries
            if len(st.session_state.monitor_logs) > 100:
                st.session_state.monitor_logs = st.session_state.monitor_logs[-100:]

            new_session_count = len(st.session_state.monitor_logs)

            logger.info(f"SYNC: Internal logs: {len(self.internal_logs)}, Session before: {old_session_count}, Session after: {new_session_count}")

            return new_session_count

        except Exception as e:
            logger.error(f"Error syncing logs to session state: {str(e)}")
            return len(self.internal_logs)

    def clear_pending_spam(self):
        """Clear internal pending spam storage"""
        self.pending_spam.clear()
        logger.info("Cleared internal pending spam storage")
    
    def start(self):
        """Start auto monitoring"""
        if self.is_running:
            logger.warning("Monitor is already running")
            return
        
        self.is_running = True
        self.statistics['start_time'] = datetime.now()
        self.processed_comments.clear()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Auto monitor started")
    
    def stop(self):
        """Stop auto monitoring"""
        if not self.is_running:
            logger.warning("Monitor is not running")
            return
        
        self.is_running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        logger.info("Auto monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting monitor loop")
        
        while self.is_running:
            try:
                # Sync configuration with session state before processing
                try:
                    if hasattr(st, 'session_state') and 'auto_delete_enabled' in st.session_state:
                        if self.auto_delete_enabled != st.session_state.auto_delete_enabled:
                            logger.info(f"Syncing auto_delete setting: {self.auto_delete_enabled} -> {st.session_state.auto_delete_enabled}")
                            self.auto_delete_enabled = st.session_state.auto_delete_enabled
                except Exception:
                    pass

                self._check_for_new_comments()
                self.last_check = datetime.now()

                # Update session state statistics
                if 'statistics' in st.session_state:
                    st.session_state.statistics.update(self.statistics)
                    st.session_state.statistics['last_check'] = self.last_check

                # Trigger stats update callback
                self.trigger_callback('on_stats_update', self.statistics)
                
            except Exception as e:
                self.statistics['errors'] += 1
                logger.error(f"Monitor loop error: {str(e)}")
                self.trigger_callback('on_error', {'error': str(e), 'timestamp': datetime.now()})
            
            # Wait for next poll
            for _ in range(self.poll_interval):
                if not self.is_running:
                    break
                time.sleep(1)
        
        logger.info("Monitor loop ended")
    
    def _check_for_new_comments(self):
        """Check for new comments and process them"""
        try:
            # Get recent posts
            posts = self.facebook_api.get_recent_posts(limit=5)
            
            for post in posts:
                post_id = post['id']
                
                # Get comments for this post
                comments = self.facebook_api.get_post_comments(post_id, limit=20)
                
                for comment in comments:
                    comment_id = comment['id']
                    
                    # Skip if already processed
                    if comment_id in self.processed_comments:
                        continue
                    
                    # Process new comment
                    self._process_comment(comment, post_id)
                    self.processed_comments.add(comment_id)
                    
                    # Limit processed comments set size
                    if len(self.processed_comments) > 1000:
                        # Remove oldest 200 entries
                        old_comments = list(self.processed_comments)[:200]
                        for old_id in old_comments:
                            self.processed_comments.discard(old_id)
        
        except Exception as e:
            logger.error(f"Error checking for new comments: {str(e)}")
            raise
    
    def _process_comment(self, comment: Dict, post_id: str):
        """
        Process a single comment for spam detection

        Args:
            comment (Dict): Comment data
            post_id (str): Post ID
        """
        try:
            comment_id = comment['id']
            message = comment.get('message', '')
            author = comment.get('from', {}).get('name', 'Unknown')

            if not message.strip():
                return

            # Update statistics
            self.statistics['comments_processed'] += 1

            # Log new comment detection
            self._add_log_entry('NEW_COMMENT', comment_id, author, message, post_id, 'New comment detected')

            # Get spam prediction
            prediction = self.spam_detector.predict(message)

            # Check if spam with high confidence
            is_spam = prediction['is_spam'] and prediction['confidence'] > self.confidence_threshold

            if is_spam:
                logger.info(f"Spam detected: {message[:50]}... (confidence: {prediction['confidence']:.3f})")

                # Update spam detected statistics
                if 'spam_detected' not in self.statistics:
                    self.statistics['spam_detected'] = 0
                self.statistics['spam_detected'] += 1

                # Log spam detection
                self._add_log_entry('SPAM_DETECTED', comment_id, author, message, post_id,
                                  f'Spam detected (confidence: {prediction["confidence"]:.3f})')

                # Trigger spam detected callback
                self.trigger_callback('on_spam_detected', {
                    'comment': comment,
                    'post_id': post_id,
                    'prediction': prediction,
                    'timestamp': datetime.now()
                })

                # CRITICAL: Always sync with session state before making delete decision
                current_auto_delete = self.auto_delete_enabled
                try:
                    if hasattr(st, 'session_state') and 'auto_delete_enabled' in st.session_state:
                        current_auto_delete = st.session_state.auto_delete_enabled
                        if self.auto_delete_enabled != current_auto_delete:
                            logger.info(f"SYNC: Auto delete setting changed from {self.auto_delete_enabled} to {current_auto_delete}")
                            self.auto_delete_enabled = current_auto_delete
                except Exception as e:
                    logger.error(f"Error syncing auto delete setting: {e}")

                logger.info(f"DECISION: Auto delete setting = {current_auto_delete} (UI: {getattr(st.session_state, 'auto_delete_enabled', 'N/A')})")

                if current_auto_delete:
                    # Auto delete spam comment
                    if self._delete_spam_comment(comment_id, message, author, post_id, "Auto deletion"):
                        self.statistics['spam_removed'] += 1

                        # Trigger comment deleted callback
                        self.trigger_callback('on_comment_deleted', {
                            'comment_id': comment_id,
                            'message': message,
                            'author': author,
                            'post_id': post_id,
                            'prediction': prediction,
                            'reason': 'Auto deletion',
                            'timestamp': datetime.now()
                        })
                else:
                    # Log spam detection but don't delete
                    logger.info(f"Spam detected but auto-delete disabled: {message[:50]}...")

                    # Log pending spam action
                    self._add_log_entry('PENDING_SPAM', comment_id, author, message, post_id,
                                      f'Spam added to pending review (auto-delete disabled)')

                    # Add to pending spam for manual review
                    self._add_to_pending_spam({
                        'comment_id': comment_id,
                        'message': message,
                        'author': author,
                        'post_id': post_id,
                        'prediction': prediction,
                        'detected_time': datetime.now().isoformat()
                    })
            else:
                logger.debug(f"Normal comment: {message[:50]}... (confidence: {prediction['confidence']:.3f})")

        except Exception as e:
            logger.error(f"Error processing comment {comment.get('id', 'unknown')}: {str(e)}")
            raise

    def _add_to_pending_spam(self, spam_data: Dict):
        """
        Add spam comment to pending review list

        Args:
            spam_data (Dict): Spam comment data
        """
        try:
            # Add to internal storage (thread-safe)
            self.pending_spam.append(spam_data)
            logger.info(f"Added spam comment to pending review: {spam_data['comment_id']}")

            # Also try to add to session state if available (best effort)
            try:
                if hasattr(st, 'session_state'):
                    if 'pending_spam' not in st.session_state:
                        st.session_state.pending_spam = []
                    st.session_state.pending_spam.append(spam_data)
            except Exception as session_error:
                logger.debug(f"Could not sync to session state: {session_error}")

        except Exception as e:
            logger.error(f"Error adding to pending spam: {str(e)}")
    
    def _delete_spam_comment(self, comment_id: str, message: str, author: str, post_id: str, reason: str = "Auto deletion") -> bool:
        """
        Delete a spam comment

        Args:
            comment_id (str): Comment ID
            message (str): Comment message
            author (str): Comment author
            post_id (str): Post ID
            reason (str): Reason for deletion

        Returns:
            bool: True if successful
        """
        try:
            success = self.facebook_api.delete_comment(comment_id)

            if success:
                logger.info(f"Deleted spam comment by {author}: {message[:50]}... (Reason: {reason})")

                # Log deletion
                self._add_log_entry('DELETED', comment_id, author, message, post_id, reason)

                return True
            else:
                logger.warning(f"Failed to delete comment {comment_id}")
                return False

        except Exception as e:
            logger.error(f"Error deleting comment {comment_id}: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get current monitoring statistics"""
        stats = self.statistics.copy()
        stats['is_running'] = self.is_running
        stats['last_check'] = self.last_check
        
        if stats['start_time']:
            runtime = datetime.now() - stats['start_time']
            stats['runtime_seconds'] = runtime.total_seconds()
            stats['runtime_formatted'] = f"{runtime.seconds // 3600}h {(runtime.seconds % 3600) // 60}m {runtime.seconds % 60}s"
        
        return stats
    
    def reset_statistics(self):
        """Reset monitoring statistics"""
        self.statistics = {
            'comments_processed': 0,
            'spam_removed': 0,
            'errors': 0,
            'start_time': datetime.now() if self.is_running else None
        }
        self.processed_comments.clear()
        logger.info("Statistics reset")
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """
        Get recent monitoring activity

        Args:
            limit (int): Number of recent activities to return

        Returns:
            List[Dict]: Recent activity log
        """
        # Try session state first
        if hasattr(st, 'session_state') and 'monitor_logs' in st.session_state and st.session_state.monitor_logs:
            return st.session_state.monitor_logs[-limit:]

        # Fallback to internal logs
        if self.internal_logs:
            return self.internal_logs[-limit:]

        return []
    
    def manual_check_post(self, post_id: str) -> Dict:
        """
        Manually check a specific post for spam comments
        
        Args:
            post_id (str): Post ID to check
            
        Returns:
            Dict: Check results
        """
        try:
            results = {
                'post_id': post_id,
                'comments_checked': 0,
                'spam_found': 0,
                'spam_removed': 0,
                'errors': 0,
                'details': []
            }
            
            # Get comments for the post
            comments = self.facebook_api.get_post_comments(post_id, limit=50)
            
            for comment in comments:
                results['comments_checked'] += 1
                
                try:
                    message = comment.get('message', '')
                    if not message.strip():
                        continue
                    
                    # Get spam prediction
                    prediction = self.spam_detector.predict(message)
                    
                    # Check if spam
                    confidence_threshold = float(st.session_state.get('confidence_threshold', 0.8))
                    is_spam = prediction['is_spam'] and prediction['confidence'] > confidence_threshold
                    
                    comment_result = {
                        'comment_id': comment['id'],
                        'message': message[:100],
                        'author': comment.get('from', {}).get('name', 'Unknown'),
                        'is_spam': is_spam,
                        'confidence': prediction['confidence'],
                        'deleted': False
                    }
                    
                    if is_spam:
                        results['spam_found'] += 1
                        
                        # Delete spam comment
                        if self._delete_spam_comment(comment['id'], message, comment_result['author'], post_id):
                            results['spam_removed'] += 1
                            comment_result['deleted'] = True
                    
                    results['details'].append(comment_result)
                    
                except Exception as e:
                    results['errors'] += 1
                    logger.error(f"Error processing comment in manual check: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in manual post check: {str(e)}")
            return {
                'post_id': post_id,
                'error': str(e),
                'comments_checked': 0,
                'spam_found': 0,
                'spam_removed': 0,
                'errors': 1
            }
    
    def get_status(self) -> Dict:
        """Get current monitor status"""
        return {
            'is_running': self.is_running,
            'poll_interval': self.poll_interval,
            'last_check': self.last_check,
            'statistics': self.get_statistics(),
            'processed_comments_count': len(self.processed_comments)
        }
