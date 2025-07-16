#!/usr/bin/env python3
"""
Logs Page Module
Handles activity logs display and management
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
from typing import List, Dict
from src.app.ui_components import NotificationManager


class LogsPage:
    """Handles logs page rendering and functionality"""
    
    def __init__(self):
        pass
    
    def render(self):
        """Render logs page with real-time updates - LOGS PAGE ONLY"""
        # CRITICAL: This method should ONLY be called when current_page == "Logs"
        # If this appears in Dashboard, there's a routing bug

        # Use isolated container with unique key to prevent bleeding to other pages
        logs_key = "logs_main_container"

        # Clear any existing logs page state to prevent bleeding
        if f"{logs_key}_state" in st.session_state:
            del st.session_state[f"{logs_key}_state"]

        logs_container = st.container(key=logs_key)
        with logs_container:
            try:
                # Real-time header with auto-refresh indicator
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown("### 📋 Activity Logs")

                with col2:
                    # Show auto-refresh status (controlled from sidebar)
                    if (st.session_state.get('monitor_running', False) and
                        st.session_state.get('auto_refresh_enabled', True)):
                        st.success("🔄 Auto Refresh ON")
                    elif st.session_state.get('monitor_running', False):
                        st.warning("⏸️ Auto Refresh OFF")
                    else:
                        st.info("⏹️ Monitor Stopped")

                # Initialize session state variables
                self._initialize_session_state()

                # Show auto-refresh instructions
                if not st.session_state.get('monitor_running', False):
                    st.info("ℹ️ Start the monitor from the sidebar to see real-time logs")
                elif not st.session_state.get('auto_refresh_enabled', True):
                    st.warning("⚠️ Auto-refresh is disabled. Enable 'Auto Refresh UI' in the sidebar for real-time updates")
                else:
                    refresh_count = st.session_state.get('refresh_counter', 0)
                    st.success(f"✅ Real-time logs enabled - Updates every 5 seconds automatically (#{refresh_count})")

                # Force sync logs from auto monitor on every page load
                self._sync_logs_from_monitor()

                # Real-time metrics
                self._render_metrics()

                # Real-time log controls
                self._render_log_controls()

                # Display logs
                self._render_logs_display()

            except Exception as e:
                st.error(f"❌ Error rendering logs page: {str(e)}")
                st.exception(e)
                # Show fallback content
                self._render_fallback_content()

    def _initialize_session_state(self):
        """Initialize all required session state variables"""
        # Initialize logs if not exists
        if 'monitor_logs' not in st.session_state:
            st.session_state.monitor_logs = []

        # Initialize auto refresh enabled if not exists
        if 'auto_refresh_enabled' not in st.session_state:
            st.session_state.auto_refresh_enabled = True

        # Initialize monitor running if not exists
        if 'monitor_running' not in st.session_state:
            st.session_state.monitor_running = False

    def _sync_logs_from_monitor(self):
        """Sync logs from auto monitor with error handling"""
        if ('auto_monitor' in st.session_state and
            st.session_state.auto_monitor is not None and
            st.session_state.get('monitor_running', False)):
            try:
                if hasattr(st.session_state.auto_monitor, 'sync_logs_to_session_state'):
                    synced_count = st.session_state.auto_monitor.sync_logs_to_session_state()
                    # Show sync status in real-time
                    if synced_count > 0:
                        st.caption(f"🔄 Last sync: {datetime.now().strftime('%H:%M:%S')} - {synced_count} logs")
                else:
                    # Fallback method
                    if hasattr(st.session_state.auto_monitor, 'get_recent_activity'):
                        recent_logs = st.session_state.auto_monitor.get_recent_activity(100)
                        if recent_logs:
                            st.session_state.monitor_logs = recent_logs
                            st.caption(f"🔄 Fallback sync: {len(recent_logs)} logs loaded")
            except Exception as e:
                st.warning(f"⚠️ Log sync error: {str(e)}")

    def _render_fallback_content(self):
        """Render fallback content when main rendering fails"""
        st.markdown("### 📋 Activity Logs (Fallback Mode)")
        st.info("📭 Logs page is in fallback mode due to an error.")

        # Show basic log count
        log_count = len(st.session_state.get('monitor_logs', []))
        st.metric("Total Logs", log_count)

        # Show simple log list if available
        if log_count > 0:
            st.markdown("#### Recent Logs")
            for i, log in enumerate(st.session_state.monitor_logs[-10:]):
                st.text(f"{i+1}. {log.get('timestamp', 'N/A')} - {log.get('action', 'N/A')} - {log.get('author', 'N/A')}")
        else:
            st.info("No logs available")

    def _add_sample_logs(self):
        """Add sample logs for testing"""
        sample_logs = [
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': 'NEW_COMMENT',
                'comment_id': 'sample_001',
                'author': 'John Doe',
                'message': 'This is a normal comment',
                'post_id': 'post_123',
                'reason': 'New comment detected'
            },
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': 'SPAM_DETECTED',
                'comment_id': 'sample_002',
                'author': 'Spammer',
                'message': 'Buy cheap products now!!!',
                'post_id': 'post_123',
                'reason': 'Spam keywords detected'
            },
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': 'DELETED',
                'comment_id': 'sample_003',
                'author': 'BadUser',
                'message': 'Inappropriate content',
                'post_id': 'post_456',
                'reason': 'Auto-deleted spam'
            },
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': 'PENDING_SPAM',
                'comment_id': 'sample_004',
                'author': 'SuspiciousUser',
                'message': 'Suspicious comment content',
                'post_id': 'post_789',
                'reason': 'Requires manual review'
            }
        ]

        # Add sample logs to session state
        for log in sample_logs:
            st.session_state.monitor_logs.append(log)

        # Keep only last 100 entries
        if len(st.session_state.monitor_logs) > 100:
            st.session_state.monitor_logs = st.session_state.monitor_logs[-100:]

    def _render_metrics(self):
        """Render real-time metrics"""
        st.markdown("#### 📊 Real-time Metrics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_logs = len(st.session_state.monitor_logs)
            st.metric("Total Logs", total_logs)

        with col2:
            monitor_status = "🟢 Running" if st.session_state.monitor_running else "🔴 Stopped"
            st.metric("Monitor Status", monitor_status)

        with col3:
            if 'auto_monitor' in st.session_state and st.session_state.auto_monitor is not None:
                processed_count = len(st.session_state.auto_monitor.processed_comments)
                internal_logs_count = len(st.session_state.auto_monitor.internal_logs)
                st.metric("Processed Comments", processed_count)
            else:
                internal_logs_count = 0
                st.metric("Processed Comments", "N/A")

        with col4:
            # Show sync status
            if internal_logs_count > 0:
                sync_status = "🟢 Synced" if internal_logs_count == total_logs else "🟡 Pending"
                st.metric("Sync Status", sync_status)
            else:
                st.metric("Sync Status", "N/A")

        # Show latest activity timestamp
        if st.session_state.monitor_logs:
            latest_log = st.session_state.monitor_logs[-1]
            latest_time = latest_log.get('timestamp', 'Unknown')
            st.info(f"🕒 Latest Activity: {latest_time}")
        else:
            st.info("🕒 No activity recorded yet")

    def _render_log_controls(self):
        """Render log control buttons"""
        st.markdown("#### 🎛️ Log Controls")
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            if st.button("🔄 Manual Refresh", key="logs_manual_refresh_btn"):
                # Force sync from auto monitor
                if ('auto_monitor' in st.session_state and
                    st.session_state.auto_monitor is not None):
                    try:
                        if hasattr(st.session_state.auto_monitor, 'sync_logs_to_session_state'):
                            synced_count = st.session_state.auto_monitor.sync_logs_to_session_state()
                            NotificationManager.show_notification(f"Refreshed! Synced {synced_count} logs", "success", 2000)
                    except Exception as e:
                        NotificationManager.show_notification(f"Error: {str(e)}", "error", 3000)
                st.rerun()

        with col2:
            if st.button("🗑️ Clear Logs", key="logs_clear_logs_btn"):
                st.session_state.monitor_logs = []
                # Also clear internal logs if available
                if ('auto_monitor' in st.session_state and
                    st.session_state.auto_monitor is not None):
                    try:
                        st.session_state.auto_monitor.internal_logs = []
                    except Exception:
                        pass
                NotificationManager.show_notification("All logs cleared!", "info", 2000)
                st.rerun()

        with col3:
            if st.button("🔄 Force Sync", key="logs_force_sync_btn"):
                if ('auto_monitor' in st.session_state and
                    st.session_state.auto_monitor is not None):
                    try:
                        if hasattr(st.session_state.auto_monitor, 'sync_logs_to_session_state'):
                            synced_count = st.session_state.auto_monitor.sync_logs_to_session_state()
                            NotificationManager.show_notification(f"Force synced {synced_count} logs", "success", 2000)
                        else:
                            NotificationManager.show_notification("Sync method not available", "warning", 2000)
                    except Exception as e:
                        NotificationManager.show_notification(f"Sync error: {str(e)}", "error", 3000)
                else:
                    NotificationManager.show_notification("Auto monitor not available", "warning", 2000)
                st.rerun()

        with col4:
            if st.button("🧪 Add Test Log", key="logs_add_test_log_btn"):
                test_log = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'action': 'TEST',
                    'comment_id': f'test_{int(time.time())}',
                    'author': 'Test User',
                    'message': f'Test log entry at {datetime.now().strftime("%H:%M:%S")}',
                    'post_id': 'test_post',
                    'reason': 'Manual test'
                }
                st.session_state.monitor_logs.append(test_log)
                NotificationManager.show_notification("Test log added!", "success", 2000)
                st.rerun()

    def _render_logs_display(self):
        """Render the main logs display"""
        logs = st.session_state.monitor_logs

        # Force refresh logs from auto monitor
        if st.button("🔄 Force Sync Logs from Monitor"):
            if 'auto_monitor' in st.session_state and st.session_state.auto_monitor is not None:
                try:
                    # Check if method exists (for backward compatibility)
                    if hasattr(st.session_state.auto_monitor, 'sync_logs_to_session_state'):
                        total_logs = st.session_state.auto_monitor.sync_logs_to_session_state()
                        st.success(f"Synced logs from auto monitor. Total logs: {total_logs}")
                    else:
                        # Fallback: get recent activity and replace session logs
                        recent_activity = st.session_state.auto_monitor.get_recent_activity(50)
                        if recent_activity:
                            st.session_state.monitor_logs = recent_activity
                            st.success(f"Synced {len(recent_activity)} logs from auto monitor (fallback method)")
                        else:
                            st.warning("No logs found in auto monitor")
                except Exception as e:
                    st.error(f"Error syncing logs: {e}")
                    # Show restart option
                    if st.button("🔄 Reset Auto Monitor"):
                        st.session_state.auto_monitor = None
                        st.success("Auto monitor reset. Please restart it from the sidebar.")
                        st.rerun()
            else:
                st.warning("Auto monitor not available")
            st.rerun()

        if not logs:
            st.info("📭 No activity logs yet. Start the auto monitor to see activity.")

            # Troubleshooting tips
            st.markdown("**Troubleshooting:**")
            st.write("1. Check if auto monitor is running")
            st.write("2. Try 'Force Sync Logs from Monitor' button above")
            st.write("3. Use 'Add Test Log' button below to add sample data")

            # Add test log buttons for empty state
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("🧪 Add Test Log", key="empty_state_test_log"):
                    test_log = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'action': 'TEST',
                        'comment_id': f'test_{int(time.time())}',
                        'author': 'Test User',
                        'message': f'Test log entry at {datetime.now().strftime("%H:%M:%S")}',
                        'post_id': 'test_post',
                        'reason': 'Manual test'
                    }
                    st.session_state.monitor_logs.append(test_log)
                    NotificationManager.show_notification("Test log added!", "success", 2000)
                    st.rerun()

            with col2:
                if st.button("📊 Add Sample Logs", key="add_sample_logs"):
                    self._add_sample_logs()
                    NotificationManager.show_notification("Sample logs added!", "success", 2000)
                    st.rerun()
            return

        st.markdown(f"#### Recent Activity ({len(logs)} entries)")

        # Filter options
        col1, col2 = st.columns(2)

        with col1:
            log_filter = st.selectbox(
                "Filter by action:",
                ["All", "NEW_COMMENT", "SPAM_DETECTED", "PENDING_SPAM", "DELETED", "TEST", "ERROR", "INFO"]
            )

        with col2:
            show_count = st.number_input(
                "Show last N entries:",
                min_value=10,
                max_value=100,
                value=50,
                step=10
            )

        # Debug info with expandable details
        with st.expander("🔍 Debug Information", expanded=False):
            st.write(f"**Total logs:** {len(logs)}")
            st.write(f"**Filter:** {log_filter}")
            st.write(f"**Monitor running:** {st.session_state.get('monitor_running', False)}")
            st.write(f"**Auto monitor available:** {'auto_monitor' in st.session_state and st.session_state.auto_monitor is not None}")

            if logs:
                st.write(f"**Sample log actions:** {[log.get('action', 'NO_ACTION') for log in logs[:3]]}")
                st.write("**First log structure:**")
                st.json(logs[0] if logs else {})
            else:
                st.write("**No logs available for debugging**")

        # Filter and display logs
        filtered_logs = logs
        if log_filter != "All":
            filtered_logs = [log for log in logs if log.get('action') == log_filter]

        # Show most recent entries
        recent_logs = filtered_logs[-show_count:]
        recent_logs.reverse()  # Show newest first

        # Display logs directly in table format
        st.markdown("---")

        if recent_logs:
            # Show table directly without tabs
            self._render_table_view(recent_logs)
        else:
            st.info(f"📭 No logs found for filter: {log_filter}")
            # Show empty table structure
            import pandas as pd
            empty_df = pd.DataFrame({
                'Time': [],
                'Action': [],
                'Author': [],
                'Message': [],
                'Reason': []
            })
            st.dataframe(empty_df, use_container_width=True, height=200)



    def _render_table_view(self, recent_logs: List[Dict]):
        """Render logs in table format with error handling"""
        try:
            # Table format for quick overview
            log_data = []

            # Handle empty logs case
            if not recent_logs:
                st.info("📊 No logs to display in table format")
                # Show empty table structure
                empty_df = pd.DataFrame({
                    'Time': [],
                    'Action': [],
                    'Author': [],
                    'Message': [],
                    'Reason': []
                })
                st.dataframe(empty_df, use_container_width=True, height=200)
                return

            # Process logs with error handling
            for i, log in enumerate(recent_logs):
                try:
                    # Validate log structure
                    if not isinstance(log, dict):
                        st.warning(f"⚠️ Invalid log entry at index {i}: {type(log)}")
                        continue

                    # Add emoji based on action
                    action = log.get('action', 'UNKNOWN')
                    if action == 'NEW_COMMENT':
                        action_display = "💬 NEW_COMMENT"
                    elif action == 'SPAM_DETECTED':
                        action_display = "🚨 SPAM_DETECTED"
                    elif action == 'DELETED':
                        action_display = "🗑️ DELETED"
                    elif action == 'PENDING_SPAM':
                        action_display = "⏳ PENDING_SPAM"
                    elif action == 'TEST':
                        action_display = "🧪 TEST"
                    else:
                        action_display = f"ℹ️ {action}"

                    # Safe string processing
                    timestamp = log.get('timestamp', '')
                    time_display = timestamp[-8:] if timestamp and len(timestamp) >= 8 else timestamp

                    author = str(log.get('author', ''))
                    author_display = author[:20] + "..." if len(author) > 20 else author

                    message = str(log.get('message', ''))
                    message_display = message[:40] + "..." if len(message) > 40 else message

                    reason = str(log.get('reason', ''))
                    reason_display = reason[:30] + "..." if len(reason) > 30 else reason

                    log_data.append({
                        'Time': time_display,
                        'Action': action_display,
                        'Author': author_display,
                        'Message': message_display,
                        'Reason': reason_display
                    })

                except Exception as e:
                    st.warning(f"⚠️ Error processing log entry {i}: {str(e)}")
                    continue

            # Create and display dataframe
            if log_data:
                df = pd.DataFrame(log_data)
                st.dataframe(df, use_container_width=True, height=400)
            else:
                st.info("📭 No valid log entries to display")
                # Show empty table structure
                empty_df = pd.DataFrame({
                    'Time': [],
                    'Action': [],
                    'Author': [],
                    'Message': [],
                    'Reason': []
                })
                st.dataframe(empty_df, use_container_width=True, height=200)

        except Exception as e:
            st.error(f"❌ Error rendering table view: {str(e)}")
            st.exception(e)
            # Fallback: show simple text list
            st.markdown("#### Fallback: Simple Log List")
            for i, log in enumerate(recent_logs[:10]):
                st.text(f"{i+1}. {log}")


