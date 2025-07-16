#!/usr/bin/env python3
"""
Test script to verify page navigation fixes
This script tests that components don't persist between pages
"""

import streamlit as st

def test_page_isolation():
    """Test that page components are properly isolated"""
    
    st.title("🧪 Page Navigation Test")
    
    # Navigation
    page = st.selectbox("Select Page:", ["Dashboard Test", "Logs Test", "Settings Test"])
    
    st.markdown("---")
    
    # Track page changes
    if 'test_previous_page' not in st.session_state:
        st.session_state.test_previous_page = None
    
    if st.session_state.test_previous_page != page:
        st.success(f"✅ Page changed from {st.session_state.test_previous_page} to {page}")
        st.session_state.test_previous_page = page
    
    # Render different content based on page
    if page == "Dashboard Test":
        render_dashboard_test()
    elif page == "Logs Test":
        render_logs_test()
    elif page == "Settings Test":
        render_settings_test()

def render_dashboard_test():
    """Test dashboard components"""
    st.markdown("### 📊 Dashboard Test")

    # Container for dashboard
    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Test Metric 1", "100")
        with col2:
            st.metric("Test Metric 2", "200")
        with col3:
            st.metric("Test Metric 3", "300")

        st.info("This is dashboard content - should NOT appear on other pages")

def render_logs_test():
    """Test logs components"""
    st.markdown("### 📋 Logs Test")

    # Container for logs
    with st.container():
        st.success("🔄 Auto Refresh ON")

        # Test logs table
        import pandas as pd
        test_logs = [
            {"Time": "10:00:00", "Action": "TEST", "Message": "Test log 1"},
            {"Time": "10:01:00", "Action": "TEST", "Message": "Test log 2"},
            {"Time": "10:02:00", "Action": "TEST", "Message": "Test log 3"},
        ]

        df = pd.DataFrame(test_logs)
        st.dataframe(df, use_container_width=True)

        st.warning("This is logs content - should NOT appear on other pages")

def render_settings_test():
    """Test settings components"""
    st.markdown("### ⚙️ Settings Test")

    # Container for settings
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Test Setting 1", value="test1")
        with col2:
            st.text_input("Test Setting 2", value="test2")

        st.error("This is settings content - should NOT appear on other pages")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Page Navigation Test",
        page_icon="🧪",
        layout="wide"
    )
    
    test_page_isolation()
