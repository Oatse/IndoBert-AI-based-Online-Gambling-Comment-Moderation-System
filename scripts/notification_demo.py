#!/usr/bin/env python3
"""
Demo untuk menguji sistem notifikasi custom
"""

import streamlit as st
import time
import uuid

# Page configuration
st.set_page_config(
    page_title="Notification Demo",
    page_icon="🔔",
    layout="wide"
)

# Custom CSS (sama seperti di streamlit_app.py)
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

def show_toast_notification(message: str, notification_type: str = "success"):
    """Show notification using Streamlit's toast feature"""
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
        if notification_type == "success":
            st.success(f"✅ {message}")
        elif notification_type == "error":
            st.error(f"❌ {message}")
        elif notification_type == "warning":
            st.warning(f"⚠️ {message}")
        elif notification_type == "info":
            st.info(f"ℹ️ {message}")

def main():
    st.title("🔔 Notification System Demo")
    st.markdown("Demo sistem notifikasi menggunakan Streamlit Toast (auto-hide)")

    st.markdown("---")

    # Demo controls
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Test Notifications")

        # Success notification
        if st.button("✅ Show Success", type="primary"):
            show_toast_notification("Operation completed successfully!", "success")

        # Error notification
        if st.button("❌ Show Error"):
            show_toast_notification("Something went wrong! Please try again.", "error")

        # Warning notification
        if st.button("⚠️ Show Warning"):
            show_toast_notification("This action requires confirmation.", "warning")

        # Info notification
        if st.button("ℹ️ Show Info"):
            show_toast_notification("Here's some useful information for you.", "info")

    with col2:
        st.markdown("### ⚙️ Custom Notification")

        # Custom notification
        custom_message = st.text_input("Custom Message", "Your custom notification message")
        custom_type = st.selectbox("Type", ["success", "error", "warning", "info"])

        if st.button("🚀 Send Custom Notification"):
            show_toast_notification(custom_message, custom_type)

    st.markdown("---")

    # Multiple notifications test
    st.markdown("### 🔄 Multiple Notifications Test")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Send Multiple Notifications"):
            show_toast_notification("First notification", "info")
            time.sleep(0.5)
            show_toast_notification("Second notification", "success")
            time.sleep(0.5)
            show_toast_notification("Third notification", "warning")

    with col2:
        if st.button("⚡ Rapid Fire Notifications"):
            for i in range(5):
                show_toast_notification(f"Notification #{i+1}", "info")
                time.sleep(0.2)

    st.markdown("---")

    # Instructions
    st.markdown("### 📖 How Toast Notifications Work")
    st.markdown("""
    **Streamlit Toast Features:**
    1. **Auto-hide**: Notifikasi hilang otomatis setelah beberapa detik
    2. **Non-blocking**: Tidak mengganggu interaksi dengan aplikasi
    3. **Stackable**: Dapat menampilkan beberapa notifikasi sekaligus
    4. **Responsive**: Menyesuaikan dengan ukuran layar
    5. **Built-in**: Menggunakan fitur bawaan Streamlit (v1.27+)

    **Keunggulan:**
    - ✅ Tidak memerlukan JavaScript custom
    - ✅ Konsisten dengan design system Streamlit
    - ✅ Auto-hide tanpa konfigurasi tambahan
    - ✅ Mudah digunakan dan maintain
    """)

    # Version info
    st.markdown("### 🔧 Technical Info")
    st.markdown(f"**Streamlit Version:** {st.__version__}")

    # Check if toast is available
    if hasattr(st, 'toast'):
        st.success("✅ Toast notifications are available!")
    else:
        st.warning("⚠️ Toast notifications not available. Using fallback notifications.")

    # Show example code
    with st.expander("� Example Code"):
        st.code("""
# Basic usage
st.toast("Success message", icon="✅")
st.toast("Error message", icon="❌")
st.toast("Warning message", icon="⚠️")
st.toast("Info message", icon="ℹ️")

# In your application
def show_notification(message, type="success"):
    if type == "success":
        st.toast(f"✅ {message}", icon="✅")
    elif type == "error":
        st.toast(f"❌ {message}", icon="❌")
    # ... etc
        """, language="python")

if __name__ == "__main__":
    main()
