#!/usr/bin/env python3
"""
Test script for infinite loop real-time updates
Demonstrates the new infinite loop implementation for real-time UI updates
"""

import streamlit as st
import time
from datetime import datetime
import random

def main():
    """Test infinite loop implementation"""
    st.set_page_config(
        page_title="Infinite Loop Test",
        page_icon="🔄",
        layout="wide"
    )
    
    st.title("🔄 Infinite Loop Real-time Updates Test")
    st.markdown("---")
    
    # Initialize session state
    if 'test_running' not in st.session_state:
        st.session_state.test_running = False
    if 'update_counter' not in st.session_state:
        st.session_state.update_counter = 0
    if 'test_data' not in st.session_state:
        st.session_state.test_data = {
            'memory_usage': 0,
            'cpu_usage': 0,
            'network_requests': 0,
            'active_users': 0
        }
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    
    # Control buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Start Real-time Updates"):
            st.session_state.test_running = True
            st.session_state.update_counter = 0
            st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Updates"):
            st.session_state.test_running = False
            st.rerun()
    
    with col3:
        if st.button("🔄 Reset Data"):
            st.session_state.update_counter = 0
            st.session_state.test_data = {
                'memory_usage': 0,
                'cpu_usage': 0,
                'network_requests': 0,
                'active_users': 0
            }
            st.session_state.last_update = None
            st.rerun()
    
    # Status indicator
    if st.session_state.test_running:
        st.success(f"🟢 Real-time updates ACTIVE - Update #{st.session_state.update_counter}")
    else:
        st.error("🔴 Real-time updates STOPPED")
    
    # Display metrics
    st.markdown("### 📊 Live Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Memory Usage",
            f"{st.session_state.test_data['memory_usage']:.1f} MB",
            delta=f"{random.uniform(-5, 5):.1f} MB" if st.session_state.update_counter > 0 else None
        )
    
    with col2:
        st.metric(
            "CPU Usage",
            f"{st.session_state.test_data['cpu_usage']:.1f}%",
            delta=f"{random.uniform(-10, 10):.1f}%" if st.session_state.update_counter > 0 else None
        )
    
    with col3:
        st.metric(
            "Network Requests",
            st.session_state.test_data['network_requests'],
            delta=random.randint(-5, 15) if st.session_state.update_counter > 0 else None
        )
    
    with col4:
        st.metric(
            "Active Users",
            st.session_state.test_data['active_users'],
            delta=random.randint(-2, 8) if st.session_state.update_counter > 0 else None
        )
    
    # Last update timestamp
    if st.session_state.last_update:
        st.caption(f"🕒 Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")
    else:
        st.caption("🕒 No updates yet")
    
    # Real-time chart placeholder
    chart_placeholder = st.empty()
    
    # Infinite loop for real-time updates
    if st.session_state.test_running:
        # Create placeholder for status updates
        status_placeholder = st.empty()
        
        # Start infinite loop
        while st.session_state.test_running:
            # Update counter
            st.session_state.update_counter += 1
            
            # Update test data with random values
            st.session_state.test_data['memory_usage'] = max(0, min(100, 
                st.session_state.test_data['memory_usage'] + random.uniform(-5, 5)))
            st.session_state.test_data['cpu_usage'] = max(0, min(100,
                st.session_state.test_data['cpu_usage'] + random.uniform(-10, 10)))
            st.session_state.test_data['network_requests'] += random.randint(0, 10)
            st.session_state.test_data['active_users'] = max(0,
                st.session_state.test_data['active_users'] + random.randint(-2, 5))
            
            # Update timestamp
            st.session_state.last_update = datetime.now()
            
            # Show status in placeholder
            with status_placeholder.container():
                st.info(f"🔄 Real-time update #{st.session_state.update_counter} - Next update in 1 second...")
            
            # Wait 1 second
            time.sleep(1)
            
            # Trigger UI refresh
            st.rerun()
    
    # Instructions
    st.markdown("---")
    st.markdown("### 📝 Instructions")
    st.markdown("""
    1. Click **Start Real-time Updates** to begin the infinite loop
    2. Watch the metrics update every second automatically
    3. The update counter shows how many updates have occurred
    4. Click **Stop Updates** to halt the infinite loop
    5. Click **Reset Data** to clear all metrics and counters
    
    **Note**: This demonstrates the infinite loop pattern with `time.sleep(1)` for real-time updates.
    """)

if __name__ == "__main__":
    main()
