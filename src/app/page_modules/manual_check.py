#!/usr/bin/env python3
"""
Manual Check Page Module
Handles manual spam checking functionality
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List
from src.app.ui_components import NotificationManager


class ManualCheckPage:
    """Handles manual check page rendering and functionality"""
    
    def __init__(self, facebook_api, spam_detector, confidence_threshold: float):
        self.facebook_api = facebook_api
        self.spam_detector = spam_detector
        self.confidence_threshold = confidence_threshold
    
    def render(self):
        """Render manual check page"""
        # Use isolated container with unique key to prevent bleeding
        manual_check_key = "manual_check_main_container"

        # Clear any existing manual check state to prevent bleeding
        if f"{manual_check_key}_state" in st.session_state:
            del st.session_state[f"{manual_check_key}_state"]

        manual_check_container = st.container(key=manual_check_key)
        with manual_check_container:
            st.markdown("### 🔍 Manual Comment Check")

            if not self.facebook_api:
                st.warning("⚠️ Facebook API not connected.")
                st.info("💡 Please configure your Facebook API credentials in the Settings page.")
                st.markdown("---")
                st.markdown("#### 📋 Manual Check Interface Preview")
                st.selectbox("Choose a post (Preview)", ["Connect Facebook API to see posts"], disabled=True)
                st.button("🔍 Check Post (Disabled)", disabled=True)
                return

            # Post selection
            st.markdown("#### Select Post to Check")

            try:
                posts = self.facebook_api.get_recent_posts(limit=10)

                if not posts:
                    st.info("No posts found.")
                    return

                # Create post options
                post_options = {}
                for post in posts:
                    preview = post.get('message', 'No message')[:50] + "..."
                    created_time = post.get('created_time', 'Unknown time')
                    option_text = f"{created_time} - {preview}"
                    post_options[option_text] = post['id']

                selected_post_text = st.selectbox("Choose a post:", list(post_options.keys()))
                selected_post_id = post_options[selected_post_text]

                col1, col2 = st.columns([1, 4])

                with col1:
                    if st.button("🔍 Check Post", type="primary"):
                        with st.spinner("Checking post for spam comments..."):
                            # Perform manual check without depending on AutoMonitor
                            results = self.perform_manual_check(selected_post_id)
                            st.session_state.manual_check_results = results

                # Display results
                if 'manual_check_results' in st.session_state:
                    results = st.session_state.manual_check_results

                    st.markdown("#### 📊 Check Results")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Comments Checked", results['comments_checked'])
                    with col2:
                        st.metric("Spam Found", results['spam_found'])
                    with col3:
                        st.metric("Spam Removed", results['spam_removed'])
                    with col4:
                        st.metric("Errors", results['errors'])

                    # Detailed results
                    if results.get('details'):
                        st.markdown("#### 📝 Detailed Results")

                        for detail in results['details']:
                            emoji = "🚨" if detail['is_spam'] else "✅"
                            status = "DELETED" if detail.get('deleted') else ("SPAM" if detail['is_spam'] else "NORMAL")

                            with st.expander(f"{emoji} {detail['author']} - {status}"):
                                st.write(f"**Message:** {detail['message']}")
                                st.write(f"**Confidence:** {detail['confidence']:.3f}")
                                st.write(f"**Comment ID:** {detail['comment_id']}")
                                if detail.get('deleted'):
                                    st.success("✅ Comment deleted successfully")

            except Exception as e:
                st.error(f"❌ Error in manual check: {str(e)}")

    def perform_manual_check(self, post_id: str) -> Dict:
        """Perform manual spam check on a post without AutoMonitor dependency"""
        try:
            # Get comments for the post
            comments = self.facebook_api.get_post_comments(post_id, limit=50)

            results = {
                'comments_checked': 0,
                'spam_found': 0,
                'spam_removed': 0,
                'errors': 0,
                'details': []
            }

            if not comments:
                return results

            for comment in comments:
                try:
                    comment_id = comment['id']
                    message = comment.get('message', '')
                    author = comment.get('from', {}).get('name', 'Unknown')

                    # Skip empty messages
                    if not message.strip():
                        continue

                    results['comments_checked'] += 1

                    # Get spam prediction
                    prediction = self.spam_detector.predict(message)
                    is_spam = prediction['is_spam'] and prediction['confidence'] > self.confidence_threshold

                    detail = {
                        'comment_id': comment_id,
                        'author': author,
                        'message': message,
                        'is_spam': is_spam,
                        'confidence': prediction['confidence'],
                        'label': prediction['label'],
                        'deleted': False
                    }

                    if is_spam:
                        results['spam_found'] += 1

                        # Only delete if auto-delete is enabled
                        if st.session_state.auto_delete_enabled:
                            try:
                                success = self.facebook_api.delete_comment(comment_id)
                                if success:
                                    results['spam_removed'] += 1
                                    detail['deleted'] = True

                                    # Log the deletion
                                    self._log_deletion({
                                        'comment_id': comment_id,
                                        'author': author,
                                        'message': message,
                                        'post_id': post_id,
                                        'prediction': prediction
                                    }, "Manual check deletion")

                            except Exception as e:
                                results['errors'] += 1
                                detail['error'] = str(e)
                        else:
                            # Add to pending spam if auto-delete is disabled
                            if 'pending_spam' not in st.session_state:
                                st.session_state.pending_spam = []

                            pending_item = {
                                'comment_id': comment_id,
                                'author': author,
                                'message': message,
                                'post_id': post_id,
                                'prediction': prediction,
                                'detected_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }

                            # Check if not already in pending
                            if not any(p['comment_id'] == comment_id for p in st.session_state.pending_spam):
                                st.session_state.pending_spam.append(pending_item)

                    results['details'].append(detail)

                except Exception as e:
                    results['errors'] += 1
                    results['details'].append({
                        'comment_id': comment.get('id', 'unknown'),
                        'author': comment.get('from', {}).get('name', 'Unknown'),
                        'message': comment.get('message', ''),
                        'is_spam': False,
                        'confidence': 0.0,
                        'label': 'error',
                        'deleted': False,
                        'error': str(e)
                    })

            return results

        except Exception as e:
            return {
                'comments_checked': 0,
                'spam_found': 0,
                'spam_removed': 0,
                'errors': 1,
                'details': [],
                'error': str(e)
            }

    def _log_deletion(self, comment: Dict, reason: str):
        """Helper function to log comment deletion"""
        if 'monitor_logs' not in st.session_state:
            st.session_state.monitor_logs = []

        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': 'DELETED',
            'comment_id': comment['comment_id'],
            'author': comment['author'],
            'message': comment['message'][:100],
            'post_id': comment['post_id'],
            'reason': reason
        }
        st.session_state.monitor_logs.append(log_entry)

        # Update statistics
        st.session_state.statistics['spam_removed'] += 1
