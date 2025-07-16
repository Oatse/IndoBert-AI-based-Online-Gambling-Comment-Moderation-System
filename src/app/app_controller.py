#!/usr/bin/env python3
"""
Main Application Controller
Coordinates between different modules and handles application flow
"""

import streamlit as st
import os
import time
from datetime import datetime
from typing import Optional

# Import custom modules with robust path handling
import sys
from pathlib import Path

# Add project root to path for deployment compatibility
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from src.services.spam_detector import SpamDetector
from src.app.streamlit_facebook import FacebookAPI
from src.app.streamlit_monitor import AutoMonitor
from config.app_config import config

# Import UI and page modules
from src.app.ui_components import NotificationManager, load_custom_css
from src.app.dashboard import DashboardRenderer
from src.app.page_modules.manual_check import ManualCheckPage
from src.app.page_modules.pending_spam import PendingSpamPage
from src.app.page_modules.test_detector import TestDetectorPage
from src.app.page_modules.settings import SettingsPage
from src.app.page_modules.logs import LogsPage


class StreamlitJudolRemover:
    """Main application controller that coordinates between different modules"""
    
    def __init__(self):
        self.initialize_session_state()
        self.load_environment()
        self.initialize_services()
        # Page renderers will be initialized when needed in run() method
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'spam_detector' not in st.session_state:
            st.session_state.spam_detector = None
        if 'facebook_api' not in st.session_state:
            st.session_state.facebook_api = None
        if 'auto_monitor' not in st.session_state:
            st.session_state.auto_monitor = None
        if 'monitor_running' not in st.session_state:
            st.session_state.monitor_running = False
        if 'posts_cache' not in st.session_state:
            st.session_state.posts_cache = {}
        if 'comments_cache' not in st.session_state:
            st.session_state.comments_cache = {}
        if 'statistics' not in st.session_state:
            st.session_state.statistics = {
                'comments_processed': 0,
                'spam_removed': 0,
                'spam_detected': 0,
                'last_check': None,
                'start_time': None
            }
        # Initialize additional session state variables (consolidated)
        if 'monitor_logs' not in st.session_state:
            st.session_state.monitor_logs = []
        if 'auto_refresh_enabled' not in st.session_state:
            st.session_state.auto_refresh_enabled = True
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Dashboard"
        if 'previous_page' not in st.session_state:
            st.session_state.previous_page = "Dashboard"
        if 'auto_delete_enabled' not in st.session_state:
            st.session_state.auto_delete_enabled = os.getenv('AUTO_DELETE_SPAM', 'true').lower() == 'true'
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        if 'pending_spam' not in st.session_state:
            st.session_state.pending_spam = []
    
    def load_environment(self):
        """Load environment variables"""
        try:
            from dotenv import load_dotenv
            # Load .env from project root (two levels up from src/app/)
            env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
            load_dotenv(env_path)
        except ImportError:
            st.warning("python-dotenv not installed. Make sure environment variables are set.")

        self.page_id = os.getenv('PAGE_ID')
        self.page_access_token = os.getenv('PAGE_ACCESS_TOKEN')
        self.model_path = os.getenv('MODEL_PATH', './src/models')
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))
    
    def initialize_services(self):
        """Initialize spam detector and Facebook API"""
        try:
            # Initialize spam detector
            if st.session_state.spam_detector is None:
                with st.spinner("Loading spam detection model..."):
                    st.session_state.spam_detector = SpamDetector(self.model_path)

            # Initialize Facebook API
            if st.session_state.facebook_api is None and self.page_access_token:
                st.session_state.facebook_api = FacebookAPI(
                    self.page_id,
                    self.page_access_token
                )

        except Exception as e:
            NotificationManager.show_notification(f"Error initializing services: {str(e)}", "error", 8000)
    
    def initialize_page_renderers(self):
        """Initialize page renderer instances"""
        try:
            # Check if renderers already exist to avoid re-initialization
            if not hasattr(self, 'dashboard_renderer'):
                self.dashboard_renderer = DashboardRenderer(
                    st.session_state.facebook_api,
                    st.session_state.spam_detector,
                    self.confidence_threshold
                )

            if not hasattr(self, 'manual_check_page'):
                self.manual_check_page = ManualCheckPage(
                    st.session_state.facebook_api,
                    st.session_state.spam_detector,
                    self.confidence_threshold
                )

            if not hasattr(self, 'pending_spam_page'):
                self.pending_spam_page = PendingSpamPage(st.session_state.facebook_api)

            if not hasattr(self, 'test_detector_page'):
                self.test_detector_page = TestDetectorPage(
                    st.session_state.spam_detector,
                    self.confidence_threshold
                )

            if not hasattr(self, 'settings_page'):
                self.settings_page = SettingsPage(
                    self.page_id,
                    self.page_access_token,
                    self.model_path,
                    self.confidence_threshold
                )

            if not hasattr(self, 'logs_page'):
                self.logs_page = LogsPage()



        except Exception as e:
            st.error(f"❌ Error initializing page renderers: {str(e)}")
            st.exception(e)
    
    def render_sidebar(self):
        """Render sidebar with navigation and controls"""
        st.sidebar.markdown("## 🛡️ Judol Remover")
        st.sidebar.markdown("---")

        # Navigation with URL routing
        page_options = ["Dashboard", "Manual Check", "Pending Spam", "Test Detector", "Settings", "Logs"]
        page_urls = ["dashboard", "manual-check", "pending-spam", "test-detector", "settings", "logs"]

        # Get current page from URL params or session state
        query_params = st.query_params
        current_page_url = query_params.get("page", "dashboard")

        # Map URL to page name
        url_to_page = dict(zip(page_urls, page_options))
        page_to_url = dict(zip(page_options, page_urls))

        current_page = url_to_page.get(current_page_url, "Dashboard")

        try:
            current_index = page_options.index(current_page)
        except ValueError:
            current_index = 0  # Default to Dashboard if current_page is not in list

        selected_page = st.sidebar.selectbox(
            "Navigate to:",
            page_options,
            index=current_index,
            key=f"page_selector_{current_page.lower().replace(' ', '_')}"
        )

        # Update URL when page changes
        if selected_page != current_page:
            new_url = page_to_url[selected_page]
            st.query_params["page"] = new_url
            st.rerun()

        page = selected_page
        
        st.sidebar.markdown("---")
        
        # Monitor controls
        st.sidebar.markdown("### 🔄 Auto Monitor")

        # Auto Delete Toggle
        auto_delete = st.sidebar.checkbox(
            "🗑️ Auto Delete Spam",
            value=st.session_state.auto_delete_enabled,
            help="Otomatis hapus komentar yang terdeteksi spam",
            key=f"auto_delete_checkbox_{current_page.lower().replace(' ', '_')}"
        )

        if auto_delete != st.session_state.auto_delete_enabled:
            st.session_state.auto_delete_enabled = auto_delete

            # Update auto monitor configuration if it exists
            if 'auto_monitor' in st.session_state and st.session_state.auto_monitor is not None:
                st.session_state.auto_monitor.update_config(auto_delete_enabled=auto_delete)

            NotificationManager.show_notification(f"Auto delete {'enabled' if auto_delete else 'disabled'}", "success", 2000)

        # Auto Refresh Toggle
        auto_refresh = st.sidebar.checkbox(
            "🔄 Auto Refresh UI",
            value=st.session_state.get('auto_refresh_enabled', False),
            help="Otomatis refresh dashboard setiap 5 detik untuk update real-time",
            key=f"auto_refresh_checkbox_{current_page.lower().replace(' ', '_')}"
        )
        st.session_state.auto_refresh_enabled = auto_refresh

        if st.session_state.monitor_running:
            if st.sidebar.button("⏹️ Stop Monitor", type="secondary", key=f"stop_monitor_btn_{current_page.lower().replace(' ', '_')}"):
                self.stop_monitor()

            # Force sync statistics from auto monitor for real-time updates
            if 'auto_monitor' in st.session_state and st.session_state.auto_monitor is not None:
                try:
                    monitor_stats = st.session_state.auto_monitor.get_statistics()
                    if monitor_stats:
                        st.session_state.statistics.update(monitor_stats)
                except Exception:
                    pass

            # Show monitor status with more frequent runtime updates
            if st.session_state.statistics['start_time']:
                # Calculate runtime with precise seconds
                runtime = datetime.now() - st.session_state.statistics['start_time']
                total_seconds = int(runtime.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60

                if hours > 0:
                    runtime_str = f"{hours}h {minutes}m {seconds}s"
                else:
                    runtime_str = f"{minutes}m {seconds}s"

                # Add live indicator
                st.sidebar.metric("Runtime", f"🔴 {runtime_str}", help="Updates every second")

            # Real-time metrics with smooth transitions
            st.sidebar.metric("Comments Processed", st.session_state.statistics['comments_processed'])
            st.sidebar.metric("Spam Detected", st.session_state.statistics['spam_detected'])
            st.sidebar.metric("Spam Removed", st.session_state.statistics['spam_removed'])

            # Show last update time for transparency
            if st.session_state.statistics.get('last_check'):
                last_update = st.session_state.statistics['last_check']
                if isinstance(last_update, datetime):
                    time_diff = (datetime.now() - last_update).total_seconds()
                    if time_diff < 60:
                        st.sidebar.caption(f"🔄 Updated {int(time_diff)}s ago")
                    else:
                        st.sidebar.caption(f"🔄 Updated {int(time_diff//60)}m ago")
        else:
            if st.sidebar.button("▶️ Start Monitor", type="primary", key=f"start_monitor_btn_{current_page.lower().replace(' ', '_')}"):
                self.start_monitor()
        
        st.sidebar.markdown("---")
        
        # System status
        st.sidebar.markdown("### 📊 System Status")

        # Model status
        model_status = "🟢 Ready" if st.session_state.spam_detector else "🔴 Not Loaded"
        st.sidebar.markdown(f"**Model:** {model_status}")

        # Facebook API status
        fb_status = "🟢 Connected" if st.session_state.facebook_api else "🔴 Not Connected"
        st.sidebar.markdown(f"**Facebook:** {fb_status}")

        # Auto Monitor status
        if 'auto_monitor' in st.session_state and st.session_state.auto_monitor is not None:
            monitor_status = "🟢 Initialized"
        else:
            monitor_status = "🔴 Not Initialized"
        st.sidebar.markdown(f"**Auto Monitor:** {monitor_status}")

        return page

    def start_monitor(self):
        """Start the auto monitor"""
        try:
            if not st.session_state.facebook_api:
                NotificationManager.show_notification("Facebook API not connected", "error", 5000)
                return

            if not st.session_state.spam_detector:
                NotificationManager.show_notification("Spam detector not loaded", "error", 5000)
                return

            # Initialize auto monitor
            st.session_state.auto_monitor = AutoMonitor(
                st.session_state.facebook_api,
                st.session_state.spam_detector,
                poll_interval=30
            )

            # Configure auto monitor settings
            st.session_state.auto_monitor.confidence_threshold = self.confidence_threshold
            st.session_state.auto_monitor.auto_delete_enabled = st.session_state.auto_delete_enabled

            # Start monitoring
            st.session_state.auto_monitor.start()
            st.session_state.monitor_running = True
            st.session_state.statistics['start_time'] = datetime.now()

            NotificationManager.show_notification("Auto monitor started!", "success", 3000)

            # Force UI update to show Stop Monitor button immediately
            st.rerun()

        except Exception as e:
            NotificationManager.show_notification(f"Failed to start monitor: {str(e)}", "error", 6000)

    def stop_monitor(self):
        """Stop the auto monitor"""
        try:
            if 'auto_monitor' in st.session_state and st.session_state.auto_monitor is not None:
                st.session_state.auto_monitor.stop()

            st.session_state.monitor_running = False
            st.session_state.statistics['start_time'] = None

            NotificationManager.show_notification("Auto monitor stopped!", "info", 3000)

            # Force UI update to show Start Monitor button immediately
            st.rerun()

        except Exception as e:
            NotificationManager.show_notification(f"Error stopping monitor: {str(e)}", "error", 5000)

    @st.fragment(run_every=1)
    def _auto_refresh_fragment(self):
        """Fragment that runs every 1 second to handle auto-refresh"""
        current_page = st.session_state.get('current_page', 'Dashboard')
        allowed_pages = ["Dashboard", "Logs"]

        if (st.session_state.get('monitor_running', False) and
            st.session_state.get('auto_refresh_enabled', False) and
            current_page in allowed_pages):

            # Initialize refresh timing if not exists
            if 'last_refresh_time' not in st.session_state:
                st.session_state.last_refresh_time = datetime.now()

            if 'refresh_counter' not in st.session_state:
                st.session_state.refresh_counter = 0

            # Calculate time since last refresh
            current_time = datetime.now()
            time_since_refresh = (current_time - st.session_state.last_refresh_time).total_seconds()

            # Show refresh status with countdown
            if time_since_refresh >= 5.0:
                # Time to refresh
                st.session_state.last_refresh_time = current_time
                st.session_state.refresh_counter += 1

                # Update real-time data
                self._update_realtime_data()

                st.success(f"🔄 Auto-refreshed #{st.session_state.refresh_counter} - {current_page} page updated at {current_time.strftime('%H:%M:%S')}")

                # Trigger full page refresh
                st.rerun()
            else:
                # Show countdown
                remaining_time = 5.0 - time_since_refresh
                st.info(f"🔄 Auto refresh enabled - Next refresh in {remaining_time:.1f} seconds (#{st.session_state.refresh_counter})")

    def handle_auto_refresh(self):
        """Handle auto refresh functionality - ONLY for specific pages to prevent bleeding"""
        # Only auto-refresh on Dashboard and Logs pages to prevent bleeding
        allowed_pages = ["Dashboard", "Logs"]
        current_page = st.session_state.get('current_page', 'Dashboard')

        if (st.session_state.get('monitor_running', False) and
            st.session_state.get('auto_refresh_enabled', False) and
            current_page in allowed_pages):

            # Use the fragment for auto-refresh
            self._auto_refresh_fragment()

    def _update_realtime_data(self):
        """Update real-time data from auto monitor"""
        try:
            # Force sync statistics from auto monitor for real-time updates
            if 'auto_monitor' in st.session_state and st.session_state.auto_monitor is not None:
                try:
                    monitor_stats = st.session_state.auto_monitor.get_statistics()
                    if monitor_stats:
                        st.session_state.statistics.update(monitor_stats)
                        st.session_state.statistics['last_update'] = datetime.now()
                except Exception as e:
                    # Log error but don't break the refresh
                    pass

            # Update last refresh timestamp
            st.session_state.statistics['last_refresh'] = datetime.now()

        except Exception as e:
            # Don't let data update errors break the refresh
            pass

    def cleanup_page_state(self, previous_page: str):
        """Clean up page-specific state when switching pages to prevent bleeding"""
        try:
            # Clean up auto-refresh states
            refresh_keys_to_remove = []
            for key in list(st.session_state.keys()):
                if key.startswith('auto_refresh_'):
                    refresh_keys_to_remove.append(key)

            for key in refresh_keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]

            # Clean up page-specific component states
            page_key = previous_page.lower().replace(' ', '_')
            page_specific_keys = [
                f"{page_key}_container",
                f"{page_key}_placeholder",
                f"{page_key}_state",
                f"{page_key}_main_container_state",
            ]

            for key in page_specific_keys:
                if key in st.session_state:
                    del st.session_state[key]

            # Clean up component keys that might be page-specific
            component_keys_to_remove = []
            for key in list(st.session_state.keys()):
                # Remove keys that contain the previous page name
                if page_key in key and any(suffix in key for suffix in ['_btn', '_checkbox', '_selector']):
                    component_keys_to_remove.append(key)

            for key in component_keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]

            # Clear notification container to prevent bleeding
            if 'notification_container' in st.session_state:
                try:
                    st.session_state.notification_container.empty()
                    del st.session_state.notification_container
                except Exception:
                    pass

            # Clear page-specific notifications
            from src.app.ui_components import NotificationManager
            NotificationManager.clear_page_notifications(previous_page)

        except Exception as e:
            # Don't let cleanup errors break the app
            pass

    def run(self):
        """Main application entry point"""
        # Set page config first (only once)
        try:
            st.set_page_config(
                page_title="Judol Remover",
                page_icon="🛡️",
                layout="wide",
                initial_sidebar_state="expanded"
            )
        except st.errors.StreamlitAPIException:
            # Page config already set, ignore
            pass

        # Load custom CSS
        load_custom_css()

        # Render sidebar and get current page
        current_page = self.render_sidebar()

        # Update current page in session state - clean state management
        if st.session_state.get('current_page') != current_page:
            previous_page = st.session_state.get('current_page', 'Dashboard')
            st.session_state.previous_page = previous_page
            st.session_state.current_page = current_page

            # Clean up page-specific state to prevent bleeding
            self.cleanup_page_state(previous_page)



        # Display notifications
        NotificationManager.display_notifications()

        # Route to appropriate page
        try:


            if current_page == "Dashboard":
                # Initialize dashboard renderer if needed
                if not hasattr(self, 'dashboard_renderer'):
                    self.dashboard_renderer = DashboardRenderer(
                        st.session_state.facebook_api,
                        st.session_state.spam_detector,
                        self.confidence_threshold
                    )
                self.dashboard_renderer.render_dashboard()

            elif current_page == "Manual Check":
                # Initialize manual check page if needed
                if not hasattr(self, 'manual_check_page'):
                    self.manual_check_page = ManualCheckPage(
                        st.session_state.facebook_api,
                        st.session_state.spam_detector,
                        self.confidence_threshold
                    )
                self.manual_check_page.render()

            elif current_page == "Pending Spam":
                # Initialize pending spam page if needed
                if not hasattr(self, 'pending_spam_page'):
                    self.pending_spam_page = PendingSpamPage(st.session_state.facebook_api)
                self.pending_spam_page.render()

            elif current_page == "Test Detector":
                # Initialize test detector page if needed
                if not hasattr(self, 'test_detector_page'):
                    self.test_detector_page = TestDetectorPage(
                        st.session_state.spam_detector,
                        self.confidence_threshold
                    )
                self.test_detector_page.render()

            elif current_page == "Settings":
                # Initialize settings page if needed
                if not hasattr(self, 'settings_page'):
                    self.settings_page = SettingsPage(
                        self.page_id,
                        self.page_access_token,
                        self.model_path,
                        self.confidence_threshold
                    )
                self.settings_page.render()

            elif current_page == "Logs":
                # Initialize logs page if needed
                if not hasattr(self, 'logs_page'):
                    self.logs_page = LogsPage()
                self.logs_page.render()

            else:
                st.error(f"❌ Unknown page: {current_page}")

        except Exception as e:
            st.error(f"❌ Error rendering {current_page} page: {str(e)}")
            st.exception(e)

        # Handle auto refresh using the centralized method
        self.handle_auto_refresh()


def main():
    """Application entry point"""
    app = StreamlitJudolRemover()
    app.run()


if __name__ == "__main__":
    main()
