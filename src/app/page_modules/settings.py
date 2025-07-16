#!/usr/bin/env python3
"""
Settings Page Module
Handles application settings and configuration
"""

import streamlit as st
from src.app.ui_components import NotificationManager
from src.services.spam_detector import SpamDetector


class SettingsPage:
    """Handles settings page rendering and functionality"""
    
    def __init__(self, page_id: str, page_access_token: str, model_path: str, confidence_threshold: float):
        self.page_id = page_id
        self.page_access_token = page_access_token
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
    
    def render(self):
        """Render settings page"""
        # Use isolated container with unique key to prevent bleeding
        settings_key = "settings_main_container"

        # Clear any existing settings state to prevent bleeding
        if f"{settings_key}_state" in st.session_state:
            del st.session_state[f"{settings_key}_state"]

        settings_container = st.container(key=settings_key)
        with settings_container:
            st.markdown("### ⚙️ Settings")

            # Facebook API Settings
            st.markdown("#### 📘 Facebook API Configuration")

            col1, col2 = st.columns(2)

            with col1:
                page_id = st.text_input("Page ID", value=self.page_id or "", help="Facebook Page ID")

            with col2:
                page_access_token = st.text_input(
                    "Page Access Token",
                    value=self.page_access_token or "",
                    type="password",
                    help="Facebook Page Access Token"
                )

            if st.button("💾 Update Facebook Settings"):
                if page_id and page_access_token:
                    try:
                        # Test new credentials
                        from src.app.streamlit_facebook import FacebookAPI
                        test_api = FacebookAPI(page_id, page_access_token)

                        # Update session state
                        st.session_state.facebook_api = test_api
                        self.page_id = page_id
                        self.page_access_token = page_access_token

                        NotificationManager.show_notification("Facebook API settings updated successfully!", "success", 4000)
                    except Exception as e:
                        NotificationManager.show_notification(f"Failed to update Facebook settings: {str(e)}", "error", 6000)
                else:
                    st.warning("Please provide both Page ID and Access Token")

            st.markdown("---")

            # Spam Detection Settings
            st.markdown("#### 🤖 Spam Detection Configuration")

            confidence_threshold = st.slider(
                "Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=self.confidence_threshold,
                step=0.05,
                help="Minimum confidence required to classify and delete as spam"
            )

            model_path = st.text_input(
                "Model Path",
                value=self.model_path,
                help="Path to the IndoBERT model directory"
            )

            if st.button("💾 Update Detection Settings"):
                self.confidence_threshold = confidence_threshold
                st.session_state.confidence_threshold = confidence_threshold

                if model_path != self.model_path:
                    try:
                        # Reload model with new path
                        with st.spinner("Reloading spam detection model..."):
                            st.session_state.spam_detector = SpamDetector(model_path)
                        self.model_path = model_path
                        NotificationManager.show_notification("Model reloaded successfully!", "success", 4000)
                    except Exception as e:
                        NotificationManager.show_notification(f"Failed to reload model: {str(e)}", "error", 6000)
                else:
                    NotificationManager.show_notification("Detection settings updated!", "success", 3000)

            st.markdown("---")

            # Monitor Settings
            st.markdown("#### 🔄 Auto Monitor Configuration")

            poll_interval = st.number_input(
                "Poll Interval (seconds)",
                min_value=10,
                max_value=300,
                value=30,
                step=5,
                help="How often to check for new comments"
            )

            auto_delete = st.checkbox(
                "Auto Delete Spam",
                value=True,
                help="Automatically delete comments detected as spam"
            )

            if st.button("💾 Update Monitor Settings"):
                st.session_state.poll_interval = poll_interval
                st.session_state.auto_delete = auto_delete
                NotificationManager.show_notification("Monitor settings updated!", "success", 3000)

            st.markdown("---")

            # System Information
            st.markdown("#### 📊 System Information")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Model Status:**")
                if st.session_state.spam_detector:
                    st.success("🟢 Loaded")
                    st.write(f"Model Path: `{self.model_path}`")
                else:
                    st.error("🔴 Not Loaded")

            with col2:
                st.markdown("**Facebook API Status:**")
                if st.session_state.facebook_api:
                    st.success("🟢 Connected")
                    st.write(f"Page ID: `{self.page_id}`")
                else:
                    st.error("🔴 Not Connected")

            # Cache Management
            st.markdown("---")
            st.markdown("#### 🗂️ Cache Management")

            col1, col2, col3 = st.columns(3)

            with col1:
                posts_cache_size = len(st.session_state.posts_cache)
                st.metric("Posts Cache", posts_cache_size)

            with col2:
                comments_cache_size = len(st.session_state.comments_cache)
                st.metric("Comments Cache", comments_cache_size)

            with col3:
                if st.button("🗑️ Clear Cache"):
                    st.session_state.posts_cache = {}
                    st.session_state.comments_cache = {}
                    NotificationManager.show_notification("Cache cleared!", "info", 2000)
                    st.rerun()
