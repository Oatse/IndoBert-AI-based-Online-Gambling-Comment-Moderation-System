#!/usr/bin/env python3
"""
Test Auto-Refresh Functionality
Tests the 5-second auto-refresh mechanism to ensure it works properly
"""

import streamlit as st
import time
from datetime import datetime

def main():
    """Test auto-refresh functionality"""
    st.set_page_config(
        page_title="Auto-Refresh Test",
        page_icon="🔄",
        layout="wide"
    )
    
    st.title("🔄 Auto-Refresh Test")
    st.markdown("---")
    
    # Initialize session state
    if 'test_refresh_enabled' not in st.session_state:
        st.session_state.test_refresh_enabled = False
    if 'test_last_refresh' not in st.session_state:
        st.session_state.test_last_refresh = datetime.now()
    if 'test_refresh_counter' not in st.session_state:
        st.session_state.test_refresh_counter = 0
    if 'test_data' not in st.session_state:
        st.session_state.test_data = {
            'random_number': 0,
            'timestamp': datetime.now(),
            'updates': []
        }
    
    # Control panel
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🟢 Start Auto-Refresh"):
            st.session_state.test_refresh_enabled = True
            st.session_state.test_last_refresh = datetime.now()
            st.success("Auto-refresh started!")
    
    with col2:
        if st.button("🔴 Stop Auto-Refresh"):
            st.session_state.test_refresh_enabled = False
            st.warning("Auto-refresh stopped!")
    
    with col3:
        if st.button("🔄 Reset Data"):
            st.session_state.test_refresh_counter = 0
            st.session_state.test_data = {
                'random_number': 0,
                'timestamp': datetime.now(),
                'updates': []
            }
            st.info("Data reset!")
    
    st.markdown("---")
    
    # Status display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = "🟢 ACTIVE" if st.session_state.test_refresh_enabled else "🔴 STOPPED"
        st.metric("Auto-Refresh Status", status)
    
    with col2:
        st.metric("Refresh Counter", st.session_state.test_refresh_counter)
    
    with col3:
        current_time = datetime.now()
        time_since_refresh = (current_time - st.session_state.test_last_refresh).total_seconds()
        st.metric("Time Since Last Refresh", f"{time_since_refresh:.1f}s")
    
    # Auto-refresh logic using fragment
    if st.session_state.test_refresh_enabled:
        auto_refresh_fragment()
    
    # Display test data
    st.markdown("### 📊 Test Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Random Number", st.session_state.test_data['random_number'])
        st.metric("Last Update", st.session_state.test_data['timestamp'].strftime('%H:%M:%S'))
    
    with col2:
        st.markdown("**Recent Updates:**")
        if st.session_state.test_data['updates']:
            for update in st.session_state.test_data['updates'][-5:]:  # Show last 5 updates
                st.text(f"• {update}")
        else:
            st.text("No updates yet")
    
    # Instructions
    st.markdown("---")
    st.markdown("### 📝 How to Test")
    st.markdown("""
    1. Click **Start Auto-Refresh** to begin the 5-second refresh cycle
    2. Watch the metrics and data update automatically every 5 seconds
    3. The refresh counter should increment with each refresh
    4. The random number and timestamp should change every 5 seconds
    5. Click **Stop Auto-Refresh** to halt the automatic updates
    6. Click **Reset Data** to clear all counters and data
    
    **Expected Behavior:**
    - Auto-refresh should trigger every 5 seconds when enabled
    - UI should show countdown to next refresh
    - Data should update automatically without manual intervention
    - Stopping should immediately halt the refresh cycle
    """)

@st.fragment(run_every=1)
def auto_refresh_fragment():
    """Fragment that runs every 1 second to handle auto-refresh"""
    if not st.session_state.test_refresh_enabled:
        return
    
    current_time = datetime.now()
    time_since_refresh = (current_time - st.session_state.test_last_refresh).total_seconds()
    
    if time_since_refresh >= 5.0:
        # Time to refresh
        st.session_state.test_last_refresh = current_time
        st.session_state.test_refresh_counter += 1
        
        # Update test data
        import random
        st.session_state.test_data['random_number'] = random.randint(1, 1000)
        st.session_state.test_data['timestamp'] = current_time
        st.session_state.test_data['updates'].append(
            f"Update #{st.session_state.test_refresh_counter} at {current_time.strftime('%H:%M:%S')}"
        )
        
        # Keep only last 10 updates
        if len(st.session_state.test_data['updates']) > 10:
            st.session_state.test_data['updates'] = st.session_state.test_data['updates'][-10:]
        
        st.success(f"🔄 Auto-refreshed #{st.session_state.test_refresh_counter} at {current_time.strftime('%H:%M:%S')}")
        st.rerun()
    else:
        # Show countdown
        remaining_time = 5.0 - time_since_refresh
        st.info(f"🔄 Next refresh in {remaining_time:.1f} seconds (#{st.session_state.test_refresh_counter})")

if __name__ == "__main__":
    main()
