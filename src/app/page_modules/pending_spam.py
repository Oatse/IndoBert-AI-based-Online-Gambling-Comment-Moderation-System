#!/usr/bin/env python3
"""
Pending Spam Page Module
Handles pending spam comments review and management
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List
from src.app.ui_components import NotificationManager


class PendingSpamPage:
    """Handles pending spam page rendering and functionality"""
    
    def __init__(self, facebook_api):
        self.facebook_api = facebook_api
    
    def render(self):
        """Render pending spam page for manual review"""
        # Use isolated container with unique key to prevent bleeding
        pending_spam_key = "pending_spam_main_container"

        # Clear any existing pending spam state to prevent bleeding
        if f"{pending_spam_key}_state" in st.session_state:
            del st.session_state[f"{pending_spam_key}_state"]

        pending_spam_container = st.container(key=pending_spam_key)
        with pending_spam_container:
            st.markdown("### 🚨 Pending Spam Comments")
            st.markdown("Komentar yang terdeteksi sebagai spam tapi belum dihapus karena auto-delete dinonaktifkan.")

            # Initialize pending spam if not exists
            if 'pending_spam' not in st.session_state:
                st.session_state.pending_spam = []

            pending_comments = st.session_state.pending_spam

            if not pending_comments:
                st.info("📭 Tidak ada komentar spam yang menunggu review.")
                if not st.session_state.auto_delete_enabled:
                    st.warning("💡 Auto-delete sedang dinonaktifkan. Aktifkan di sidebar untuk menghapus spam secara otomatis.")
                return

            st.markdown(f"#### 📊 {len(pending_comments)} komentar menunggu review")

            # Bulk actions
            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("🗑️ Delete All Spam", type="primary"):
                    deleted_count = 0
                    for comment in pending_comments[:]:  # Copy list to avoid modification during iteration
                        try:
                            success = self.facebook_api.delete_comment(comment['comment_id'])
                            if success:
                                deleted_count += 1
                                st.session_state.pending_spam.remove(comment)

                                # Log the deletion
                                self._log_deletion(comment, "Bulk manual deletion")

                        except Exception as e:
                            st.error(f"Failed to delete comment {comment['comment_id']}: {str(e)}")

                    NotificationManager.show_notification(f"Deleted {deleted_count} spam comments", "success", 4000)
                    st.rerun()

            with col2:
                if st.button("✅ Mark All as Normal"):
                    st.session_state.pending_spam = []
                    NotificationManager.show_notification("All comments marked as normal", "info", 3000)
                    st.rerun()

            # Display pending comments
            for i, comment in enumerate(pending_comments):
                with st.expander(f"🚨 Spam #{i+1} - {comment['author']}", expanded=False):
                    st.markdown(f"**Author:** {comment['author']}")
                    st.markdown(f"**Message:** {comment['message']}")
                    st.markdown(f"**Confidence:** {comment['prediction']['confidence']:.3f}")
                    st.markdown(f"**Detected:** {comment['detected_time']}")

                    # Individual actions
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        if st.button(f"🗑️ Delete", key=f"delete_pending_{i}"):
                            try:
                                success = self.facebook_api.delete_comment(comment['comment_id'])
                                if success:
                                    st.session_state.pending_spam.remove(comment)
                                    self._log_deletion(comment, "Manual deletion from pending")
                                    NotificationManager.show_notification("Comment deleted", "success", 3000)
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete comment")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")

                    with col2:
                        if st.button(f"✅ Mark Normal", key=f"normal_pending_{i}"):
                            st.session_state.pending_spam.remove(comment)
                            NotificationManager.show_notification("Marked as normal", "info", 2000)
                            st.rerun()

                    # Show prediction details
                    st.json(comment['prediction'])

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
