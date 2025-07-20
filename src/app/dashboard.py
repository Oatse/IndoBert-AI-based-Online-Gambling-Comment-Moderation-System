#!/usr/bin/env python3
"""
Dashboard Module
Contains dashboard-specific rendering logic and recent activity display
"""

import streamlit as st
from typing import Dict, Optional
from datetime import datetime
from src.app.ui_components import NotificationManager, render_comment_card


class DashboardRenderer:
    """Handles dashboard rendering and recent activity display"""
    
    def __init__(self, facebook_api, spam_detector, confidence_threshold: float):
        self.facebook_api = facebook_api
        self.spam_detector = spam_detector
        self.confidence_threshold = confidence_threshold
    
    def render_dashboard(self):
        """Render main dashboard - ONLY dashboard content, NO logs components"""
        # CRITICAL: This method should NEVER render logs components
        # All logs components should ONLY be in render_logs() method

        # Use isolated container with unique key to prevent bleeding
        dashboard_key = "dashboard_main_container"

        # Clear any existing dashboard state to prevent bleeding
        if f"{dashboard_key}_state" in st.session_state:
            del st.session_state[f"{dashboard_key}_state"]

        dashboard_container = st.container(key=dashboard_key)
        with dashboard_container:
            # Header with auto-refresh status
            col_header, col_status = st.columns([3, 1])

            with col_header:
                st.markdown('<h1 class="main-header">🛡️ Judol Remover</h1>', unsafe_allow_html=True)

            with col_status:
                # Show auto-refresh status
                if (st.session_state.get('monitor_running', False) and
                    st.session_state.get('auto_refresh_enabled', False)):
                    refresh_count = st.session_state.get('refresh_counter', 0)
                    st.success(f"🔄 Auto Refresh ON (#{refresh_count})")
                elif st.session_state.get('monitor_running', False):
                    st.warning("⏸️ Auto Refresh OFF")
                else:
                    st.info("⏹️ Monitor Stopped")

            # Metrics row - isolated within dashboard container
            col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Comments Processed",
                st.session_state.statistics['comments_processed'],
                delta=None
            )

        with col2:
            spam_detected = st.session_state.statistics.get('spam_detected', 0)
            st.metric(
                "Spam Detected",
                spam_detected,
                delta=None
            )

        with col3:
            st.metric(
                "Spam Removed",
                st.session_state.statistics['spam_removed'],
                delta=None
            )

        with col4:
            pending_count = len(st.session_state.get('pending_spam', []))
            st.metric(
                "Pending Review",
                pending_count,
                delta=None,
                help="Spam comments waiting for manual review"
            )

        with col5:
            status = "🟢 Running" if st.session_state.monitor_running else "🔴 Stopped"
            st.metric("Monitor Status", status)

        # Show auto delete status
        auto_delete_status = "🟢 Enabled" if st.session_state.auto_delete_enabled else "🔴 Disabled"
        st.info(f"Auto Delete: {auto_delete_status}")

        # Sync pending spam from auto monitor
        if 'auto_monitor' in st.session_state and st.session_state.auto_monitor is not None:
            try:
                st.session_state.auto_monitor.sync_pending_spam_to_session_state()
            except Exception:
                pass

        # Show pending spam alert
        pending_count = len(st.session_state.get('pending_spam', []))
        if pending_count > 0 and not st.session_state.auto_delete_enabled:
            st.warning(f"⚠️ {pending_count} spam comments are waiting for manual review. Go to 'Pending Spam' page to review them.")

        st.markdown("---")

        # Recent posts and comments - ONLY Facebook posts, NO logs
        self.render_recent_activity()
    
    def render_recent_activity(self):
        """Render recent posts and comments - DASHBOARD ONLY, NO LOGS"""
        # CRITICAL: This method is for dashboard only
        # It should NEVER render logs, activity logs, or monitoring logs
        # All logs should ONLY be rendered in render_logs() method

        st.markdown("### 📝 Recent Posts & Comments")

        # ONLY render Facebook posts and comments - NO logs components
        self.render_posts_and_comments()

    def render_posts_and_comments(self):
        """Render recent posts and comments from Facebook - FACEBOOK ONLY, NO LOGS"""
        # CRITICAL GUARD: This method should ONLY render Facebook posts and comments
        # It should NEVER render any logs, activity logs, monitoring logs, or log buttons
        # All logs components belong ONLY in render_logs() method

        if not self.facebook_api:
            st.warning("⚠️ Facebook API not connected. Please check your access token.")
            return

        # Refresh button for Facebook posts only with unique key
        if st.button("🔄 Refresh Posts", key="dashboard_refresh_posts_btn"):
            st.session_state.posts_cache = {}
            st.session_state.comments_cache = {}
            # Use experimental_rerun to avoid component conflicts
            st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()

        try:
            # Get recent posts from Facebook
            posts = self.facebook_api.get_recent_posts(limit=10)

            if not posts:
                st.info("No recent posts found.")
                return

            # Display Facebook posts with collapsible comments
            for post in posts:
                with st.expander(f"📄 Post from {post.get('created_time', 'Unknown time')}", expanded=False):
                    # Post content
                    if post.get('message'):
                        st.markdown(f"**Content:** {post['message'][:200]}...")

                    # Load comments for this post
                    self.render_post_comments(post['id'])

        except Exception as e:
            st.error(f"❌ Error loading posts: {str(e)}")

        # CRITICAL: NO logs rendering code should be here
        # This method is for Facebook posts ONLY
    
    def render_post_comments(self, post_id: str):
        """Render comments for a specific post"""
        try:
            # Get comments
            comments = self.facebook_api.get_post_comments(post_id, limit=10)
            
            if not comments:
                st.info("No comments found for this post.")
                return
            
            st.markdown(f"**Comments ({len(comments)}):**")
            
            # Process each comment
            for comment in comments:
                self.render_comment_with_detection(comment, post_id)
                
        except Exception as e:
            st.error(f"❌ Error loading comments: {str(e)}")
    
    def render_comment_with_detection(self, comment: Dict, post_id: str):
        """Render individual comment with spam detection"""
        comment_id = comment['id']
        message = comment.get('message', '')
        author = comment.get('from', {}).get('name', 'Unknown')
        
        # Get spam prediction
        try:
            prediction = self.spam_detector.predict(message)
            is_spam = prediction['is_spam'] and prediction['confidence'] > self.confidence_threshold
        except Exception as e:
            prediction = {'is_spam': False, 'confidence': 0.0, 'label': 'error', 'error': str(e)}
            is_spam = False
        
        # Use the reusable comment card component
        render_comment_card(
            comment=comment,
            post_id=post_id,
            is_spam=is_spam,
            prediction=prediction,
            confidence_threshold=self.confidence_threshold,
            facebook_api=self.facebook_api,
            spam_detector=self.spam_detector,
            delete_callback=self.delete_comment
        )
    
    def delete_comment(self, comment_id: str, post_id: str, message: str, author: str, reason: str = "Manual deletion"):
        """Delete a comment"""
        try:
            success = self.facebook_api.delete_comment(comment_id)
            if success:
                st.session_state.statistics['spam_removed'] += 1
                NotificationManager.show_notification(f"Deleted comment by {author} ({reason})", "success", 4000)

                # Log the deletion
                if 'monitor_logs' not in st.session_state:
                    st.session_state.monitor_logs = []

                log_entry = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'action': 'DELETED',
                    'comment_id': comment_id,
                    'author': author,
                    'message': message[:100],
                    'post_id': post_id,
                    'reason': reason
                }
                st.session_state.monitor_logs.append(log_entry)

                # Clear cache to refresh comments
                if post_id in st.session_state.comments_cache:
                    del st.session_state.comments_cache[post_id]
                # Use experimental_rerun to avoid component conflicts
                st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()
            else:
                NotificationManager.show_notification("Failed to delete comment", "error", 5000)
        except Exception as e:
            NotificationManager.show_notification(f"Error deleting comment: {str(e)}", "error", 5000)
