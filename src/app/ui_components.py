#!/usr/bin/env python3
"""
UI Components Module
Contains reusable UI components, CSS styles, and notification management for the Streamlit app
"""

import streamlit as st
import time
import uuid
from typing import Optional


def load_custom_css():
    """Load custom CSS styles for the application"""
    st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 4rem;
    
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .spam-comment {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
    .normal-comment {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
    .stButton > button {
        width: 100%;
    }
    /* Reduce UI flicker and smooth transitions - scoped to avoid bleeding */
    .main .stApp {
        transition: none;
    }
    .main .element-container {
        transition: none;
    }
    .main .stMetric {
        transition: all 0.3s ease;
    }
    /* Sidebar metrics real-time styling */
    .sidebar .stMetric {
        animation: pulse-subtle 3s infinite;
    }
    @keyframes pulse-subtle {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.9; }
    }
    /* Prevent layout shift */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    /* Custom notification styles */
    .custom-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        line-height: 1.4;
        animation: slideInRight 0.3s ease-out;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .custom-notification:hover {
        transform: translateX(-5px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    }

    .notification-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }

    .notification-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }

    .notification-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }

    .notification-info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }

    .notification-close {
        float: right;
        font-size: 18px;
        font-weight: bold;
        line-height: 1;
        color: inherit;
        opacity: 0.5;
        margin-left: 15px;
        cursor: pointer;
        transition: opacity 0.2s;
    }

    .notification-close:hover {
        opacity: 1;
    }

    .notification-icon {
        display: inline-block;
        margin-right: 8px;
        font-size: 16px;
    }

    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }

    .notification-fade-out {
        animation: slideOutRight 0.3s ease-in forwards;
    }

    /* Hide Streamlit's default navigation - scoped to prevent bleeding */
    .main .stTabs [data-baseweb="tab-list"] {
        display: none;
    }

    /* Hide main content tabs/navigation - scoped */
    .main .stTabs {
        display: none;
    }

    /* Hide any tab-like navigation in main area - scoped */
    .main [data-testid="stTabs"] {
        display: none;
    }

    /* Keep sidebar navigation visible */
    .sidebar .stSelectbox {
        display: block;
    }
</style>
""", unsafe_allow_html=True)


class NotificationManager:
    """Manages custom notifications with auto-hide functionality"""

    @staticmethod
    def show_notification(message: str, notification_type: str = "success", duration: int = 5000, auto_hide: bool = True):
        """
        Show a custom notification using Streamlit's built-in components with custom styling

        Args:
            message: The notification message
            notification_type: Type of notification (success, error, warning, info)
            duration: Duration in seconds before auto-hide (default: 5)
            auto_hide: Whether to auto-hide the notification
        """
        # Initialize notifications list in session state
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []

        # Create notification ID
        notification_id = str(uuid.uuid4())

        # Add notification to session state
        notification = {
            'id': notification_id,
            'message': message,
            'type': notification_type,
            'duration': duration,
            'auto_hide': auto_hide,
            'timestamp': time.time(),
            'show': True
        }

        st.session_state.notifications.append(notification)

        # Show notification immediately using toast (Streamlit 1.27+)
        try:
            if notification_type == "success":
                st.toast(f"{message}", icon="✅")
            elif notification_type == "error":
                st.toast(f"{message}", icon="❌")
            elif notification_type == "warning":
                st.toast(f"{message}", icon="⚠️")
            elif notification_type == "info":
                st.toast(f"{message}", icon="ℹ️")
        except AttributeError:
            # Fallback for older Streamlit versions
            NotificationManager._show_fallback_notification(message, notification_type)

    @staticmethod
    def _show_fallback_notification(message: str, notification_type: str):
        """Fallback notification for older Streamlit versions"""
        # Create a container at the top of the page
        if 'notification_container' not in st.session_state:
            st.session_state.notification_container = st.empty()

        # Style mapping
        styles = {
            'success': {'color': '#155724', 'background': '#d4edda', 'border': '#c3e6cb', 'icon': '✅'},
            'error': {'color': '#721c24', 'background': '#f8d7da', 'border': '#f5c6cb', 'icon': '❌'},
            'warning': {'color': '#856404', 'background': '#fff3cd', 'border': '#ffeaa7', 'icon': '⚠️'},
            'info': {'color': '#0c5460', 'background': '#d1ecf1', 'border': '#bee5eb', 'icon': 'ℹ️'}
        }

        style = styles.get(notification_type, styles['info'])

        # Create notification HTML
        notification_html = f"""
        <div style="
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            padding: 15px 20px;
            border-radius: 8px;
            background-color: {style['background']};
            border: 1px solid {style['border']};
            color: {style['color']};
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.4;
            animation: slideInRight 0.3s ease-out;
        ">
            <span style="margin-right: 8px; font-size: 16px;">{style['icon']}</span>
            {message}
        </div>

        <style>
        @keyframes slideInRight {{
            from {{
                transform: translateX(100%);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
        </style>
        """

        # Show notification
        st.session_state.notification_container.markdown(notification_html, unsafe_allow_html=True)

        # Auto-hide after delay
        time.sleep(0.1)  # Small delay to ensure rendering

    @staticmethod
    def _render_notifications():
        """Render all active notifications (for compatibility)"""
        # Filter out expired notifications
        if 'notifications' not in st.session_state:
            return

        current_time = time.time()
        active_notifications = []

        for notification in st.session_state.notifications:
            if notification['auto_hide']:
                # Check if notification has expired
                elapsed_time = current_time - notification['timestamp']
                if elapsed_time < notification['duration']:
                    active_notifications.append(notification)
            else:
                active_notifications.append(notification)

        st.session_state.notifications = active_notifications

    @staticmethod
    def display_notifications():
        """Display all active notifications (for compatibility)"""
        NotificationManager._render_notifications()

    @staticmethod
    def clear_all_notifications():
        """Clear all notifications and containers"""
        if 'notifications' in st.session_state:
            st.session_state.notifications = []
        if 'notification_container' in st.session_state:
            try:
                st.session_state.notification_container.empty()
                # Remove the container reference to prevent persistence
                del st.session_state.notification_container
            except Exception:
                # If container is already gone, just remove the reference
                if 'notification_container' in st.session_state:
                    del st.session_state.notification_container

    @staticmethod
    def clear_page_notifications(page_name: str):
        """Clear notifications specific to a page to prevent bleeding"""
        if 'notifications' not in st.session_state:
            return

        # Filter out notifications that might be page-specific
        current_notifications = st.session_state.notifications
        filtered_notifications = []

        for notification in current_notifications:
            # Keep notifications that are not expired and not page-specific
            if notification.get('page') != page_name:
                filtered_notifications.append(notification)

        st.session_state.notifications = filtered_notifications


def render_comment_card(comment: dict, post_id: str, is_spam: bool, prediction: dict, 
                       confidence_threshold: float, facebook_api, spam_detector, 
                       delete_callback=None):
    """
    Render individual comment with spam detection
    
    Args:
        comment: Comment data from Facebook API
        post_id: ID of the post containing the comment
        is_spam: Whether the comment is classified as spam
        prediction: Spam detection prediction results
        confidence_threshold: Minimum confidence threshold for spam classification
        facebook_api: Facebook API instance
        spam_detector: Spam detector instance
        delete_callback: Optional callback function for comment deletion
    """
    comment_id = comment['id']
    message = comment.get('message', '')
    author = comment.get('from', {}).get('name', 'Unknown')
    created_time = comment.get('created_time', '')
    
    # Style based on spam detection
    card_class = "spam-comment" if is_spam else "normal-comment"
    emoji = "🚨" if is_spam else "✅"
    
    # Create comment card
    with st.container():
        st.markdown(f"""
        <div class="{card_class}">
            <strong>{emoji} {author}</strong> - {created_time}<br>
            <em>"{message[:100]}{'...' if len(message) > 100 else ''}"</em><br>
            <small>Confidence: {prediction['confidence']:.3f} | Label: {prediction['label']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2 = st.columns([1, 1])

        with col1:
            # Show delete button for spam comments or allow manual delete for any comment
            if is_spam:
                if st.session_state.get('auto_delete_enabled', False):
                    st.info("🤖 Auto-deleted")
                else:
                    if st.button(f"🗑️ Delete Spam", key=f"delete_{comment_id}", type="primary"):
                        if delete_callback:
                            delete_callback(comment_id, post_id, message, author, "Manual spam deletion")
            else:
                if st.button(f"🗑️ Delete", key=f"delete_{comment_id}", help="Manual moderation"):
                    if delete_callback:
                        delete_callback(comment_id, post_id, message, author, "Manual moderation")

        with col2:
            if st.button(f"🔍 Details", key=f"details_{comment_id}"):
                st.json({
                    "comment": comment,
                    "prediction": prediction
                })
